# Buddy Product System Execution Plan

This document turns the Buddy manifesto into a repo-by-repo execution plan.

## Goal

Build Buddies as a real Prismtek product family with clear repo boundaries:

- `Prismtek` = house brand
- `Buddies` = product family
- `Lil' Buddies` = youth-safe branch
- `BMO` = flagship character and public entry point
- `AutoMindLab` = separate enterprise/services lane

## Canonical repo boundaries

### New private repo: `prismtek-buddy-core` (proposed)

This should become the crown-jewel Buddy domain repo.

Own here:

- `BuddyProfile` schema and validators
- `BuddyPolicy` schema and validators
- `BuddyMemory` schema and storage contract
- `BuddyReceipt` schema and ledger contract
- `BuddyTemplate` schema and compatibility metadata
- `BuddyPack` schema and install contract
- template sanitizer/export pipeline
- pack loader / pack capability registry
- memory weighting / ranking logic
- trust scoring / moderation hooks
- youth-safety rule sets
- private evals and safety fixtures

Do **not** keep these long-term in permissive public repos if they become moat logic.

### `prismtek-apps`

Own here:

- Buddy shell UX
- onboarding
- settings and trust controls
- memory cards UI
- receipts UI
- pack install / clone flows
- Creator Buddy, Teen Buddy, and Field Tech Buddy product surfaces
- local app state and platform clients
- pack-specific presentation and affordances

Consume `prismtek-buddy-core`; do not become the long-term home of crown-jewel Buddy logic.

### `bmo-stack`

Own here:

- operator runbooks
- fork governor / donor inventory
- policy and council operating docs
- runtime contracts and validation posture
- repo boundary docs
- open-core examples and public integration guidance

Do **not** let `bmo-stack` become the product-core repo for Buddy identity, memory ranking, or premium pack logic.

### `omni-bmo`

Own here:

- device/runtime execution
- transport selection
- local bridge adapters
- resilient remote operator posture
- companion runtime pairing state
- local/offline helper mode
- edge/device receipts for runtime actions

Expose product-safe runtime state to the app layer; do not own Buddy product identity or pack logic.

## Canonical objects

These objects should be frozen early and shared across the system:

- `BuddyProfile`
- `BuddyPolicy`
- `BuddyMemory`
- `BuddyReceipt`
- `BuddyPack`
- `BuddyTemplate`

## 90-day execution sequence

### Phase 1 — freeze vocabulary and boundaries (days 1-14)

1. lock naming across site, app, runtime, and docs
2. freeze canonical schemas for profile/policy/memory/receipt/pack/template
3. approve the repo boundary split above
4. classify repos as:
   - public/open-core
   - public/docs/examples
   - private/crown-jewel
   - archive/demo

### Phase 2 — extract Buddy core (days 15-30)

1. create `prismtek-buddy-core` privately
2. move shared Buddy schemas and validators there
3. move template sanitation and pack install logic there
4. add tests for:
   - publish-safe template export
   - never-publish memory flags
   - youth-safe policy gates
   - receipt generation

### Phase 3 — ship the Buddy shell (days 31-45)

Use `prismtek-apps` to ship one shell with:

- dashboard
- chat
- memory cards
- receipts
- tasks
- settings / trust controls

Do not build separate apps per pack. Build one shell and install packs into it.

### Phase 4 — ship the first pack wedge (days 46-60)

Ship `Creator Buddy` first.

Why first:

- strongest fit with Prismtek
- lower safety/regulatory burden than Teen Buddy
- strong continuity and project-memory use case

### Phase 5 — extend to the other two packs (days 61-90)

- `Teen Buddy` alpha with strict youth-safe policy gating
- `Field Tech Buddy` alpha with explicit verification posture and offline-first helper behavior
- Buddy Workshop alpha with sanitized template export only

## Non-negotiable product invariants

1. no live Buddy is ever sold or shared; only sanitized templates are
2. every meaningful action produces a receipt
3. no Buddy may fake capability, certainty, or execution
4. every pack must have a clear fallback mode
5. youth-safe packs must have separate policy rules, not cosmetic copy only

## KPI spine

Track these from the first alpha:

- weekly retained users
- number of users with 2+ Buddies
- receipts generated
- memory recalls that users keep
- projects resumed
- trust score
- "this feels like mine" score
- safety incident rate

## Immediate next actions

1. merge repo-boundary plan
2. create the private `prismtek-buddy-core` repo
3. move schema definitions there before more pack-specific code spreads
4. implement Creator Buddy first inside `prismtek-apps`
5. keep runtime boundaries explicit in `omni-bmo`
