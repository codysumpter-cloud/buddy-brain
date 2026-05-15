# BMO specs

BMO specs are lightweight planning artifacts for work that is too complex to trust to a PR body alone.

Use them when a change is expected to touch multiple files, alter runtime behavior, introduce automation, or change user-facing flows.

## Layout

```text
specs/GH<number>/product.md
specs/GH<number>/tech.md
```

- `product.md` captures the user-facing intent: what problem is being solved, who it helps, what is in scope, what is out of scope, and how success is recognized.
- `tech.md` translates that intent into a grounded implementation plan: current code paths, proposed changes, risks, validation, and rollback.

## PR contract

A PR can use a spec-backed task contract by referencing its tech spec:

```md
## Task contract
Plan: specs/GH123/tech.md
- Verification: yes
- Rollback: yes
```

`task-readiness` validates the referenced plan exists and contains the required sections. If a PR is small, `Plan: PR_BODY` is still valid.

## Templates

Start from:

- `specs/templates/product.md`
- `specs/templates/tech.md`

Keep specs concise, specific, and grounded in the repository as it exists today.
