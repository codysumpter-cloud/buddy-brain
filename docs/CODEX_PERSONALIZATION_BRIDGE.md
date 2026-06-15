# Codex Personalization Bridge

This bridge defines the Buddy Brain files that Codex may load as safe
repo-backed user/operator profile context when operating under BUAP. It does
not create hidden/global model personalization and does not replace repo-local
`AGENTS.md` contracts.

## Safe profile inputs

Load these files when repository access is available and the session context
allows it:

| File | Use |
| --- | --- |
| [`../soul.md`](../soul.md) | Fast Buddy/BMO posture, decision rules, owner-path discipline, validation posture, and tone. |
| [`../memory.md`](../memory.md) | Direct main-session durable truths, Cody preferences, repo boundaries, and repeated lessons. Skip in shared or group contexts. |
| [`../routines.md`](../routines.md) | Preferred operator routine order and machine-readable routine owner. |
| [`../RESPONSE_GUIDE.md`](../RESPONSE_GUIDE.md) | Reply discipline, capability reporting, troubleshooting, and reliability rules. |
| [`../context/RUNBOOK.md`](../context/RUNBOOK.md) | Restart recovery, checkpoint protocol, verification protocol, council routing, and worker split. |

For broader startup context, follow [`../AGENTS.md`](../AGENTS.md) and
[`../context/identity/AGENTS.md`](../context/identity/AGENTS.md). If startup
order drifts between those files and the runbook, treat that as a source-of-truth
bug instead of silently choosing one.

## Codex loading contract

Codex should treat these files as Source-backed profile/context inputs:

1. Load BUAP first when the session is BUAP-enabled:
   [`codysumpter-cloud/buddy-universal-agent-profile`](https://github.com/codysumpter-cloud/buddy-universal-agent-profile).
2. Load the safe Buddy Brain files above for operator preferences, posture,
   response expectations, routine order, and recovery/checkpoint behavior.
3. Use Knowledge Vault for durable project history and graph-backed context:
   [`codysumpter-cloud/knowledge-vault`](https://github.com/codysumpter-cloud/knowledge-vault).
4. Use Buddy Agent for guarded execution, risk classification, approvals,
   worker reports, and sanitized receipts:
   [`codysumpter-cloud/buddy-agent`](https://github.com/codysumpter-cloud/buddy-agent).
5. Use Omni Buddy only when the task involves local voice, vision, transport,
   device, or hardware runtime claims:
   [`codysumpter-cloud/omni-buddy`](https://github.com/codysumpter-cloud/omni-buddy).

## Safety boundary

Do not copy private or credential-bearing material into prompts, public repos,
memory events, receipts, or docs. In particular, never copy:

- `.env` files, API keys, tokens, cookies, passwords, OAuth material, private
  keys, wallet data, or credential inventories;
- raw private prompts, full private transcripts, browser state, signed-in
  session state, or account identifiers;
- private local filesystem paths, generated private media, sensitive receipts,
  or host-only runtime state;
- ignored private notes or credential files from Knowledge Vault or local
  operator machines.

When a profile update is worth preserving, distill it into a public-safe durable
truth, runbook change, or Knowledge Vault event draft after meaningful completed
work. Do not claim persistence unless the owning repo or adapter write path was
actually used and verified.
