# Buddy Symphony Contract v0.1

## Purpose

Buddy Symphony defines how BMO and BeMore Buddies can use Symphony-style work orchestration without making Symphony the source of truth for Buddy state, memory, approvals, or persistence claims.

Symphony is treated as a scheduler/runner for isolated implementation work. BMO remains the policy, approval, receipt, and runtime-contract owner. BeMore app surfaces remain supervision and companion UX surfaces.

## Boundary

### Symphony owns

- Polling eligible work from an issue tracker or work queue.
- Creating deterministic per-work-item workspaces.
- Running coding-agent sessions inside those isolated workspaces.
- Retrying, reconciling, and releasing claimed work.
- Emitting operator-visible run status.

### BMO owns

- Buddy identity, policy, council review, and approval gates.
- Runtime event validation and receipt requirements.
- Durable memory promotion.
- XP, bond, proficiency, unlock, and evolution effects.
- Whether a Symphony result is accepted into source-of-truth state.

### BeMore / Prismtek app surfaces own

- Showing Buddy work status to the user.
- Displaying proofs, pending approvals, and handoff summaries.
- Triggering only approved relay actions.
- Falling back to Mac/runtime relay for execution.

## Core model

### BuddyWorkItem

```json
{
  "id": "string",
  "source": "linear | github | local | manual",
  "source_ref": "string",
  "buddy_id": "string",
  "title": "string",
  "description": "string",
  "priority": "low | normal | high | urgent",
  "state": "queued | running | waiting_review | accepted | rejected | failed | canceled",
  "labels": ["string"],
  "constraints": ["string"],
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### BuddySymphonyRun

```json
{
  "run_id": "uuid",
  "work_item_id": "string",
  "buddy_id": "string",
  "workspace_path": "string",
  "status": "claimed | preparing | running | waiting_review | completed | failed | canceled",
  "attempt": 1,
  "session_id": "string",
  "started_at": "ISO8601",
  "ended_at": "ISO8601 or null",
  "proofs": ["BuddySymphonyProof"],
  "receipt_refs": ["string"]
}
```

### BuddySymphonyProof

```json
{
  "proof_id": "uuid",
  "run_id": "uuid",
  "kind": "ci_status | diff | pr | review_feedback | complexity | walkthrough | artifact | receipt",
  "summary": "string",
  "uri": "string or null",
  "metadata": {},
  "created_at": "ISO8601"
}
```

## Event mapping

All Buddy Symphony activity should be converted into existing Buddy runtime event streams before it can affect Buddy state.

| Symphony lifecycle | Buddy runtime event | Required receipt posture |
| --- | --- | --- |
| Work item claimed | `status` | No Buddy growth effect. |
| Workspace created/reused | `receipt` | Workspace path may be summarized; avoid secrets. |
| Agent turn started | `status` | No persistence claim. |
| File diff proposed | `diff_proposed` | Requires diff reference before review. |
| Artifact produced | `artifact_created` | Requires artifact metadata. |
| Proof collected | `receipt` | Required before XP/proficiency effects. |
| Human approval needed | `tool_request` | Safe default is reject. |
| Run accepted | `receipt` | Required before Buddy growth/evolution effects. |
| Run failed/canceled | `status` + optional `receipt` | No growth effect unless policy explicitly awards reflection XP. |

## Acceptance rules

A Symphony run may improve Buddy state only when all are true:

1. The work item is tied to a known `buddy_id`.
2. The run has at least one proof object.
3. The proof object has been converted into a BMO receipt.
4. Any source mutation has a diff, PR, CI, or equivalent receipt.
5. Council or operator policy accepts the run.
6. The Buddy state machine allows the resulting transition.

## Rejection rules

Reject or hold the run if any are true:

- The run claims persistence without a receipt.
- The run modifies source without a diff or PR reference.
- The run requests destructive commands without explicit approval.
- The run attempts to promote memory without evidence.
- The run updates Buddy XP, bond, unlocks, or evolution directly.
- The run workspace path escapes its assigned workspace root.

## Recommended Buddy-specific states

```text
queued -> claimed -> preparing -> running -> waiting_review -> accepted
                                                -> rejected
                              -> failed
                              -> canceled
```

## Minimum integration slice

1. Keep Symphony runtime separate from BeMore app surfaces.
2. Add a Buddy-owned `WORKFLOW.md` prompt for coding agents.
3. Map Symphony status/proof events into Buddy runtime events.
4. Render read-only Symphony run status in BeMore Mission Control.
5. Award Buddy growth only after accepted BMO receipts.

## Non-goals

- Symphony is not a Buddy memory store.
- Symphony is not a Buddy state machine.
- Symphony is not an approval bypass.
- Symphony is not the public app runtime.
- Symphony should not make source mutation claims without proof.
