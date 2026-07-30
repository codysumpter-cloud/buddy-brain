# Stochastic Norn robustness scoring

Buddy Brain independently scores `prismtek-norn-stochastic-arena-v1` receipts produced by the cortex-off Prismtek Buddy Core runtime.

This layer complements the deterministic Norn parity score. It tests distributions and long-horizon behavior rather than repeating one fixture.

## Required evidence

The receipt must use seed `90210`, contain exactly 32 trials for repeated scenarios, pass SHA-256 verification, and include all six scenarios:

| Scenario | Independent requirement | Weight |
| --- | --- | ---: |
| Noisy adaptation | Acquisition and reversal each succeed in at least 90% of trials; success counts match rates; worst reversal margin is at least `0.40` under 15% outcome noise | 25 |
| Noisy unseen transfer | At least 90% of novel foods are selected; minimum category value stays positive; mean category value is at least `0.25` under 15% noise | 20 |
| Random need planning | All 32 plans succeed and maximum final drive pressure is at most `0.10` | 15 |
| Random persistence | All 32 restore trials reproduce the plan and category value with at most `1e-12` drift | 15 |
| Ecology endurance | The simulation reaches exactly 1,000 ticks with zero extinctions, a viable population, and confirmed harvest nutrition | 15 |
| Two-generation lineage | Two conceptions and births produce a distinct generation-two grandchild with two parents | 10 |

The game runtime's pass flags are recorded for audit but do not determine the independent judgment.

## Claim boundary

A green `100/100` score establishes the measured seeded robustness, 1,000-tick ecology endurance, and two-generation lineage for the exact receipt. It does not establish consciousness, unrestricted general intelligence, OpenC2E behavioral equivalence, unseeded performance, or behavior outside the tested distributions.
