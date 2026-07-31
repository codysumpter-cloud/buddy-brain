from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from buddy_life_stochastic_score import (  # noqa: E402
    LEGACY_RECEIPT_SCHEMA,
    RECEIPT_SCHEMA,
    BuddyLifeStochasticScoreError,
    score_buddy_life_stochastic_receipt,
)


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _reseal(receipt: dict[str, object]) -> None:
    """Re-stamp the receipt hash after editing it, the way the runtime stamps it."""
    receipt.pop("receipt_sha256", None)
    receipt["receipt_sha256"] = _digest(receipt)


def _scenario(scenario_id: str, measurements: dict[str, object]) -> dict[str, object]:
    value: dict[str, object] = {
        "id": scenario_id,
        "passed": True,
        "measurements": measurements,
    }
    value["receipt_sha256"] = _digest(value)
    return value


def _receipt() -> dict[str, object]:
    scenarios = [
        _scenario(
            "noisy-adaptation",
            {
                "acquisition_rate": 1.0,
                "acquisition_successes": 32,
                "minimum_reversal_margin": 0.85706015960603,
                "noise_probability": 0.15,
                "reversal_rate": 1.0,
                "reversal_successes": 32,
                "trials": 32,
            },
        ),
        _scenario(
            "noisy-unseen-transfer",
            {
                "mean_category_value": 0.43821862396833,
                "minimum_category_value": 0.0809491382117401,
                "noise_probability": 0.15,
                "success_rate": 1.0,
                "successes": 32,
                "trials": 32,
            },
        ),
        _scenario(
            "random-need-planning",
            {
                "maximum_final_pressure": 0.0913552403450012,
                "success_rate": 1.0,
                "successes": 32,
                "trials": 32,
            },
        ),
        _scenario(
            "random-persistence",
            {
                "maximum_value_delta": 0.0,
                "success_rate": 1.0,
                "successes": 32,
                "trials": 32,
            },
        ),
        _scenario(
            "ecology-endurance-1000-ticks",
            {
                "extinctions": 0,
                "final_population": 39.3428781808381,
                "minimum_population": 9.26,
                "ticks": 1000,
                "total_harvest_nutrition": 3.0,
            },
        ),
        _scenario(
            "two-generation-lineage",
            {
                "child_id": "founder_a_child_1",
                "first_birth_count": 1,
                "first_conception": True,
                "grandchild_generation": 2,
                "grandchild_id": "founder_a_child_1_child_1",
                "grandchild_parent_count": 2,
                "second_birth_count": 1,
                "second_conception": True,
            },
        ),
    ]
    value: dict[str, object] = {
        "claim_boundary": "Seeded stochastic artificial-life robustness only.",
        "failed_count": 0,
        "mode": "cortex-off",
        "passed": True,
        "passed_count": 6,
        "scenario_count": 6,
        "scenarios": scenarios,
        "schema": "prismtek-norn-stochastic-arena-v1",
        "seed": 90210,
        "trials": 32,
    }
    value["receipt_sha256"] = _digest(value)
    return value


def _rehash(receipt: dict[str, object]) -> None:
    scenarios = receipt["scenarios"]
    assert isinstance(scenarios, list)
    for scenario in scenarios:
        assert isinstance(scenario, dict)
        scenario["receipt_sha256"] = _digest(
            {key: value for key, value in scenario.items() if key != "receipt_sha256"}
        )
    receipt["receipt_sha256"] = _digest(
        {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    )


class BuddyLifeStochasticScoreTests(unittest.TestCase):
    def test_current_and_legacy_receipt_schemas_both_score(self) -> None:
        """A published receipt keeps its old name; a fresh one carries the new one."""
        legacy = _receipt()
        self.assertEqual(legacy["schema"], LEGACY_RECEIPT_SCHEMA)
        legacy_score = score_buddy_life_stochastic_receipt(legacy)

        current = _receipt()
        current["schema"] = RECEIPT_SCHEMA
        _reseal(current)
        current_score = score_buddy_life_stochastic_receipt(current)

        self.assertTrue(legacy_score["passed"])
        self.assertTrue(current_score["passed"])
        self.assertEqual(legacy_score["score"], current_score["score"])
        self.assertEqual(legacy_score["source_schema"], LEGACY_RECEIPT_SCHEMA)
        self.assertEqual(current_score["source_schema"], RECEIPT_SCHEMA)

    def test_exact_green_receipt_scores_one_hundred(self) -> None:
        score = score_buddy_life_stochastic_receipt(_receipt())
        self.assertTrue(score["passed"])
        self.assertEqual(score["score"], 100)
        self.assertEqual(score["readiness"], "green")
        self.assertEqual(len(score["judgments"]), 6)

    def test_runtime_green_cannot_hide_weak_mean_transfer(self) -> None:
        receipt = _receipt()
        scenarios = receipt["scenarios"]
        assert isinstance(scenarios, list)
        transfer = scenarios[1]
        assert isinstance(transfer, dict)
        measurements = transfer["measurements"]
        assert isinstance(measurements, dict)
        measurements["mean_category_value"] = 0.10
        _rehash(receipt)
        score = score_buddy_life_stochastic_receipt(receipt)
        self.assertFalse(score["passed"])
        self.assertEqual(score["score"], 80)
        judgment = next(
            item for item in score["judgments"] if item["id"] == "noisy-unseen-transfer"
        )
        self.assertTrue(judgment["runtime_reported_pass"])
        self.assertFalse(judgment["passed"])

    def test_inconsistent_success_rate_is_rejected_by_judgment(self) -> None:
        receipt = _receipt()
        scenarios = receipt["scenarios"]
        assert isinstance(scenarios, list)
        adaptation = scenarios[0]
        assert isinstance(adaptation, dict)
        measurements = adaptation["measurements"]
        assert isinstance(measurements, dict)
        measurements["acquisition_successes"] = 20
        _rehash(receipt)
        score = score_buddy_life_stochastic_receipt(receipt)
        self.assertFalse(score["passed"])
        judgment = next(
            item for item in score["judgments"] if item["id"] == "noisy-adaptation"
        )
        self.assertFalse(judgment["passed"])

    def test_short_ecology_run_cannot_claim_endurance(self) -> None:
        receipt = _receipt()
        scenarios = receipt["scenarios"]
        assert isinstance(scenarios, list)
        ecology = scenarios[4]
        assert isinstance(ecology, dict)
        measurements = ecology["measurements"]
        assert isinstance(measurements, dict)
        measurements["ticks"] = 100
        _rehash(receipt)
        score = score_buddy_life_stochastic_receipt(receipt)
        self.assertFalse(score["passed"])

    def test_tampered_receipt_is_rejected(self) -> None:
        receipt = _receipt()
        receipt["seed"] = 7
        with self.assertRaisesRegex(BuddyLifeStochasticScoreError, "seed or trial count"):
            score_buddy_life_stochastic_receipt(receipt)

    def test_cortex_on_receipt_is_rejected(self) -> None:
        receipt = _receipt()
        receipt["mode"] = "cortex-on"
        _rehash(receipt)
        with self.assertRaisesRegex(BuddyLifeStochasticScoreError, "cortex-off"):
            score_buddy_life_stochastic_receipt(receipt)

    def test_scoring_is_deterministic_and_non_mutating(self) -> None:
        receipt = _receipt()
        before = copy.deepcopy(receipt)
        first = score_buddy_life_stochastic_receipt(receipt)
        second = score_buddy_life_stochastic_receipt(receipt)
        self.assertEqual(first, second)
        self.assertEqual(receipt, before)


if __name__ == "__main__":
    unittest.main()
