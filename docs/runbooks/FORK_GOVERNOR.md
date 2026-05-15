# Fork Governor Runbook

`bmo-stack` hosts the central fork governor.

## What it does

On a schedule or manual dispatch, the governor will:

1. enumerate the authenticated owner's fork repos
2. install or update `.github/workflows/sync-fork-upstream.yml` inside each fork
3. regenerate `DONORS.yaml` from the live fork inventory
4. open or update a PR against the default branch when `DONORS.yaml` changes

## Why this exists

This keeps fork repos fresh from upstream without sending fork-local work back to the original repo. It also makes `DONORS.yaml` a live inventory instead of a stale hand-edited file.

## Required secret

Add this repository secret to `bmo-stack`:

- `FORK_GOVERNOR_TOKEN`

Recommended token capabilities:

- contents: write
- pull requests: write
- workflows: write
- metadata: read

The token must be able to access the owner's fork repos that should receive the sync workflow.

## Workflow files

- `.github/workflows/fork-governor.yml`
- `scripts/fork-governor.mjs`
- `scripts/fork-governor-pr.sh`

## Generated inventory

- `DONORS.yaml`

## Operational notes

- fork repos may still require manual attention if upstream sync hits conflicts
- repo-level locks or write restrictions will be surfaced in `DONORS.yaml`
- canonical repos remain PR-driven; the governor opens or updates a PR for donor inventory refreshes instead of pushing directly to the default branch
