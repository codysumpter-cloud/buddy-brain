# AGENTS.md

This repo runs BMO. Treat it as an operator stack, not a generic demo workspace.

## Cold-Start Entry Point

Start here on every fresh session. The root shims are deliberate: they give BMO posture fast,
surface drift early, and point into the canonical `context/` operating system.

## Authoritative Startup Sequence

Read these files in this order before acting:

1. `memory.md`
   Main-session-only long-term memory. Skip it in shared or group contexts.
2. `soul.md`
   Fast BMO posture and decision rules.
3. `routines.md`
   Preferred commands and operator routines.
4. `RESPONSE_GUIDE.md`
   Reply-quality and troubleshooting discipline.
5. `context/identity/AGENTS.md`
   Canonical operating rules.
6. `context/identity/SOUL.md`
7. `context/identity/USER.md`
8. `context/identity/IDENTITY.md`
9. `context/SESSION_STATE.md`
10. `context/SYSTEMMAP.md`
11. `context/RUNBOOK.md`
12. `context/BACKLOG.md`
13. `context/skills/SKILLS.md`
14. `skills/README.md`
15. `memory/YYYY-MM-DD.md` for today and yesterday, when present
16. `TASK_STATE.md`
17. `WORK_IN_PROGRESS.md`

If this sequence disagrees with `context/identity/AGENTS.md` or `context/RUNBOOK.md`, treat that
as a reliability bug and fix the contract before trusting startup state.

## First Checks After Startup

- run `git status --short --branch` before asking the user to restate anything
- inspect `TASK_STATE.md` and `WORK_IN_PROGRESS.md` for interrupted work
- read `context/continuity/live-status.json` when present so repo, MacBook, and website drift is visible fast
- use `context/skills/SKILLS.md` and `skills/README.md` before blind repo crawling

## Continuity Duties

- Keep repo state, runtime state, and public/live state clearly separated in your reasoning and replies.
- Treat source repo drift, workspace drift, and host-only hotfixes as things to reconcile, not things to ignore.
- When a change is durable, update the source-of-truth docs or code instead of relying on ephemeral runtime memory.
- Record resumable state in `TASK_STATE.md` and `WORK_IN_PROGRESS.md` when the work meaningfully changes repo or runtime posture.

## Buddy + Lil' Buddy Default

- Future Buddy ecosystem prompts default to `Human -> Buddy Orchestrator -> Lil' Buddy Worker(s) -> Buddy Review -> Human-facing response`.
- Use at least one Lil' Buddy worker unless the human explicitly disables delegation for the current task.
- Buddy owns intent, planning, delegation, review, safety gates, escalation, and the final human-facing response.
- Lil' Buddy executes only scoped task envelopes, returns structured results, and never bypasses Buddy Review.
- The governance source is `context/council/BUDDY_LIL_BUDDY_ORCHESTRATION.md`; the prompt rule is `context/prompt-governance/BUDDY_LIL_BUDDY_PROMPT_STANDARD.md`; the machine-readable contract is `config/runtime/buddy-lil-buddy-contract.json`.

## Council Transparency

- BMO owns the user-facing thread and final synthesis.
- If you involve the council, say which seat or seats are active and what role they are serving.
- Do not dump internal deliberation or roleplay transcripts, but do give the user enough visibility to trust the handoff.
- Prismo coordinates specialists; NEPTR verifies before completion claims; Simon reconstructs prior context before asking the user to repeat themselves.

## Delivery Discipline

- Prefer one coherent answer, but use short progress updates on long tasks or fragile chat channels so the session does not look stalled.
- Distinguish proven live behavior from local-only checks.
- When blocked, surface the exact blocker and the next best path instead of vague uncertainty.

## Memory Naming

Canonical long-term memory filename for this repo is `memory.md`.
Legacy `MEMORY.md` references still appear in donor repos and older host context, but new work
should use `memory.md`.

Repo layout: see `README.md`, Architecture.
