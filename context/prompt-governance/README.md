# Prompt Governance

Status: active
Owner: Buddy Brain / Prismtek
Last verified: 2026-06-12

## What was added

Buddy Brain now defines the default Buddy + Lil' Buddy governance path for future prompts and tasks:

```text
Human -> Buddy Orchestrator -> Lil' Buddy Worker(s) -> Buddy Review -> Human-facing response
```

Key files:

- `context/council/BUDDY_LIL_BUDDY_ORCHESTRATION.md` - orchestration contract, review loop, and escalation rules
- `context/prompt-governance/BUDDY_LIL_BUDDY_PROMPT_STANDARD.md` - reusable system prompt and default prompt rule
- `config/runtime/buddy-lil-buddy-contract.json` - machine-readable runtime contract
- `config/runtime/delegation-policy.json` - existing delegation policy extended to point at the new contract

## Future prompt rule

Always use Buddy + Lil' Buddy unless explicitly disabled by the human for the current task.

Buddy owns intent, planning, delegation, review, safety gates, and the final human-facing response. Lil' Buddy executes scoped tasks and returns structured results.

## Runtime demo

The local no-secrets demo is in `buddy-agent`:

```bash
buddy-demo "Draft a safe project note"
```
