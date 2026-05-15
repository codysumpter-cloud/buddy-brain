# WorldBox AgentCraft Safe Tools

This package is the safe, GitHub-hosted replacement for the experimental zip-based WorldBox helper kits.

It exists to support Prismtek's WorldBox + AgentCraft experiment without relying on brittle autonomous pixel clicking.

## Goal

Use WorldBox as a live sandbox for AgentCraft-style AI orchestration:

- WorldBox is the simulation/testbed.
- BMO is the policy and runtime authority.
- AgentCraft is the command-room HUD.
- Screen viewing is perception only.
- A future NML/BepInEx bridge is the real game API.

## Current stance

The no-mod screen-control path is not trusted for autonomous gameplay on the current Mac setup. The agent may observe the screen, describe plans, emit events, and guide the user, but must not claim it can reliably click WorldBox until input has been proven.

## Install

From the repo root:

```bash
npm link ./tools/worldbox-agentcraft
worldboxctl-safe help
agentcraft-worldbox-lite help
worldboxmod-plan help
```

If this repo does not use npm workspaces, this package still works through `npm link` because it has no external dependencies.

## Commands

### `worldboxctl-safe`

A zero-dependency safety wrapper. It does not click the game. It tracks mission events, blocks unsafe autonomous gameplay, and writes JSONL logs.

```bash
worldboxctl-safe help
worldboxctl-safe mode knowledge
worldboxctl-safe mission-start "WorldBox Ant World setup"
worldboxctl-safe observe "WorldBox map visible, no modal open"
worldboxctl-safe propose "User manually starts a new map; agent verifies Ant World setup" --risk low
worldboxctl-safe block "No-mod input is not proven; autonomous clicking disabled"
worldboxctl-safe done "Knowledge-mode handoff complete"
```

Default log path:

```text
~/.worldbox-agentcraft/events.jsonl
```

### `agentcraft-worldbox-lite`

A tiny local event viewer for the JSONL log.

```bash
agentcraft-worldbox-lite serve --port 4777
```

Open:

```text
http://127.0.0.1:4777
```

### `worldboxmod-plan`

A planning helper for the real bridge work. It does not install mods or modify WorldBox.

```bash
worldboxmod-plan roadmap
worldboxmod-plan checklist
worldboxmod-plan nml-brief
```

## Agent policy

The agent must follow this until the real mod bridge exists:

1. No autonomous WorldBox clicking.
2. No repeated Escape.
3. No blind `clear-ui` rituals.
4. No spread-clicking dangerous UI.
5. No achievement attempts through no-mod clicking.
6. Use screen viewer as eyes only.
7. Ask the user for manual actions when needed.
8. Emit AgentCraft events for observations, proposals, blocked actions, and completed steps.
9. Build the NML/BepInEx bridge as the real control path.

## Why this exists

The previous no-mod control attempts failed due to focus, modal dialogs, coordinate drift, and likely WorldBox rejecting synthetic input. More screenshots and better coordinates do not solve an input-layer failure. This package makes that boundary explicit.
