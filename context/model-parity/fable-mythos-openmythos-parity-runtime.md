# Fable/Mythos Open Architecture Parity Runtime

Status: source-backed governance contract.  
Created: 2026-06-15.

## Rule

OpenMythos and OpenFable may be used as architecture references, but they are not drop-in Claude Fable 5 or Claude Mythos 5 equivalents. Buddy may only claim parity for a feature after the owning repo has code, validation, and a source-linked receipt.

## Sources

- Official Claude feature baseline: `https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5`
- OpenMythos: `https://github.com/kyegomez/OpenMythos`
- OpenFable: `https://github.com/lovestaco/OpenFable`
- Third-party desktop client: `https://github.com/anthropic-fable/claude-fable-5`

## Status vocabulary

- `supported`: proven by code, tests, or runtime receipts.
- `partial`: some pieces exist, but production/runtime coverage is incomplete.
- `claimed-not-verified`: docs or configs claim it, but Buddy has not proved it.
- `missing`: no implementation found.
- `external-runtime-required`: requires a hosted provider or separate runtime.

## Current ledger

| Capability | Open source status | Buddy ruling |
|---|---|---|
| Trained frontier weights | Missing | Hosted-provider boundary only. |
| Recurrent-depth architecture | Partial | Research inspiration allowed. |
| Large context / large output | Claimed in variants, not locally proven | Needs token accounting and stress receipts. |
| Adaptive compute | Partial through loop depth / halting ideas | Map to effort and task-budget policy. |
| Memory, tools, code execution, compaction, vision | Mostly missing in architecture repos | Implement through guarded Buddy adapters. |
| Provider safety and fallback behavior | Vendor-specific | Normalize in provider adapters; do not fake claims. |

## Repo ownership

- `buddy-brain`: policy, claim taxonomy, council review, and coordination.
- `buddy-agent`: typed runtime parity registry and provider/adapter work.
- `knowledge-vault`: source pack, decisions, and graph events.
- `omni-buddy`: local device voice/vision parity receipts.
- `prismtek-apps`: user-facing model controls and Buddy chat UX.
- `buddy-universal-agent-profile`: portable no-fake-parity rule.

## Validation gate

Before marking a feature `supported`, record the repo path, validation command, source, receipt, provider boundary, and user-facing limitation.
