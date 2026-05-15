# AgentCraft Integration

## Purpose

AgentCraft is an optional local observability overlay for BMO operator work. It can show active sessions, mission starts, file access summaries, command summaries, and idle states in a browser HUD.

It is not the source of truth for BMO runtime state, approvals, receipts, policy, memory, or persistence claims.

## Ownership boundary

- `bmo-stack` owns runtime policy, council review, approvals, receipts, worktree discipline, and validation.
- AgentCraft owns the local visual HUD.
- BeMore and Prismtek app surfaces may consume approved runtime summaries, but should not treat AgentCraft as a command authority.

## Safety defaults

The bridge is disabled by default.

```bash
AGENTCRAFT_ENABLED=1 node scripts/agentcraft-report.mjs hero_active
```

Default behavior:

- posts to the local AgentCraft server only
- redacts prompt text by default
- redacts common secret-like fields and token patterns
- truncates command summaries to 120 characters by default
- never fails the BMO runtime path if AgentCraft is offline

## Local usage

Start AgentCraft:

```bash
make agentcraft-start
```

Check the local AgentCraft server:

```bash
make agentcraft-health
```

Send a dry smoke event without transmission:

```bash
node scripts/agentcraft-report.mjs hero_active
```

Send local smoke events:

```bash
AGENTCRAFT_ENABLED=1 node scripts/agentcraft-report.mjs hero_active
AGENTCRAFT_ENABLED=1 node scripts/agentcraft-report.mjs mission_start '{"name":"BMO smoke test","prompt":"redacted smoke test"}'
AGENTCRAFT_ENABLED=1 node scripts/agentcraft-report.mjs hero_idle
```

Stop AgentCraft:

```bash
make agentcraft-stop
```

## Event mapping

| BMO runtime event | AgentCraft event | Notes |
| --- | --- | --- |
| `launch_task` | `hero_active`, `mission_start` | Mission prompt is redacted by default. |
| `status: thinking` | `hero_active` | HUD-only status cue. |
| `status: acting` | `hero_active` | HUD-only status cue. |
| file read/write/edit receipt | `file_access` | Prefer relative paths where possible. |
| guarded command receipt | `bash_command` | Summary is truncated by default. |
| `diff_proposed` | `file_access` | Treat as preview, not persistence. |
| `status: completed` | `hero_idle` | Completion claim still requires BMO receipt. |
| `status: failed` | `hero_idle` | Include error summary only after redaction. |

## Recommended checks

```bash
make agentcraft-doctor
make agentcraft-health || true
make runtime-doctor
```

## Non-goals

- Do not let AgentCraft bypass BMO approvals.
- Do not expose browser-triggered local command execution.
- Do not use AgentCraft events as durable memory evidence.
- Do not claim install, publish, persistence, or file mutation success without BMO receipts.
