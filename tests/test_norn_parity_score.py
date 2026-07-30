from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from norn_parity_score import (  # noqa: E402
    NornParityScoreError,
    score_norn_parity_receipt,
)


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


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
            "object-learning-reversal",
            {
                "alpha_after_reversal": -0.843256201138953,
                "alpha_before_reversal": 0.695993328576,
                "beta_after_reversal": 0.843256201138953,
                "selected_after_acquisition": "alpha",
                "selected_after_reversal": "beta",
            },
        ),
        _scenario(
            "unseen-category-transfer",
            {
                "learned_food_category": 0.565611545776368,
                "novel_exact_history": 0.0,
                "selected_novel_subject": "novel_berry",
            },
        ),
        _scenario(
            "multi-step-need-planning",
            {
                "all_steps_require_host_validation": True,
                "plan_ids": ["warm_bed", "food_bowl", "toy_ball"],
                "projected_final_drives": {
                    "boredom": 0.0,
                    "hunger": 0.15,
                    "sleepiness": 0.0,
                },
                "steps": 3,
            },
        ),
        _scenario(
            "relationship-scoped-social-teaching",
            {
                "learner_strength": 0.0353889174493258,
                "learner_word": "berry",
                "rejected_without_contact": True,
                "transfer": 0.294907645411048,
            },
        ),
        _scenario(
            "ecology-driven-survival",
            {
                "food_resource": 0.439,
                "harvest_nutrition": 0.7,
                "selected_under_hunger": "species:glow_berry",
            },
        ),
        _scenario(
            "hereditary-lineage",
            {
                "birth_count": 1,
                "child_id": "aurora_child_1",
                "conceived": True,
                "generation": 1,
                "parent_count": 2,
            },
        ),
        _scenario(
            "learning-and-plan-persistence",
            {
                "category_value_after": 0.3409184768,
                "category_value_before": 0.3409184768,
                "plan_matches": True,
                "restored": True,
            },
        ),
    ]
    value: dict[str, object] = {
        "claim_boundary": "Deterministic artificial-life behaviors only.",
        "failed_count": 0,
        "mode": "cortex-off",
        "passed": True,
        "passed_count": 7,
        "scenario_count": 7,
        "scenarios": scenarios,
        "schema": "prismtek-norn-parity-arena-v1",
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


class NornParityScoreTests(unittest.TestCase):
    def test_exact_green_receipt_scores_one_hundred(self) -> None:
        score = score_norn_parity_receipt(_receipt())
        self.assertTrue(score["passed"])
        self.assertEqual(score["score"], 100)
        self.assertEqual(score["readiness"], "green")
        self.assertEqual(len(score["judgments"]), 7)

    def test_runtime_pass_flag_cannot_hide_weak_transfer(self) -> None:
        receipt = _receipt()
        scenarios = receipt["scenarios"]
        assert isinstance(scenarios, list)
        transfer = scenarios[1]
        assert isinstance(transfer, dict)
        measurements = transfer["measurements"]
        assert isinstance(measurements, dict)
        measurements["learned_food_category"] = 0.05
        _rehash(receipt)
        score = score_norn_parity_receipt(receipt)
        self.assertFalse(score["passed"])
        self.assertEqual(score["score"], 85)
        judgment = next(
            item for item in score["judgments"] if item["id"] == "unseen-category-transfer"
        )
        self.assertTrue(judgment["runtime_reported_pass"])
        self.assertFalse(judgment["passed"])

    def test_runtime_pass_flag_cannot_hide_unbounded_social_transfer(self) -> None:
        receipt = _receipt()
        scenarios = receipt["scenarios"]
        assert isinstance(scenarios, list)
        social = scenarios[3]
        assert isinstance(social, dict)
        measurements = social["measurements"]
        assert isinstance(measurements, dict)
        measurements["transfer"] = 1.0
        measurements["learner_strength"] = 0.9
        _rehash(receipt)
        score = score_norn_parity_receipt(receipt)
        self.assertFalse(score["passed"])
        judgment = next(
            item
            for item in score["judgments"]
            if item["id"] == "relationship-scoped-social-teaching"
        )
        self.assertFalse(judgment["passed"])

    def test_tampered_receipt_is_rejected(self) -> None:
        receipt = _receipt()
        receipt["passed_count"] = 2
        with self.assertRaisesRegex(NornParityScoreError, "hash mismatch"):
            score_norn_parity_receipt(receipt)

    def test_cortex_on_receipt_is_rejected(self) -> None:
        receipt = _receipt()
        receipt["mode"] = "cortex-on"
        _rehash(receipt)
        with self.assertRaisesRegex(NornParityScoreError, "cortex-off"):
            score_norn_parity_receipt(receipt)

    def test_scoring_is_deterministic_and_non_mutating(self) -> None:
        receipt = _receipt()
        before = copy.deepcopy(receipt)
        first = score_norn_parity_receipt(receipt)
        second = score_norn_parity_receipt(receipt)
        self.assertEqual(first, second)
        self.assertEqual(receipt, before)


if __name__ == "__main__":
    unittest.main()
