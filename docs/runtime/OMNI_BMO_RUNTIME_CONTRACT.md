# Omni-BMO Runtime Contract

This document mirrors the Omni-BMO runtime contract at the operator and integration layer.

## Purpose

`omni-bmo` remains the executable runtime reference. `bmo-stack` mirrors the contract here so operators, downstream repos, and runbooks have a canonical source of truth for:

- runtime modes
- transport state
- failover expectations
- profile semantics
- product-safe adapter boundaries

## Ownership split

- `omni-bmo` — executable runtime implementation, health checks, bridge adapters, operator controls
- `bmo-stack` — contract mirror, operator runbooks, validation posture, cross-repo boundary documentation
- `prismtek-apps` — product-safe pairing and reachability surfaces only

## Canonical transport modes

The runtime contract recognizes exactly these modes:

- `online`
- `mesh`
- `reticulum_fallback`
- `auto`

The meanings of those modes must stay aligned with the executable runtime implementation.

## Resolution rules

1. Explicit operator override wins over automatic selection.
2. `online` is preferred when healthy.
3. `mesh` is preferred when the online path is unhealthy but mesh access is healthy.
4. `reticulum_fallback` is the compact resilient control path.
5. The runtime must always expose the selected mode and the reason for the last transition.

## Required transport state

The mirrored state shape is captured in `schemas/transport-state.schema.json`.

At minimum, downstream integrations should expect:

- `selected_mode`
- `requested_mode`
- `last_reason`
- `online_healthy`
- `mesh_healthy`
- `reticulum_available`
- `last_transition_at`
- `override_source`

## Runtime profile posture

The mirrored profile shape is captured in `schemas/runtime-profile.schema.json`.

Profiles should remain composable and readable instead of becoming ad hoc shell-only presets.

Current profile families:

- environment profile — `desktop-dev | pi-live | demo-mode | field`
- latency profile — `snappy | balanced | robust`

Profile material may eventually live in executable files elsewhere, but the shape should stay stable here.

## Downstream adapter rules

### For `prismtek-apps`

Allowed to consume:

- pairing / unpaired state
- selected transport mode
- degraded / reachable / control-only status
- last successful heartbeat
- remote-session-available indicator

Not allowed to inherit wholesale:

- field operator hotkeys
- shell-centric diagnostics
- raw bridge secrets
- full council / operator workflow semantics

### For operator surfaces

Runbooks should always describe:

- how a mode is selected
- what degraded means
- what control-only means
- how to recover to normal operation

## Source-of-truth rule

When the executable `omni-bmo` implementation evolves, this mirrored contract in `bmo-stack` must be updated in the same change window so downstream repos do not drift.