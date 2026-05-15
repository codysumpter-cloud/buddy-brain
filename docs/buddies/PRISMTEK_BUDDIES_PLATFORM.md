# Prismtek Buddies multi-surface platform architecture

## Positioning

Prismtek Buddies are portable companion identities. A Buddy is not bound to one chat surface, app shell, device, or rendering mode. The platform should let the same Buddy identity move across Prismtek-owned surfaces, ChatGPT-hosted surfaces, community surfaces, and future local/offline contexts while preserving continuity, policy, visual evolution, and receipts.

The core product thesis is that a Buddy should feel continuous wherever the user meets it:

- shared identity across surfaces
- memory continuity with explicit boundaries
- safety and trust policy that travels with the Buddy
- receipt-backed meaningful actions
- visual evolution from egg/baby forms into more expressive stages
- template marketplace primitives that never expose raw private live state

## Scope

This document defines the architecture contract for Prismtek Buddies as a multi-surface platform. It is a product/system architecture layer and does not implement Hermes-owned runtime stability, LiteRT/MLCSwift integration, fork assimilation, or the hierarchical context DAG foundation.

## Supported and planned surfaces

### Prismtek iOS app

The iOS app is the first native runtime surface for persistent Buddies. It should support live Buddy profile display, validated visual asset preview, Buddy Studio entry points, receipt timelines, user-controlled memory views, and safe save flows for compiled assets.

### Prismtek web app

The web app should mirror the canonical Buddy identity and asset contracts. It should support Buddy creation, preview, policy display, receipt inspection, template browsing, and administrative/review flows that benefit from a larger canvas.

### ChatGPT surface

The ChatGPT surface should represent a Buddy through sanitized template and session-safe state projections. It may reference a Buddy identity, template, or user-authorized memory summary, but it must not expose raw private Buddy state inside public prompts, marketplace assets, or reusable templates.

### Future ChatGPT App/MCP integration

A future ChatGPT App or MCP integration should expose explicit tools for Buddy lookup, receipt creation, template install, safe memory summary retrieval, and validated visual asset operations. Tool outputs should be scoped, least-privilege, and receipt-backed for meaningful actions.

### Discord and Telegram later

Community chat surfaces should be treated as lower-trust and higher-visibility contexts. Buddy actions there should use minimized memory projections, stricter safety policy defaults, and public/private boundary checks before rendering content or referencing user-specific context.

### Local/offline mode later

Local/offline mode should support cached Buddy identity, local-only memory shards, offline visual preview, and delayed receipt synchronization. Any local-only work must be clearly marked until it is synced and visible in the canonical backend.

## Canonical backend objects

### BuddyProfile

The stable identity object for a Buddy.

Required responsibilities:

- persistent Buddy ID
- owner/user binding
- display name and species/persona choices
- lifecycle stage such as egg, baby, child, teen, adult, or evolved
- installed template reference, when applicable
- active policy reference
- active visual asset references
- surface availability flags

BuddyProfile should not contain raw conversational transcripts. It should reference memory and receipts by ID.

### BuddyMemory

The continuity layer for user-authorized memory.

Required responsibilities:

- memory shards scoped by user, Buddy, surface, and sensitivity
- summary views suitable for lower-trust surfaces
- provenance for when and why memory was written
- retention controls
- user-visible deletion/export paths

BuddyMemory must distinguish private live Buddy state from reusable public template content.

### BuddyPolicy

The safety and trust contract for a Buddy.

Required responsibilities:

- allowed surfaces
- age/safety lane constraints
- memory access level per surface
- action permissions
- public/private rendering rules
- escalation/fallback behavior
- Lil’ Buddies constraints for child-friendly or family-safe experiences

BuddyPolicy should travel with BuddyProfile and should be checked before memory access, action execution, template export, or community-surface rendering.

### BuddyVisualAsset

The compiled renderable asset for a Buddy.

Required responsibilities:

- render style: ASCII, pixel, or future style
- lifecycle stage and animation set
- exact frame dimensions
- normalized metadata
- validation result and score references
- source/provenance references
- runtime-safe compiled payload or pointer

Runtime surfaces must render BuddyVisualAsset only after the asset passes the validation pipeline.

### BuddyReceipt

The audit object for meaningful Buddy actions.

Required responsibilities:

- action kind
- actor and surface
- affected BuddyProfile, BuddyMemory, BuddyVisualAsset, BuddyTemplate, or BuddyPack IDs
- timestamp
- source/provenance
- validation or policy decisions when relevant
- rollback or recovery hints where possible

Receipts should be created for meaningful actions such as memory writes, template installs, visual asset compilation, asset saves, policy changes, and cross-surface sync.

### BuddyTemplate

A sanitized reusable Buddy blueprint.

Required responsibilities:

- public display metadata
- allowed species/stages/personality tags
- default policy profile
- default style pack choices
- starter prompts or behavior rules that are safe to share
- no raw private Buddy state
- no user-specific secrets, private memory, or transcripts

BuddyTemplate is marketplace-safe only if it has passed sanitization and provenance checks.

### BuddyPack

A bundle of templates, style packs, sample visual specs, and optional starter flows.

Required responsibilities:

- pack metadata and versioning
- included BuddyTemplate IDs
- included style pack IDs
- compatible surfaces
- license/provenance metadata
- safety lane eligibility

BuddyPack may include public starter assets, but it must not include private live Buddy state.

## Public templates vs private live Buddy state

The platform must keep reusable templates and private live state separate.

Public BuddyTemplate and BuddyPack objects may contain:

- sanitized persona rules
- starter lifecycle/stage defaults
- safe behavior constraints
- public style pack references
- public sample visual specs
- marketplace metadata

Private live Buddy state may contain:

- user-specific BuddyProfile values
- private BuddyMemory shards
- private receipts
- user-specific visual evolution history
- surface-specific preferences
- policy overrides

Raw private Buddy state must never be embedded in public templates, marketplace packs, public prompts, or third-party integration payloads.

## Lil’ Buddies safety lane

Lil’ Buddies is a stricter lane for child-friendly, family-safe, or broader-audience companion experiences.

Required constraints:

- conservative memory defaults
- no sensitive inference or adult persona behavior
- limited external action permissions
- safer template vocabulary
- explicit guardian/owner controls where applicable
- stricter public/private state separation
- visual assets that stay cute, readable, non-threatening, and non-infringing

Lil’ Buddies should be represented as BuddyPolicy constraints, not as an ad hoc UI-only toggle.

## Visual asset pipeline

No raw model output should render directly in runtime.

All visual output must move through this sequence:

1. BuddyVisualSpec
2. style pack selection
3. generation, import, or drawing
4. normalization
5. validation
6. scoring
7. compiled BuddyVisualAsset
8. runtime preview or save

Runtime display surfaces should only render compiled BuddyVisualAsset objects with successful validation metadata.

### BuddyVisualSpec

BuddyVisualSpec is the intent contract. It should describe species, lifecycle stage, style, canvas, allowed animations, anchors, palette/style-pack references, and generation constraints.

### Style pack selection

Style packs define exact render rules. For the first wedge, the anchor direction is a cute, blocky, browser-dino/virtual-pet T-Rex style with a readable silhouette, simple face, tiny arms, and strong small-size legibility.

### Generation, import, or drawing

Generation providers, imports, and in-product drawing tools are all candidate producers. They must emit candidate assets into the same normalization and validation gate before preview/save.

### Normalization

Normalization should make dimensions, frame counts, frame ordering, transparent background behavior, palette constraints, ASCII line widths, and metadata consistent before validation.

### Validation

Validation should reject malformed assets and surface structured issues. Existing bmo-stack buddy_art validators provide the foundation for ASCII dimensions, pixel dimensions, imagePath presence, normalized metadata, and provenance receipt helpers.

### Scoring

Scoring should help Buddy Studio show quality and repair guidance. Initial scoring dimensions should include readability, silhouette clarity, animation stability, charm, and style compliance.

### Compilation

Compilation produces the runtime-safe BuddyVisualAsset. Compiled assets should include validation metadata, score metadata, provenance, and exact rendering dimensions.

### Runtime preview/save

Preview and save flows must only use compiled assets. Invalid or uncompiled candidates can be shown only inside an editor/repair context that clearly indicates they are not runtime-safe.

## Receipts

Receipts are part of the product trust moat. The platform should create BuddyReceipt records for meaningful actions, including:

- Buddy creation
- template install
- policy update
- memory write/delete
- visual candidate generation
- visual asset normalization
- visual asset validation
- visual asset compilation
- runtime asset save
- cross-surface sync
- marketplace publishing or installation

Receipts should make it possible to answer: what changed, who/what changed it, where it happened, what policy allowed it, what validation ran, and how to roll it back or recover if needed.

## Marketplace and template safety

The sanitized template marketplace should trade in BuddyTemplate and BuddyPack objects, not private live Buddy state.

Marketplace publishing must require:

- private state scrub
- license/provenance metadata
- public template safety review
- policy compatibility review
- visual asset validation for included public assets
- clear distinction between inspiration references and licensed product assets

External inspiration sources and generators may inform direction or integration planning, but protected third-party art, names, or character assets must not ship without license clearance.

## Cross-surface runtime model

Each surface should receive a surface projection rather than the entire Buddy object graph.

A surface projection should include:

- BuddyProfile fields needed for display
- policy-permitted BuddyMemory summaries only
- active compiled BuddyVisualAsset references
- allowed actions for that surface
- recent receipts safe for that surface
- template metadata safe for that surface

This projection model prevents a low-trust surface from accidentally receiving high-trust private Buddy state.

## Initial platform wedge

The smallest useful architecture wedge is:

- define this platform architecture in bmo-stack
- keep prismtek-buddy-core PR #2 focused on visual contracts and T-Rex style packs
- use bmo-stack buddy_art validators as the operator-side validation/scoring/compiler foundation
- defer prismtek-apps Buddy Studio implementation until core contracts are green and mergeable
- keep Hermes-owned runtime/LiteRT/DAG work out of this PR

## Next visual pipeline PR sequence

1. prismtek-buddy-core: make PR #2 green, remove temporary smoke workflow after Actions are healthy, and merge only after GitHub checks pass.
2. bmo-stack: extend buddy_art validators to reject non-object frames, reject boolean canvas dimensions, add scoring objects, add compiler output, and add receipt coverage.
3. prismtek-apps: implement issue #97 guided Buddy Studio after the core contracts are merged, with ASCII/pixel preview, quality score, one-tap repairs, and save-only-valid compiled assets.

## Non-goals

This document does not implement:

- Build 47 runtime stability
- LiteRT or MLCSwift integration
- fork upgrades or donor assimilation
- bmo-stack DAG foundation PR #293
- Buddy Studio UI in prismtek-apps
- third-party generator integration
- marketplace publishing UI

## Review checklist

- Buddies are defined as portable companions, not one-surface chat characters.
- All named surfaces have explicit trust posture.
- Canonical backend objects are named and bounded.
- Lil’ Buddies has a policy-backed safety lane.
- Public templates and private live state are separated.
- Raw private Buddy state is forbidden in public templates.
- Meaningful actions require receipts.
- Visual assets compile through validators before runtime display.
- Third-party inspiration is treated as inspiration/integration only until license clearance.
