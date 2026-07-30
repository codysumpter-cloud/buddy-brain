# Independent modern Norn cognition scoring

Buddy Brain evaluates `prismtek-norn-modern-cognition-receipt-v1` evidence produced by the Prismtek Buddy Core Godot runtime.

The game cannot establish success by setting `passed: true`. This scorer recomputes the complete SHA-256 receipt, requires exactly the seven supported measurement domains and applies thresholds owned outside the game repository.

## Scored domains

| Domain | Independent requirement | Weight |
| --- | --- | ---: |
| Delayed temporal credit | Exactly two actions receive credit; the recent action is at least `0.20`; the earlier cause remains positive but lower, with an early/recent ratio between `0.60` and `0.85` | 15 |
| Learning-progress curiosity | The learnable stimulus scores at least `0.30`, uncontrollable noise stays at or below `0.15`, the selection margin is at least `0.20`, and both learning progress and noise penalty are active | 15 |
| Development | Infant language plasticity exceeds adult plasticity by at least `0.25`; adolescent causal plasticity exceeds infant causal plasticity by at least `0.30`; high hunger selects an ecological curriculum | 15 |
| Predictive planning | Exactly two unique food/rest steps are selected, at least six futures are expanded and every step preserves host validation | 15 |
| Cultural learning | Learning is refused without contact; observed skill stays below the demonstrated transfer bound; the bound stays under `85%` of teacher competence; the teacher remains more skilled | 15 |
| Cortex containment | Valid advice is accepted, while an invented target and an authority-escape request are both rejected | 15 |
| Persistence | Restore succeeds with at least one causal model, one sleep-consolidation cycle and a positive retained prediction of at least `0.15` | 10 |

All independent judgments and the game summary must agree for a green `100/100` result.

## Adversarial tests

The scorer rejects or independently fails:

- modified payloads whose SHA-256 no longer matches;
- equal temporal credit disguised as a green runtime result;
- random noise outranking a learnable stimulus;
- cultural transfer exceeding teacher-owned knowledge;
- a cortex authority escape that the runtime reports as acceptable;
- missing or unknown measurement domains;
- game summary counts that disagree with the independently judged evidence.

The scorer is deterministic and does not mutate the supplied receipt.

## Claim boundary

A green score establishes the seven measured software behaviors for the exact content-addressed receipt. It does not establish consciousness, subjective experience, unrestricted intelligence, human-equivalent social cognition, or performance outside the tested environments.
