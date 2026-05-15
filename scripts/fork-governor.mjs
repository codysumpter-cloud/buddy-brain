#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises';

const owner = process.env.GITHUB_OWNER || process.env.GITHUB_REPOSITORY_OWNER || 'codysumpter-cloud';
const donorsPath = process.env.DONORS_PATH || 'DONORS.yaml';
const token = process.env.FORK_GOVERNOR_TOKEN || process.env.GH_TOKEN || process.env.GITHUB_TOKEN;
const apiBase = 'https://api.github.com';
const syncWorkflowPath = '.github/workflows/sync-fork-upstream.yml';

const syncWorkflowContent = [
  'name: Sync fork from upstream',
  '',
  'on:',
  '  schedule:',
  "    - cron: '17 13 * * *'",
  '  workflow_dispatch:',
  '',
  'permissions:',
  '  contents: write',
  '',
  'concurrency:',
  '  group: sync-fork-upstream',
  '  cancel-in-progress: false',
  '',
  'jobs:',
  '  sync:',
  '    runs-on: ubuntu-latest',
  '    steps:',
  '      - name: Sync default branch from upstream',
  '        env:',
  '          GH_TOKEN: ${{ github.token }}',
  '          REPO: ${{ github.repository }}',
  '          BRANCH: ${{ github.event.repository.default_branch }}',
  '        run: |',
  '          set -euo pipefail',
  '          payload=$(printf \'{"branch":"%s"}\' "$BRANCH")',
  '          status=$(curl -sS -o response.json -w "%{http_code}" \\',
  '            -X POST \\',
  '            -H "Accept: application/vnd.github+json" \\',
  '            -H "Authorization: Bearer ${GH_TOKEN}" \\',
  '            -H "X-GitHub-Api-Version: 2022-11-28" \\',
  '            "https://api.github.com/repos/${REPO}/merge-upstream" \\',
  '            -d "$payload")',
  '          cat response.json',
  '          if [ "$status" = "200" ]; then',
  '            echo "Upstream sync complete."',
  '          elif [ "$status" = "409" ] || [ "$status" = "422" ]; then',
  '            echo "Upstream sync needs manual resolution (status $status)." >&2',
  '            exit 1',
  '          else',
  '            echo "Unexpected response: $status" >&2',
  '            exit 1',
  '          fi',
  ''
].join('\n');

function encodePath(path) {
  return path.split('/').map(encodeURIComponent).join('/');
}

async function github(path, options = {}) {
  const headers = {
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    ...(options.headers || {})
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${apiBase}${path}`, { ...options, headers });
  if (response.status === 204) return null;
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const error = new Error(data?.message || `GitHub API request failed: ${response.status}`);
    error.status = response.status;
    error.data = data;
    throw error;
  }
  return data;
}

async function listOwnedRepos() {
  const repos = [];
  let page = 1;
  while (true) {
    const batch = await github(`/user/repos?visibility=all&affiliation=owner&per_page=100&page=${page}&sort=full_name`);
    if (!Array.isArray(batch) || batch.length === 0) break;
    repos.push(...batch);
    if (batch.length < 100) break;
    page += 1;
  }
  return repos.filter((repo) => repo.owner?.login === owner);
}

async function getContents(repoFullName, path, ref) {
  try {
    return await github(`/repos/${repoFullName}/contents/${encodePath(path)}?ref=${encodeURIComponent(ref)}`);
  } catch (error) {
    if (error.status === 404) return null;
    throw error;
  }
}

async function upsertFile(repo, path, content, message) {
  const existing = await getContents(repo.full_name, path, repo.default_branch);
  if (existing?.type === 'file') {
    const current = Buffer.from(existing.content, 'base64').toString('utf8');
    if (current === content) return 'unchanged';
    await github(`/repos/${repo.full_name}/contents/${encodePath(path)}`, {
      method: 'PUT',
      body: JSON.stringify({
        message,
        content: Buffer.from(content, 'utf8').toString('base64'),
        sha: existing.sha,
        branch: repo.default_branch
      })
    });
    return 'updated';
  }
  await github(`/repos/${repo.full_name}/contents/${encodePath(path)}`, {
    method: 'PUT',
    body: JSON.stringify({
      message,
      content: Buffer.from(content, 'utf8').toString('base64'),
      branch: repo.default_branch
    })
  });
  return 'created';
}

function yamlString(value) {
  if (value === null || value === undefined) return 'null';
  return `'${String(value).replace(/'/g, "''")}'`;
}

function renderDonorsYaml(forks) {
  const lines = [];
  lines.push('version: 1');
  lines.push(`owner: ${yamlString(owner)}`);
  lines.push(`generated_by: ${yamlString('scripts/fork-governor.mjs')}`);
  lines.push(`generated_at: ${yamlString(new Date().toISOString())}`);
  lines.push(`total_forks: ${forks.length}`);
  lines.push('forks:');
  for (const fork of forks) {
    lines.push(`  - name: ${yamlString(fork.name)}`);
    lines.push(`    full_name: ${yamlString(fork.full_name)}`);
    lines.push(`    visibility: ${yamlString(fork.visibility)}`);
    lines.push(`    default_branch: ${yamlString(fork.default_branch)}`);
    lines.push(`    html_url: ${yamlString(fork.html_url)}`);
    lines.push(`    upstream_full_name: ${yamlString(fork.upstream_full_name)}`);
    lines.push(`    archived: ${fork.archived ? 'true' : 'false'}`);
    lines.push(`    sync_workflow_status: ${yamlString(fork.sync_workflow_status)}`);
    lines.push(`    sync_workflow_path: ${yamlString(syncWorkflowPath)}`);
  }
  return `${lines.join('\n')}\n`;
}

function normalizeGeneratedAt(content) {
  return content.replace(/^generated_at: .+$/m, "generated_at: '<ignored>'");
}

async function readExistingDonors() {
  try {
    return await readFile(donorsPath, 'utf8');
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
}

async function writeDonorsIfMateriallyChanged(nextDonors) {
  const existingDonors = await readExistingDonors();
  if (
    existingDonors !== null &&
    normalizeGeneratedAt(existingDonors) === normalizeGeneratedAt(nextDonors)
  ) {
    console.log('No material DONORS.yaml changes; preserving existing generated_at timestamp.');
    return false;
  }

  await writeFile(donorsPath, nextDonors, 'utf8');
  return true;
}

async function main() {
  if (!token) {
    throw new Error('Missing FORK_GOVERNOR_TOKEN (or GH_TOKEN / GITHUB_TOKEN).');
  }

  const repos = await listOwnedRepos();
  const forks = repos
    .filter((repo) => repo.fork)
    .sort((a, b) => a.full_name.localeCompare(b.full_name));

  const materialized = [];
  const operations = [];

  for (const repo of forks) {
    let syncStatus = 'skipped';
    let syncOperation = 'skipped';

    if (repo.archived) {
      syncStatus = 'skipped_archived';
      syncOperation = 'skipped_archived';
    } else {
      try {
        syncOperation = await upsertFile(repo, syncWorkflowPath, syncWorkflowContent, 'Add scheduled upstream fork sync workflow');
        syncStatus = 'managed';
      } catch (error) {
        if (error.status === 403 && /locked/i.test(error.data?.message || '')) {
          syncStatus = 'locked';
          syncOperation = 'locked';
        } else if (error.status === 409 || error.status === 422) {
          syncStatus = 'manual_resolution_required';
          syncOperation = 'manual_resolution_required';
        } else {
          syncStatus = `error:${error.status || 'unknown'}`;
          syncOperation = syncStatus;
        }
      }
    }

    operations.push(syncOperation);
    materialized.push({
      name: repo.name,
      full_name: repo.full_name,
      visibility: repo.private ? 'private' : 'public',
      default_branch: repo.default_branch,
      html_url: repo.html_url,
      upstream_full_name: repo.parent?.full_name || null,
      archived: Boolean(repo.archived),
      sync_workflow_status: syncStatus
    });
  }

  const donorsChanged = await writeDonorsIfMateriallyChanged(renderDonorsYaml(materialized));

  const created = operations.filter((operation) => operation === 'created').length;
  const updated = operations.filter((operation) => operation === 'updated').length;
  const unchanged = operations.filter((operation) => operation === 'unchanged').length;
  console.log(`Fork governor complete: ${materialized.length} forks scanned, ${created} created, ${updated} updated, ${unchanged} unchanged.`);
  console.log(`DONORS.yaml ${donorsChanged ? 'updated' : 'unchanged'}.`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
