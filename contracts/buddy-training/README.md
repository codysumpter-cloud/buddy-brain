# Buddy Training Contract

Buddy Training is a local companion progression contract for Buddy surfaces. It may make Buddy feel more alive, reward useful interactions, and unlock cosmetic or training milestones.

## Source of truth

- `buddy-brain` owns this contract and the schema in `contracts/buddy-training/state.schema.json`.
- `buddy-agent` owns executable state updates and CLI/runtime behavior.
- `prismtek-apps` owns app UI rendering and app-local storage/sync surfaces.
- AgentCraft may visualize training events, but it is not the source of truth.

## Training state meaning

Training state may describe:

- Buddy level and XP
- cosmetic resources such as sparks and snacks
- companion stats such as bond, focus, curiosity, discipline, creativity, reliability, and autonomy
- achievements and cosmetics
- evolution stage
- last explicitly recorded training action

Training state must not be used as:

- durable memory evidence
- approval state
- proof that a file changed
- proof that a command succeeded
- proof that user intent was satisfied
- hidden productivity tracking

## Allowed training actions

The MVP action vocabulary is:

```text
chat
remember
recall
skill_used
quest_completed
test_passed
doc_added
code_reviewed
memory_reviewed
approval_handled
```

App surfaces may add visual labels, icons, and animations, but should not invent new persisted action names until this contract is updated.

## Privacy defaults

Buddy Training must be explicit and consent-first.

Allowed signals:

- Buddy runtime receipts
- explicit app-local Buddy interactions
- completed Buddy tasks
- user-approved memory review or skill practice
- test or validation completion events

Disallowed default signals:

- raw keystroke capture
- global click capture
- prompt/content scraping for XP
- hidden productivity monitoring
- using AgentCraft HUD events as receipt evidence

## AgentCraft bridge

AgentCraft can receive safe, redacted, local-only HUD events for training progress. AgentCraft events are decorative observability and must not bypass Buddy approvals, policy gates, receipts, or memory rules.

## App rendering guidance

`prismtek-apps` should treat this as a companion UI contract:

```text
Buddy action -> Buddy Agent reward -> Buddy Training state -> app renders growth
```

The app should prefer original Buddy Garden or Buddy Workshop styling over directly copying referenced idle-game branding.
