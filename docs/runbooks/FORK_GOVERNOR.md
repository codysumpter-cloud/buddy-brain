# Fork Governor Runbook

`buddy-brain` hosts the central fork governor.

## What it does

When manually dispatched or when the governor policy changes, the governor will:

1. enumerate the authenticated owner's fork repositories
2. refresh `.github/workflows/sync-fork-upstream.yml` inside each fork
3. enforce a manual-only, conflict-safe sync policy
4. regenerate `DONORS.yaml` from the live fork inventory
5. open or update a PR against the default branch when `DONORS.yaml` changes

## Why this exists

The governor keeps fork management centralized without launching hosted runners across the entire fork fleet every day. Forks remain easy to sync on demand, while diverged forks no longer fail repeatedly just because upstream has merge conflicts.

## Fork sync policy

Each managed fork receives `.github/workflows/sync-fork-upstream.yml` with these rules:

- `workflow_dispatch` only; there is no scheduled runner usage
- one sync may run at a time and newer requests cancel older ones
- jobs time out after two minutes
- GitHub responses `409` and `422` are recorded as notices requiring manual resolution, not failed runs
- unexpected API responses still fail so genuine authentication or platform problems remain visible

## Required secret

Add this repository secret to `buddy-brain`:

- `FORK_GOVERNOR_TOKEN`

Recommended token capabilities:

- contents: write
- pull requests: write
- workflows: write
- metadata: read

The token must be able to access the owner's fork repositories that should receive the sync workflow.

## Workflow files

- `.github/workflows/fork-governor.yml`
- `scripts/fork-governor.mjs`
- `scripts/fork-sync-policy.mjs`
- `scripts/fork-governor-pr.sh`

## Generated inventory

- `DONORS.yaml`

## Operations

Run **Govern forks and donors** manually after adding or removing forks, changing sync policy, or rotating the governor token. A policy-file change on `master` also triggers one reconciliation run automatically.

## Operational notes

- fork repositories may still require manual attention when upstream and local history conflict
- repository locks or write restrictions are surfaced by the governor
- canonical repositories remain PR-driven
- do not restore a fleet-wide schedule unless the expected runner usage and notification volume have been reviewed first
