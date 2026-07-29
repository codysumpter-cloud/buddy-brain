#!/usr/bin/env node

const owner = process.env.GITHUB_OWNER || process.env.GITHUB_REPOSITORY_OWNER || 'codysumpter-cloud';
const token = process.env.FORK_GOVERNOR_TOKEN || process.env.GH_TOKEN || process.env.GITHUB_TOKEN;
const apiBase = 'https://api.github.com';
const workflowPath = '.github/workflows/sync-fork-upstream.yml';

const workflowContent = [
  'name: Sync fork from upstream',
  '',
  'on:',
  '  workflow_dispatch:',
  '',
  'permissions:',
  '  contents: write',
  '',
  'concurrency:',
  '  group: sync-fork-upstream',
  '  cancel-in-progress: true',
  '',
  'jobs:',
  '  sync:',
  '    runs-on: ubuntu-latest',
  '    timeout-minutes: 2',
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
  '            echo "::notice title=Fork sync needs manual resolution::GitHub returned status $status for $REPO. No retry was scheduled."',
  '            exit 0',
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
  return repos.filter((repo) => repo.owner?.login === owner && repo.fork && !repo.archived);
}

async function getContents(repoFullName, path, ref) {
  try {
    return await github(`/repos/${repoFullName}/contents/${encodePath(path)}?ref=${encodeURIComponent(ref)}`);
  } catch (error) {
    if (error.status === 404) return null;
    throw error;
  }
}

async function upsertWorkflow(repo) {
  const existing = await getContents(repo.full_name, workflowPath, repo.default_branch);
  if (existing?.type === 'file') {
    const current = Buffer.from(existing.content, 'base64').toString('utf8');
    if (current === workflowContent) return 'unchanged';
    await github(`/repos/${repo.full_name}/contents/${encodePath(workflowPath)}`, {
      method: 'PUT',
      body: JSON.stringify({
        message: 'chore(actions): make upstream sync manual and conflict-safe',
        content: Buffer.from(workflowContent, 'utf8').toString('base64'),
        sha: existing.sha,
        branch: repo.default_branch
      })
    });
    return 'updated';
  }

  await github(`/repos/${repo.full_name}/contents/${encodePath(workflowPath)}`, {
    method: 'PUT',
    body: JSON.stringify({
      message: 'chore(actions): add manual conflict-safe upstream sync',
      content: Buffer.from(workflowContent, 'utf8').toString('base64'),
      branch: repo.default_branch
    })
  });
  return 'created';
}

async function main() {
  if (!token) throw new Error('Missing FORK_GOVERNOR_TOKEN (or GH_TOKEN / GITHUB_TOKEN).');

  const repos = await listOwnedRepos();
  const results = [];
  for (const repo of repos) {
    try {
      results.push({ repo: repo.full_name, result: await upsertWorkflow(repo) });
    } catch (error) {
      results.push({ repo: repo.full_name, result: `error:${error.status || 'unknown'}` });
    }
  }

  for (const row of results) console.log(`${row.result}\t${row.repo}`);
  const failed = results.filter((row) => row.result.startsWith('error:'));
  console.log(`Fork sync policy complete: ${results.length} forks scanned, ${failed.length} errors.`);
  if (failed.length > 0) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
