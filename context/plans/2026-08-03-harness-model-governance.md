## Problem

Buddy Brain currently aggregates task economics primarily by provider and model. That can silently combine runs with different BUAP artifacts, runtime adapters, memory strategies, context handling, reasoning retention, effort, and tool policy. A model can appear newly available through a provider before Buddy has benchmarked, security-reviewed, supervised, or approved it for any task class.

This makes routing evidence less trustworthy and creates a policy gap between provider availability and Buddy approval.

## Smallest useful wedge

Extend the existing task-economics record with a backward-compatible harness identity and group results by a stable harness fingerprint. Keep legacy records readable, but mark their harness evidence incomplete.

Add a separate quarantine-first model lifecycle registry that:

- defaults newly discovered models to `quarantined`;
- enforces evidence-bearing lifecycle transitions;
- requires attributable review for security-reviewed, supervised, and approved states;
- requires explicit task classes before approval;
- requires caller opt-in for supervised routing;
- permits immediate re-quarantine when behavior changes;
- commits no approved provider models in this change.

Do not mix model discovery with automatic routing approval, and do not store prompts, credentials, or private conversation content as lifecycle evidence.

## Verification plan

- Compile the readiness, economics, and model-governance scripts with Python 3.12.
- Run economics regression tests, including separation of identical models under different harness identities.
- Run model-registry tests for quarantine defaults, invalid transition refusal, evidence requirements, reviewer requirements, supervised opt-in, approved task classes, re-quarantine, deterministic persistence, and identity collisions.
- Validate the committed empty registry through the CLI.
- Run the focused Agent readiness metrics workflow.
- Require the repository CI, lint, CodeQL, bootstrap, autonomy, runtime smoke, iOS validation, and task-readiness checks to pass before merge.
- Confirm no provider model becomes approved and no runtime route changes in this PR.

## Rollback plan

- Revert the PR to restore provider/model-only grouping and remove the model registry.
- Existing task-economics producers remain compatible because the new harness identity is optional and legacy records are parsed explicitly.
- The committed registry contains no approved models, so rollback does not revoke an active approved route.
- If a later producer emits malformed harness data, quarantine those records from comparative reports rather than weakening validation.
