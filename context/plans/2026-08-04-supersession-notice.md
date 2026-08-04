# Mark Buddy Brain superseded by prismtek-apps

## Problem

Buddy Brain has been consolidated into `codysumpter-cloud/prismtek-apps`, but
this repository's README still presents it as an active standalone project.
Anyone landing here, human or agent, would treat it as the source of truth and
open new work against a repository that is about to become read-only.

## Smallest useful wedge

Prepend a supersession notice to `README.md`, plus this plan. Documentation
only: no code, workflow, schema, package, or release behaviour changes.

The notice records where the code went, links the migration record and the
consolidation tracker, and names the `pre-archive-final` tag that will mark the
exact final state of `master`.

## Verification plan

Destination parity was already established and merged as prismtek-apps#363:
57 shell scripts parse, all five node validators pass, 7/7 Makefile targets and
5/5 context bootstrap files are present, and 84 tests pass with 1 pre-existing
failure, which is exact parity with this repository's own baseline. Governance
behaviour was proven from `packages/buddy-governance`: newly discovered models
quarantine and do not route, a direct quarantined to approved transition is
refused, and task economics groups by harness fingerprint.

The three `prismtek-buddy-life-*-score` workflows were the only consumers that
checked this repository out at build time. They were repointed at a pinned
prismtek-apps revision in prismtek-apps#368 and all three ran green afterwards.

This change touches only documentation, so this repository's existing checks are
the verification for it.

## Rollback plan

Revert the commit. It touches `README.md` and this plan file and nothing else.
