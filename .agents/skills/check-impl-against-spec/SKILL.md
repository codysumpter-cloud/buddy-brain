---
name: check-impl-against-spec
description: Compare an implementation PR against its referenced BMO tech spec and report gaps, risks, and verification status.
---

# check-impl-against-spec

Review an implementation against its referenced BMO tech spec.

## Purpose

This skill keeps implementation aligned with planned intent. It checks whether the PR actually satisfies the spec without silently expanding scope or skipping verification.

## Inputs

Use the PR body, referenced `Plan:` path, diff, related product and tech specs, workflow results, and reviewer comments.

## Workflow

1. Read the PR body and extract the `Plan:` reference.
2. Read the referenced tech spec.
3. If a sibling `product.md` exists, read it for user-facing intent.
4. Inspect the PR diff.
5. Compare the implementation against:
   - proposed changes
   - scope boundaries
   - risks and mitigations
   - testing and validation
   - rollback plan
6. Report gaps as concrete review findings.
7. Do not approve changes that satisfy tests while violating scope, user intent, safety, or rollback expectations.

## Output expectations

Return a concise review summary with:

- aligned items
- missing or risky items
- validation status
- recommended next action: approve, request changes, or ask for clarification
