# Buddy Product Spine

This is the operating contract that links the existing Buddy systems into one functional product instead of scattered scaffolding.

## Product promise

Buddy / BeMore is one usable product loop:

```text
Human request
  -> Prismtek Apps guarded Agent Browser
  -> Buddy Orchestrator
  -> Lil' Buddy worker delegation
  -> Buddy Agent local runtime / project workspace
  -> .bemore app-visible receipts and artifacts
  -> external adapters only after approval
```

## Repo ownership

| Repo | Owns | Default branch |
| --- | --- | --- |
| `codysumpter-cloud/prismtek-apps` | iOS/macOS product surfaces, guarded Agent Browser, `.bemore` workspace runtime, receipt/artifact rendering, linked-account settings | `main` |
| `codysumpter-cloud/buddy-agent` | local Buddy CLI/runtime, app-chat bridge seam, Buddy Playground project workspace, Game Studio VS Code/Godot/Unity helpers, integration status/contracts | `main` |
| `codysumpter-cloud/buddy-brain` | operator policy, workspace dispatch, browser automation profile, Orchestrator/Worker runbooks, cross-repo ownership boundaries | `master` |

## Existing surfaces to treat as real

Do not describe these as future greenfield work. They already exist as code, skill docs, or runtime contracts.

| Surface | Owner | Status | Role |
| --- | --- | --- | --- |
| Guarded Agent Browser | `prismtek-apps` | implemented app MVP | Human starts missions, Buddy delegates to Lil' Buddy, and risky actions pause for approval. |
| `.bemore` Workspace Runtime | `prismtek-apps` | implemented app-local runtime | Persists app-visible skills, artifacts, receipts, memory, session state, and runtime actions. |
| Buddy Agent Runtime | `buddy-agent` | runnable alpha | Local CLI, chat path, memory path, skills, app-chat seam, integrations, and diagnostics. |
| Buddy Playground | `buddy-agent` | implemented project workspace | Reviewable local files, browser notes, code tasks, art briefs, outbox drafts, and receipts before adapters act. |
| Buddy Game Studio | `buddy-agent` | implemented VS Code cockpit | Game/project workspace setup for Godot/Unity with Buddy task hooks. |
| Workspace Dispatch | `buddy-brain` | documented orchestration contract | Worker task loop, verification rules, retry behavior, and operator ownership boundaries. |
| Browser Automation Policy | `buddy-brain` | documented policy contract | Opt-in, scoped, auditable browser automation separate from default chat execution. |

## End-to-end flow

1. **Human** enters a mission or opens/searches a page in the guarded Agent Browser.
   - Surface: `agent-browser`
   - Risk: `read-only`
   - Output: `BuddyAgentSession` intent, current URL, visible UI context.

2. **Buddy Orchestrator** decomposes the mission into bounded worker steps with exit criteria.
   - Surface: `workspace-dispatch`
   - Risk: `draft-only`
   - Output: worker plan with approval checkpoints.

3. **Lil' Buddy Worker** drafts browser notes, code tasks, art briefs, files, email/message/calendar outbox items, or receipts.
   - Surface: `buddy-playground`
   - Risk: `draft-only`
   - Output: reviewable `.buddy/playground` artifact.

4. **Buddy Runtime** validates local runtime status, integration capability, and app-chat handoff.
   - Surface: `buddy-agent-runtime`
   - Risk: `read-only`
   - Output: CLI/app bridge result and sanitized status.

5. **Prismtek Apps Runtime** promotes approved useful outputs into `.bemore` skills, artifacts, receipts, memory, or session state.
   - Surface: `bemore-workspace-runtime`
   - Risk: `write`
   - Output: app-visible `BeMoreReceipt` and persisted artifact.

6. **External Adapter** performs browser/account/calendar/message/email/repo external actions only after approval.
   - Surface: `browser-policy`
   - Risk: `external-action`
   - Output: secret-free receipt and verification status.

## Approval boundary

Human approval is required for these risk classes:

- `write`
- `external-action`
- `destructive`
- `credential`
- `money`
- `repo-mutation`

Buddy Brain should treat missing or unknown risk classification as blocked until a policy owner classifies it.

## Workspace split

| Workspace | Owner | Purpose |
| --- | --- | --- |
| `.bemore/` | `prismtek-apps` | Canonical app-visible runtime artifacts, skills, receipts, memory, session state, action logs. |
| `.buddy/playground/` | `buddy-agent` | Local/project drafts, browser notes, code tasks, art requests, outbox drafts, pre-adapter receipts. |

Promotion from `.buddy/playground/` into `.bemore/` must be explicit and receipt-backed.

## Canonical implementation hooks

- `buddy-agent`: `src/buddy_agent/product_spine.py`
- `buddy-agent`: `buddy-product-spine summary|json|validate`
- `prismtek-apps`: `packages/core/buddyProductSpine.ts`
- `buddy-brain`: this document plus `skills/workspace-dispatch/SKILL.md` and `docs/BROWSER_AUTOMATION_PROFILE.md`

## Dispatch rule

When a mission involves multiple surfaces, dispatch against this spine:

1. choose the product surface that owns the user-visible action;
2. route worker planning through Workspace Dispatch;
3. write local draft/receipt artifacts before external actions;
4. promote to `.bemore` only after review;
5. require approval before external side effects;
6. record secret-free receipts after each completed, failed, denied, or cancelled step.

## Done definition

A feature is product-linked when it has:

1. an owner repo;
2. a product surface id;
3. a risk class;
4. a receipt/artifact path;
5. a promotion path between `.buddy/playground` and `.bemore` if applicable;
6. tests or validation commands;
7. no hidden external side effects.
