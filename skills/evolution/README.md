# evolution

## Purpose

Document the evolution workflow used when the Buddy audits its own operating behavior, proposes a bounded improvement, and records the resulting change as an explicit, reviewable mutation instead of an implicit prompt drift.

## When to use it

Use this skill when:

- repeated operator mistakes suggest a stable invariant should be added
- an autonomy or kernel update needs an explicit audit path
- an agent proposes a self-improvement loop and you need a documented procedure

## Workflow

1. audit the repeated failure or friction point
2. identify the smallest useful invariant or kernel mutation
3. write the proposed change in a reviewable artifact
4. validate the updated operating rule before claiming improvement
5. record the result and any rollback path

## Validation

- the proposed mutation is explicit and reviewable
- the new rule is machine-checkable or operator-checkable where possible
- no hidden autonomy change is claimed without a committed artifact or PR

## Related files

- `skills/index.json`
- `skills/README.md`
- `docs/BUDDY_PRODUCT_SYSTEM_EXECUTION_PLAN.md`
