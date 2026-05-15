---
name: skillify
version: 1.0.0
description: |
  The meta skill. Turn any raw feature or script into a properly-skilled,
  tested, resolvable unit of agent-visible capability. Use when
  the user says "skillify this", "is this a skill?", "make this proper",
  or after a new feature is built without the full skill infrastructure.
  
  Paired with skill validation checks, skillify gives you a controllable
  equivalent of Hermes' auto-skill-creation: you build, skillify checks the
  checklist, validation verifies nothing is orphaned. The human keeps
  judgment; the tooling keeps the checklist honest.
triggers:
  - "skillify this"
  - "skillify"
  - "is this a skill?"
  - "make this proper"
  - "add tests and evals for this"
  - "check skill completeness"
tools:
  - search
  - session_search
  - write_file
mutating: false
---

# Skillify — The Meta Skill

## Purpose

Transform raw features, scripts, or capabilities into properly skilled units that integrate with the Hermes skill system. This ensures all capabilities are discoverable, testable, and maintainable.

## Problem

When building new features or scripts, developers often create functional code without the surrounding skill infrastructure (SKILL.md, tests, validation, resolver entries). This leads to:
- Orphaned capabilities that the agent cannot discover
- Untested contracts that break silently
- Inconsistent skill quality
- Difficulty in maintaining and evolving capabilities

## Contract

A feature is "properly skilled" when all ten checklist items are present:

1. `SKILL.md` — skill file with YAML frontmatter, triggers, contract, phases.
2. Code — deterministic script if applicable.
3. Unit tests — cover every branch of deterministic logic.
4. Integration tests — exercise live endpoints, not just in-memory shape.
5. LLM evals — quality/correctness cases if the feature includes any LLM call.
6. Skill validation — passes the repo's skill validation script.
7. Resolver trigger — `skills/README.md` entry with the trigger patterns the user actually types.
8. Resolver trigger eval — test that feeds trigger phrases to the resolver and asserts they route to this skill.
9. Validation check — `scripts/validate-skills.mjs` passes for this skill.
10. Documentation — clear purpose, usage, and expected outcomes.

## Trigger

- "skillify this" / "skillify" / "is this a skill?" / "make this proper"
- "add tests and evals for this"
- After building any new feature that touches user-facing behavior
- When you grep the repo and notice a script with no SKILL.md next to it
- When adding new functionality to bmo-stack, prismtek-apps, or omni-bmo

## Phases

### Phase 1: Audit what exists

For the feature being skillified, answer:

- **Feature name**: what does it do in one line?
- **Code path**: where does the implementation live (file path)?
- **Checklist status**: run the skillify audit (see below) and note which items are missing.

### Phase 2: Create missing pieces in order

Work the list top-down. Each earlier item constrains what later items look like (the SKILL.md contract determines what tests assert; tests determine what evals gate; the resolver entry determines what trigger-eval checks).

1. Write `SKILL.md` first. Frontmatter must include `name`, `version`, `description`, `triggers[]`, `tools[]`, `mutating`. Body has at minimum Contract, Phases, and Output Format sections.
2. Extract deterministic code into a script if applicable (scripts/*.ts for bmo-stack; host projects may use .mjs / .py / whatever their runtime uses).
3. Write unit tests for every branch of the script. Mock external calls (LLM, DB, network) so tests run fast and deterministic.
4. Add integration tests that hit real endpoints. These catch bugs the unit tests' mocks hide.
5. Add LLM evals if the feature includes any LLM call. Even a three-case eval (happy / edge / adversarial) is cheap insurance against prompt regressions.
6. Ensure the skill passes validation by running `node scripts/validate-skills.mjs`.
7. Add the resolver trigger to `skills/README.md`. Use the trigger patterns the user ACTUALLY types, not what you think they should type.
8. Add a resolver trigger eval that feeds those patterns in and asserts they route to the new skill.
9. Run validation checks. If it fails, fix the skill (or extend an existing one instead of creating a duplicate).
10. Update documentation if the skill writes files or changes state.

### Phase 3: Verify

Run each of these and confirm green:

```bash
# Unit tests
bun test test/<skill-name>.test.ts || npm test || python -m pytest

# Integration tests (when applicable)
# (Project-specific test command)

# Skill validation
node scripts/validate-skills.mjs

# Conformance tests (skill YAML + required sections)
# (Project-specific skill conformance test)
```

## Quality gates

A feature is NOT properly skilled until:

- All tests pass (unit + integration + evals).
- The skill passes the validation script (`scripts/validate-skills.mjs`).
- It appears in `skills/README.md` with accurate trigger patterns.
- The resolver trigger eval confirms patterns route to the new skill.
- Validation checks show no orphaned skills, no MECE overlaps, no DRY violations.
- Documentation is clear and complete.

## Anti-Patterns

- ❌ Code with no SKILL.md — invisible to the resolver; the agent will never run it.
- ❌ SKILL.md with no tests — untested contract; one prompt change regresses silently.
- ❌ Tests that reimplement production code — the reimplementation's bugs don't catch production's bugs.
- ❌ Resolver entry that uses internal jargon the user never types — trigger patterns must mirror real user language.
- ❌ Feature that writes to brain without a documentation entry — undiscoverable changes.
- ❌ Deterministic logic in LLM space — should be a script.
- ❌ LLM judgment in deterministic space — should be an eval.

## Why skillify + validation is the right pair

Hermes and similar agent frameworks auto-create skills as a background behavior. That's fine until you don't know what the agent shipped — checklists decay, tests drift, resolver entries get stale.

This approach gives you the same capability as two user-controlled tools:

- `/skillify` builds the checklist and helps you fill in the gaps.
- `validation` checks the whole skill tree: reachability, MECE, DRY, gap detection, orphaned skills.

You decide when and what. The human keeps judgment. The tooling keeps the checklist honest. In practice this combo produces zero orphaned skills, every feature with tests + evals + resolver triggers + evals of the triggers.

## Output Format

A skillify run produces, in order:

1. An audit printout listing which of the 10 items exist and which are missing for the target feature.
2. The files created to close each gap (SKILL.md, test files, resolver entries).
3. The final validation output confirming skill validity.
4. A one-line summary of the resulting skill completeness score (N/10).