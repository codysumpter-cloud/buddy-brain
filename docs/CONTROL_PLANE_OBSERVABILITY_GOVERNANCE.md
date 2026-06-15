# Buddy Brain Control Plane and Observability Governance

Status: spec-only governance contract  
Owner repo: `codysumpter-cloud/buddy-brain`  
Related runtime repo: `codysumpter-cloud/buddy-agent`  
Related orchestrator repo: `codysumpter-cloud/omni-buddy`  
Related receiver repo: `codysumpter-cloud/knowledge-vault`  
Reference systems: AgentRQ, Monocle

## Purpose

Buddy Brain owns the governance layer for Buddy behavior: policy, council review, risk rules, durable decisions, and cross-repo operating standards.

This document defines how Buddy Brain should govern optional integrations with:

- AgentRQ as a human-in-the-loop control plane.
- Monocle as a private trace and verification layer.
- Knowledge Vault / Vegapunk Brain as the durable sanitized memory receiver.

This is a governance spec, not a runtime adapter.

## Layer boundaries

| Layer | Owns | Must not own |
| --- | --- | --- |
| Buddy Brain | policy, risk rules, approval semantics, memory emission rules | live task execution |
| Buddy Agent | runtime task execution, task receipts, adapter implementation | durable governance truth |
| Omni Buddy | multi-workspace routing and orchestration | single-agent implementation details |
| Knowledge Vault | validated durable graph/memory records | raw traces, secrets, raw prompts |
| AgentRQ | optional external task/approval workspace | Buddy's source of policy truth |
| Monocle | optional external observability/tracing | public memory or policy truth |

## Governance position

AgentRQ and Monocle are useful Buddy stack layers, but neither replaces Buddy Brain.

- AgentRQ may coordinate task state and human approvals.
- Monocle may provide private runtime traces and trace-based tests.
- Buddy Brain remains the policy authority for what actions require approval, what may be persisted, and what must be redacted.

## AgentRQ policy

Buddy Brain permits AgentRQ integration only when:

- The operator explicitly configures a workspace.
- Tokens and workspace URLs remain local/private.
- Buddy's own risk policy still runs before actions execute.
- AgentRQ approval records are treated as additional evidence, not as a bypass.
- Broad command allowlists or `allow_all_commands` behavior require separate explicit approval.
- Attachments are handled under the same privacy and safety rules as any other input.

Buddy Brain blocks durable emission of:

- AgentRQ tokens
- tokenized MCP URLs
- raw task chat history
- private workspace identifiers unless intentionally public
- attachment contents
- private operator notes
- hidden task metadata

## Monocle policy

Buddy Brain permits Monocle integration only when raw traces remain private by default.

Raw traces may be used for:

- debugging
- regression tests
- trace-based assertions
- tool-call verification
- duration and error analysis
- local/private observability

Raw traces must not be persisted to Knowledge Vault.

Only sanitized trace receipts may be emitted, such as:

- workflow name
- public task or PR reference
- high-level tool categories
- validation pass/fail
- approval pause count
- denial count
- redaction summary
- error class without private stack details

## Durable memory rules

Knowledge Vault may receive only sanitized graph events.

Allowed durable event examples:

- "Buddy Agent completed task X with validation Y."
- "Human denied risky action Z."
- "Monocle trace assertions passed for workflow W."
- "AgentRQ task moved from ongoing to completed."

Blocked durable event examples:

- raw prompt text
- raw model response text
- full AgentRQ chat thread
- OAuth tokens
- bearer tokens
- private MCP URLs
- stack traces with local paths
- browser session data
- credentialed API request/response bodies
- unredacted user IDs, tenant IDs, or session IDs

## Approval semantics

Buddy Brain defines these outcomes for AgentRQ-backed approval flows:

| Outcome | Meaning | Durable emission |
| --- | --- | --- |
| `approved` | Human approved the described action and scope | sanitized decision receipt |
| `denied` | Human denied the described action | sanitized decision receipt |
| `needs_more_context` | Human requested clarification or smaller scope | sanitized task/decision receipt |
| `expired` | Approval was not answered in time | sanitized task receipt |
| `not_required` | Action fell below approval threshold | optional task receipt |

No adapter may convert silence into approval.

## Council review defaults

Use council review before enabling runtime behavior that changes:

- shell execution
- repository writes
- credential handling
- task queue mutation
- external service calls
- trace export destination
- Knowledge Vault emission scope
- AgentRQ permission defaults
- Monocle cloud export configuration

## Adapter readiness checklist

A Buddy stack integration is not ready until it has:

- explicit local-only secret loading
- `.gitignore` coverage for tokenized config and trace output
- allowlisted AgentRQ operations
- explicit approval pause behavior
- Monocle opt-in setup
- raw trace privacy controls
- trace-to-receipt sanitizer
- schema validation against Knowledge Vault graph events
- tests for redaction and denied-action handling
- rollback notes

## Implementation status

Current status: spec-only.

Buddy Brain recognizes AgentRQ and Monocle as useful reference integrations, but no repo should claim production-native support until runtime adapters and tests exist in the owning implementation repos.
