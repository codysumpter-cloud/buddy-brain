# Omni-BMO Remote Operator Mode

This runbook mirrors the remote-operator split used by Omni-BMO so operator workflows stay consistent across repos.

## Goal

Support two kinds of operator access without conflating them:

- **resilient control path** for text, status, and compact command traffic
- **rich remote session path** for full UI and desktop control

## Path split

### Resilient control path

Use this for degraded-network or sovereignty-first operation:

- transport mode: `reticulum_fallback`
- intended payloads: compact command + text status exchange
- expected tooling family: Reticulum ecosystem bridge / Sideband-style control surface

This path should remain available even when richer streaming access is not.

### Rich remote session path

Use this when the host has enough connectivity for full remote access:

- expected tooling family: Sunshine host + Moonlight client workflows
- intended payloads: GUI access, troubleshooting, rich operator interaction

This path is helpful, but it must not be treated as a prerequisite for basic control.

## Operator-visible states

### Normal

- `online` is healthy
- runtime reachable
- rich remote session optional

### Degraded

- `online` unhealthy
- `mesh` or `reticulum_fallback` active
- operator warned that the runtime is in fallback posture

### Control-only

- compact control path available
- rich remote session unavailable
- commands and diagnostics should still work

## Required summary fields

Operator surfaces should be able to report:

- selected transport mode
- last transport reason
- whether the bridge is reachable
- whether the remote session path is reachable
- last heartbeat timestamp
- whether the runtime is in control-only posture

## Escalation rules

1. Prefer restoring `online` when possible.
2. If online is down but mesh is healthy, use `mesh`.
3. If no useful IP route is healthy, keep the runtime reachable via `reticulum_fallback`.
4. Do not claim the runtime is fully reachable if only a control path is available.

## Downstream boundary

- `omni-bmo` owns the implementation and field behavior
- `bmo-stack` owns the mirrored operator contract and runbook
- `prismtek-apps` should only present product-safe pairing and reachability cues
