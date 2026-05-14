# Signed-in Safari Social Automation

Buddy Brain coordination note for the `signed-in-safari-social-automation` skill.

## Purpose

Use this as a routing clue when a browser task requires the user's real signed-in Safari state and isolated browser automation cannot access that state.

## Policy

Buddy Brain may recommend this skill, summarize its safety posture, and remind the operator of prerequisites. Buddy Brain must not execute Safari automation directly.

Execution belongs to Hermes or Buddy runtime adapters after explicit user approval.

## Safety requirements

- Require explicit approval before signed-in Safari automation.
- Never request or store raw passwords, tokens, cookies, API keys, or MFA codes.
- Prefer read-only verification and draft preparation.
- Treat profile edits, publishing, replies, DMs, or account changes as external actions.
- Public visibility must be verified separately from local UI publication.

## Related skills

- `content-growth-social-ops`
- `hermes-x-insights-analyst`
- `moneyprinter-content-factory`
