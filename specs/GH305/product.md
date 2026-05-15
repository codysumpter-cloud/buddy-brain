# Product spec

## Summary

Add a lightweight BMO spec gate inspired by Oz-style OSS workflows. The change gives larger `bmo-stack` work a durable planning path before implementation while preserving the existing fast path for small PRs.

## Problem

`bmo-stack` currently validates PR readiness through the PR body, which works for small changes but does not create a durable artifact for larger changes. Complex work needs a clearer product-to-tech handoff so intent, scope, validation, and rollback can be reviewed before code changes accumulate.

## Goals

- Add a predictable place for product and tech specs under `specs/GH<number>/`.
- Provide templates that make spec creation fast and consistent.
- Add local BMO agent skill docs for product specs, tech specs, and implementation-vs-spec review.
- Allow PRs to reference `specs/GH<number>/tech.md` in the task contract.
- Keep `Plan: PR_BODY` valid for small changes.

## Non-goals / scope boundaries

- Do not install the full Oz cloud workflow stack in this wedge.
- Do not require Warp/Oz secrets, API keys, or GitHub App credentials.
- Do not mutate issues, labels, assignees, or reviewer state.
- Do not require every PR to create specs.

## User experience / behavior requirements

For small PRs, authors can keep using `Plan: PR_BODY` with the existing task contract sections.

For larger PRs, authors can create:

```text
specs/GH<number>/product.md
specs/GH<number>/tech.md
```

Then the PR body can reference:

```md
## Task contract
Plan: specs/GH<number>/tech.md
- Verification: yes
- Rollback: yes
```

The readiness check should fail if the referenced spec file is missing, points outside the repository, uses the wrong spec path shape, omits required tech sections, or lacks a sibling product spec with required product sections.

## Success criteria

- `specs/README.md` explains when and how to use BMO specs.
- Product and tech templates exist and contain the required headings.
- Local `.agents/skills` docs exist for product planning, tech planning, and spec-backed implementation review.
- `scripts/check_task_readiness.py` accepts `Plan: PR_BODY` and validates spec-backed plans.
- PR #305 dogfoods the new flow by referencing `specs/GH305/tech.md`.

## Validation

Validate through repository pull request checks, especially `task-readiness`, `ci`, and `lint`. The `task-readiness` check must pass when PR #305 references this spec-backed plan.

## Open product questions

None for v1. Full Oz issue triage, PR review, and cloud execution can be evaluated in a later PR once secrets and repo settings are ready.
