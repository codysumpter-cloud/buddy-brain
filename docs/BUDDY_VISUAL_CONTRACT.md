# Buddy Visual Contract

This repo uses Buddy visuals for operator-facing docs, status surfaces, and coordination diagrams. The goal is consistency with the broader Buddy system, not a new mascot fork.

## Roles

| Role | Asset | Purpose |
| --- | --- | --- |
| Buddy Brain README mascot | `assets/buddy-brain-mascot.svg` | Animated ASCII operator mascot for this repo |
| Default pixel Buddy | `assets/default-buddy.svg` | Canonical mint pixel Buddy avatar for docs/contracts |
| Machine-readable contract | `config/buddy-visual-contract.json` | Shared style and animation metadata |

## Canonical style

Buddy should look like the attached mint/cyan pixel-pet reference:

- round mint/cyan body;
- deep navy high-contrast outline;
- heart-shaped antler/ear nubs;
- small top tuft;
- large soft face panel;
- tiny dot eyes with small highlights;
- small friendly smile;
- plus/blush cheek marks;
- tiny side arms;
- tiny rounded feet;
- gold heart belly charm;
- asymmetric cyan and white highlight clusters;
- transparent background for reusable assets.

The look should be crisp, readable, and game/sprite friendly. Prefer hard pixel edges over soft gradients.

## Animation states

Buddy Brain uses the same state contract as `buddy-agent`:

```text
idle -> happy -> thinking -> sleepy -> repeat
```

| State | Operator meaning |
| --- | --- |
| `idle` | Ready, watching repo state, no active claim |
| `happy` | Green checks, good handoff, completed draft/review |
| `thinking` | Reviewing policy, reconstructing context, resolving ambiguity |
| `sleepy` | Standby, paused, waiting for host/runtime/user action |

Default timing:

| Setting | Value |
| --- | --- |
| Frame duration | `900ms` |
| Full cycle | `3600ms` to `4800ms` depending on surface |
| Loop | `true` |
| Reduced motion | Show `idle` only |

## Do not draw Buddy as

- a phone;
- a gamepad;
- a monitor/screen body;
- a generic robot head;
- a 3D rendered mascot;
- a blurry painterly creature;
- an existing copyrighted character silhouette.

Buddy is the living companion. The app, terminal, website, or HUD is the device around Buddy.

## Repo-specific overlay rules

Buddy Brain may add operator-brain context around the base Buddy style, such as:

- small `[ BRAIN ]` label in ASCII/docs mascot;
- policy/review/green/standby captions;
- council or memory motifs in diagrams;
- repo-status text around the mascot.

Do not change the base silhouette away from the canonical Buddy shape.

## Asset hygiene

- Keep SVGs lightweight and text-readable.
- Do not commit generated private media or user-specific source assets.
- Prefer transparent backgrounds for reusable Buddy assets.
- Keep README assets small enough for GitHub rendering.
- Update `config/buddy-visual-contract.json` when the style contract changes.
