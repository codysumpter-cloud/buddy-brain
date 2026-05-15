# BeMore stack remaining work checklist

This document tracks the remaining canonical runtime / capability / identity work still needed in `bmo-stack`.

## P0

- Keep the Hermes / BeMore capability contract as the canonical source of truth and verify downstream consumers match it.
- Validate that the merged capability parity map still matches current runtime/operator expectations.
- `master` is the active default branch and the earlier `main -> master` reconciliation removed the practical lead-branch drift. Only keep both names where compatibility or migration notes still require it.

## P1 — Canonical runtime gaps

- Continue removing legacy OpenClaw naming and compatibility types where they are no longer necessary.
- Move remaining runtime identity, path, and compatibility surfaces from OpenClaw-centric names to BeMore/Hermes-native names.
- Ensure posture, council behavior, operator rules, skills/manifests, Codex execution, and runtime discipline docs all reflect the BeMore/Hermes system consistently.

## P1 — Capability parity gaps

- Expand the canonical capability registry and contracts where the app/site now expose linked-account and linked-runtime behavior.
- Document the trust boundaries clearly for:
  - native app
  - linked account
  - linked runtime
  - web shell
- Tighten the separation between innate capabilities, learned skills, and deeper runtime/operator actions.

## P2 — Validation

- Add or strengthen validation/docs around user-taught skill packages and capability compatibility.
- Add explicit migration notes for repos still consuming OpenClaw-named runtime artifacts or paths.
