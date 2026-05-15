# Contributing to BMO Stack

Thanks for contributing to `bmo-stack`.

## Scope

This repository owns operator workflows, contracts, runbooks, donor inventory, and integration glue. Product UI belongs in `prismtek-apps`. Device/runtime behavior belongs in `omni-bmo`.

## Working rules

1. Open a branch first.
2. Open a draft PR early.
3. Keep PRs small and scoped.
4. Do not merge until all required GitHub checks are green.
5. Do not let the lead branch go red.
6. Prefer machine-checkable docs, contracts, and scripts over vague promises.

## Pull request expectations

Every PR should include:

- a clear summary
- a task contract block in the PR body
- verification notes
- rollback notes
- repo-boundary awareness

## Local validation

Before requesting review, run the validation path relevant to your change.

Common commands:

```bash
make doctor
make runtime-doctor
make workspace-sync
make worker-status
```

If you touch docs, manifests, or GitHub automation, also verify the changed files directly.

## Branch and merge policy

- never push directly to `master`
- use PRs for every meaningful change
- wait for required checks
- use squash merge unless there is a strong reason not to

## Security and secrets

- never commit tokens, secrets, or local `.env` data
- use placeholders in examples
- report sensitive issues privately as described in `SECURITY.md`

## Repo boundaries

When in doubt:

- `bmo-stack` = operator contracts, policy, runbooks, automation, donor/governor docs
- `prismtek-apps` = shipped Buddy product UX
- `omni-bmo` = runtime/device execution and pairing state
