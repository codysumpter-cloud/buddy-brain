# Tech spec

## Problem

`bmo-stack` needs an Oz-inspired planning gate that supports durable product and tech specs without requiring the full Oz cloud workflow stack. The existing `task-readiness` validator only checks PR body plans or generic referenced plans; it does not understand spec-backed PR contracts.

## Relevant code

- `scripts/check_task_readiness.py`
- `.github/workflows/task-readiness.yml`
- `specs/README.md`
- `specs/templates/product.md`
- `specs/templates/tech.md`
- `.agents/skills/create-product-spec/SKILL.md`
- `.agents/skills/create-tech-spec/SKILL.md`
- `.agents/skills/check-impl-against-spec/SKILL.md`

## Current state

`task-readiness` reads the PR body, requires a `## Task contract` block, extracts `Plan:`, and validates that the referenced content includes the standard PR-body sections: `## Problem`, `## Smallest useful wedge`, `## Verification plan`, and `## Rollback plan`.

There is no `specs/` planning convention and no local `.agents/skills` guidance for creating or reviewing specs.

## Proposed changes

Add spec documentation and templates:

- `specs/README.md`
- `specs/templates/product.md`
- `specs/templates/tech.md`

Add local BMO agent skill docs:

- `.agents/skills/create-product-spec/SKILL.md`
- `.agents/skills/create-tech-spec/SKILL.md`
- `.agents/skills/check-impl-against-spec/SKILL.md`

Update `scripts/check_task_readiness.py` so:

- `Plan: PR_BODY` remains valid for small changes.
- non-spec file references still validate the existing required plan sections.
- spec-backed plans must match `specs/GH<number>/tech.md`.
- spec-backed plans must not reference absolute paths or parent traversal.
- `tech.md` must include the required tech-spec headings.
- sibling `product.md` must exist and include the required product-spec headings.

## End-to-end flow

1. A complex PR creates or updates `specs/GH<number>/product.md` and `specs/GH<number>/tech.md`.
2. The PR body includes:

   ```md
   ## Task contract
   Plan: specs/GH<number>/tech.md
   - Verification: yes
   - Rollback: yes
   ```

3. `task-readiness` runs on PR open/edit/sync/reopen.
4. The validator reads the referenced `tech.md` and sibling `product.md`.
5. The check passes only when both spec files contain the required sections and the PR body declares verification and rollback.

## Risks and mitigations

- Risk: The new gate could make simple PRs too heavy.
  - Mitigation: Keep `Plan: PR_BODY` valid.
- Risk: A referenced plan could escape the repository.
  - Mitigation: Reject absolute paths and `..` traversal.
- Risk: Spec files could become busywork.
  - Mitigation: Require only headings and concise content in v1; avoid mandatory specs for all PRs.
- Risk: Full Oz workflows could fail without secrets if copied prematurely.
  - Mitigation: Add local docs and validation only; defer cloud workflows.

## Testing and validation

- Open PR #305 with a temporary `Plan: PR_BODY` contract.
- Add `specs/GH305/product.md` and `specs/GH305/tech.md`.
- Update PR #305 to reference `Plan: specs/GH305/tech.md`.
- Confirm `task-readiness` passes with the spec-backed plan.
- Confirm normal repository checks pass, including `ci` and `lint`.

## Rollback plan

Revert PR #305. That removes the `specs/` directory additions, local `.agents/skills` docs, and the readiness checker changes, returning the repository to PR-body-only readiness validation.

## Follow-ups / open technical questions

- Add optional issue triage and spec creation workflows after required secrets and repository settings are available.
- Consider adding unit tests for `scripts/check_task_readiness.py` once the validation matrix grows beyond this v1 gate.
