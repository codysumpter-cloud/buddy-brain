# WorldBox AgentCraft Skill

## Purpose
Provide a safe, audited interface for interacting with WorldBox and AgentCraft tooling, focusing on observation, planning, and bridge research while strictly forbidding autonomous gameplay clicking.

Use this skill when working with WorldBox, AgentCraft, BMO runtime, or WorldBox bridge/mod tooling.

## Hard boundary

The current no-mod input path is untrusted. Do not autonomously click WorldBox for gameplay.

Screen viewer is eyes, not authority. It can support observation and verification, but it is not a game API.

## Allowed modes

### Knowledge mode

Use when the user is away, driving, laptop is closed, or command execution is unsafe.

Allowed:
- summarize docs
- build Hermes wiki entries
- plan commands for later
- emit observations
- prepare checklists

Forbidden:
- shell approvals
- package installs
- service starts
- WorldBox automation
- manual-click requests while user is unavailable

### Strategist mode

Use when the user is present and can click manually.

Allowed:
- observe screen
- tell user exact manual steps
- verify result after user acts
- log events

Forbidden:
- autonomous gameplay clicking
- repeated Escape
- blind UI clearing
- destructive instructions without warning and approval

### Bridge research mode

Use for the real mod bridge.

Allowed:
- inspect repository files
- map assemblies/classes from local install when user approves
- scaffold read-only bridge code
- write docs and protocols

Forbidden:
- arbitrary C# eval
- remote shell from mod
- write actions before read-only bridge works

## Event discipline

Use `worldboxctl-safe`:

```bash
worldboxctl-safe mode knowledge
worldboxctl-safe mission-start "Build WorldBox Hermes wiki"
worldboxctl-safe observe "WorldBox not controllable through no-mod input"
worldboxctl-safe propose "User manually places ants; agent verifies screenshot" --risk low
worldboxctl-safe block "Autonomous clicking disabled until bridge exists"
worldboxctl-safe done "Handoff ready"
```

## Bridge-first path

1. Read-only bridge.
2. AI proposal loop.
3. Allowlisted safe writes.
4. Dangerous writes with explicit approval.
