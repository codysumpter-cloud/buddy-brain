# Independent Norn memory, navigation and skill scoring

Buddy Brain evaluates `prismtek-norn-memory-navigation-skills-receipt-v1` evidence produced by the Prismtek Buddy Core Godot runtime.

The game cannot establish success by setting `passed: true`. This scorer recomputes the complete source SHA-256, requires exactly seven declared measurement domains and independently judges the raw values.

## Scored domains

| Domain | Independent requirement | Weight |
| --- | --- | ---: |
| Autobiographical recall | The cue retrieves `red_ball`, the match score is at least `0.45`, and exactly one retrieval is recorded | 15 |
| Semantic knowledge | Two supporting observations establish an edible fact with confidence at least `0.55`; one weak contradiction does not flip it; exactly one contradiction is recorded; retained confidence remains at least `0.50` | 15 |
| Spatial routing | The route is exactly `hall → garden`, contains two steps and preserves host validation, rather than using the dangerous direct shortcut | 15 |
| Hierarchical skill | The three-step sequence becomes learned, produces exactly one proposal, expands into exactly three host-validated primitives and has reliability at least `0.75` | 15 |
| Skill adaptation | One failed execution lowers reliability from at least `0.75` to below the prior value and at most `0.70` | 15 |
| Runtime integration | An outcome creates a named episode, one matching recall, a grounded fact with confidence at least `0.35`, and one mapped room | 15 |
| Persistence | Restore preserves exactly one episode, fact, room and learned skill | 10 |

All seven independent judgments and the game summary must agree for a green `100/100` result.

## Adversarial tests

The scorer independently fails or rejects:

- an irrelevant autobiographical memory hidden behind a green game summary;
- a weak rumor overwriting a supported fact;
- a dangerous shortcut presented as safe routing;
- an unlearned or non-host-validated skill;
- a skill failure that does not reduce reliability;
- incomplete persistence;
- summary counts that disagree with the raw measurements;
- missing measurement domains;
- modified payloads whose SHA-256 no longer matches.

Scoring is deterministic and does not mutate the supplied receipt.

## Claim boundary

A green score establishes the seven measured bounded memory, navigation and skill software behaviors for the exact content-addressed receipt. It does not establish human autobiographical memory, perfect navigation, unrestricted autonomy or performance outside the tested environments.
