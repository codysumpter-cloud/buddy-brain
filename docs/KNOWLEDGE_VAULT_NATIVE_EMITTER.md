# Knowledge Vault Native Emitter: Buddy Brain

## Status

This document is a **native emitter specification only**. Buddy Brain does not yet include a production code adapter that writes directly into Knowledge Vault / Vegapunk Brain. Until that adapter exists and is reviewed, any emitted event is a drafted, reviewed artifact rather than automatic governance output.

BUAP remains the profile and routing layer. Buddy Brain owns governance, policy, council, runbook, and decision records; BUAP does not become the runtime or governance owner.

## Source identity

- Source repo: `codysumpter-cloud/buddy-brain`
- Source name for Vegapunk Brain events: `buddy-brain`
- Receiver contract: `knowledge-vault/99-System/Vegapunk Brain/integrations/satellite-native-emitters.md`
- Receiver schema: `knowledge-vault/99-System/Vegapunk Brain/emitters/graph-event.schema.json`

## Emitter responsibility

Buddy Brain may emit public-safe event drafts for durable ecosystem coordination:

- governance decisions;
- policy updates;
- council review outcomes;
- runbook updates;
- cross-repo ownership decisions;
- public-safe concepts that should be searchable across the Buddy ecosystem.

Buddy Brain must keep private memory and sensitive operator context out of the public Knowledge Vault. The emitter records reviewed public summaries, not private reasoning, private preferences, raw conversations, account details, or hidden internal context.

## Allowed event classes

Buddy Brain may draft the following event classes when they pass sanitization and human approval rules:

| Event class | Typical Vegapunk event types | Purpose |
| --- | --- | --- |
| `decision` | `decision_made`, `policy_updated`, `council_update` | Record durable governance, council, and ownership outcomes. |
| `system` | `repo_updated`, `feature_added`, `feature_removed` | Record public-safe ecosystem capability changes. |
| `task` | `task_created`, `task_completed` | Record public-safe runbook or governance work items. |
| `concept` | `concept_created`, `concept_updated`, `relationship_created` | Record reusable public concepts for search and linking. |

## Trigger points

Native emitter code, once implemented, should draft an event at these points:

1. **Council review** — reviewed summary, outcome, affected repos, and follow-up tasks.
2. **Policy change** — durable policy update with human approval and rollback note.
3. **Cross-repo ownership decision** — source-of-truth decision, repo boundaries, and affected contracts.
4. **Runbook update** — public-safe operational change, validation state, and owner.

## Human approval requirement

Buddy Brain must require human approval before durable governance decisions are emitted. A native adapter may prepare a draft automatically, but it must not publish governance records to Knowledge Vault intake until the decision is explicitly reviewed and approved.

Minimum approval metadata for durable governance events:

- `approval_state`: `approved` or `draft-only`;
- `approved_by`: public-safe reviewer label, not a private account credential or contact export;
- `approved_at`: UTC timestamp;
- `rollback`: public-safe rollback summary;
- `scope`: affected repos, docs, or contracts.

## Never emit

The native emitter must reject or strip all of the following:

- private memory, personal operator context, hidden preferences, private notes, or sensitive account details;
- secrets, tokens, API keys, cookies, private keys, OAuth material, passwords, or credentials;
- raw prompts, hidden reasoning, raw transcripts, private browser sessions, or private document excerpts;
- private local paths, personal machine names, account identifiers, or environment-specific absolute paths;
- unapproved governance decisions or policy changes;
- any information that would make the public Knowledge Vault a private memory database.

## Event draft shape

Emitter output should be an event JSON object that validates against `graph-event.schema.json` before intake:

```json
{
  "event_id": "evt-buddy-brain-decision-example",
  "event_type": "decision_made",
  "source": "buddy-brain",
  "timestamp": "2026-06-15T00:00:00Z",
  "payload": {
    "class": "decision",
    "summary": "Reviewed public-safe governance decision for Knowledge Vault intake.",
    "scope": ["public repo or contract name only"],
    "approval_state": "approved",
    "rollback": "Revert the related docs-only decision record.",
    "adapter_status": "spec-only"
  }
}
```

The example above is intentionally fake and public-safe. Real adapter output must provide reviewed governance receipts without exposing private memory or sensitive operator context.

## Adapter requirements

Before Buddy Brain can be considered a complete native satellite emitter, it needs reviewed adapter code that:

1. builds event drafts from reviewed public governance records only;
2. validates every draft against Knowledge Vault's `graph-event.schema.json`;
3. blocks emission when human approval is missing for durable decisions;
4. blocks emission on sanitizer failure;
5. writes to the reviewed receiver intake path rather than directly mutating compiled graph outputs;
6. includes tests for private-memory exclusion, approval enforcement, secret stripping, private-path stripping, and unapproved policy-change rejection.

Until then, this spec defines the contract and guardrails, not a live emitter implementation.
