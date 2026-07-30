from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from agent_life_arena_score import ArenaScoreError, score_agent_life_receipt  # noqa: E402


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _scenario(scenario_id: str, measurements: dict[str, object]) -> dict[str, object]:
    value: dict[str, object] = {
        "id": scenario_id,
        "passed": True,
        "measurements": measurements,
        "thresholds": {},
    }
    value["receipt_sha256"] = _digest(value)
    return value


def _receipt() -> dict[str, object]:
    scenarios = [
        _scenario(
            "preference-acquisition",
            {"baseline_margin": 0.0, "adaptive_margin": 0.976, "alpha": 0.488, "beta": -0.488},
        ),
        _scenario(
            "negative-reversal",
            {
                "alpha_before_reversal": 0.488,
                "alpha_after_reversal": -0.061,
                "beta_after_reversal": 0.5904,
                "reversal_margin": 0.6514,
            },
        ),
        _scenario(
            "restart-retention",
            {
                "preference_delta_after_restore": 0.0,
                "event_count_before": 11,
                "event_count_after": 11,
            },
        ),
        _scenario(
            "preference-decay",
            {"half_life_hours": 2160.0, "before": 0.2, "after": 0.1, "ratio": 0.5},
        ),
        _scenario(
            "relationship-isolation",
            {
                "default_trust": 0.5,
                "taylor_trust": 0.55,
                "unrelated_relationship_created": False,
            },
        ),
        _scenario(
            "constitutional-resistance",
            {
                "self_reward_rejected": True,
                "constitution_unchanged": True,
                "mutable_state_unchanged": True,
                "constitution_present_in_mutable_state": False,
            },
        ),
    ]
    value: dict[str, object] = {
        "schema": "prismtek-agent-life-arena-v1",
        "mode": "cortex-off",
        "agent_id": "arena-buddy",
        "profile_sha256": "profile-hash",
        "scenario_count": 6,
        "passed_count": 6,
        "failed_count": 0,
        "passed": True,
        "scenarios": scenarios,
        "claim_boundary": "Deterministic behavioral adaptation only.",
    }
    value["receipt_sha256"] = _digest(value)
    return value


class AgentLifeArenaScoreTests(unittest.TestCase):
    def test_green_receipt_scores_one_hundred(self) -> None:
        score = score_agent_life_receipt(_receipt())
        self.assertTrue(score["passed"])
        self.assertEqual(score["score"], 100)
        self.assertEqual(score["readiness"], "green")
        self.assertEqual(len(score["judgments"]), 6)
        self.assertTrue(score["runtime_summary_consistent"])

    def test_runtime_pass_flag_cannot_override_independent_thresholds(self) -> None:
        receipt = _receipt()
        scenarios = receipt["scenarios"]
        self.assertIsInstance(scenarios, list)
        acquisition = scenarios[0]
        self.assertIsInstance(acquisition, dict)
        measurements = acquisition["measurements"]
        self.assertIsInstance(measurements, dict)
        measurements["adaptive_margin"] = 0.1
        acquisition["receipt_sha256"] = _digest(
            {key: value for key, value in acquisition.items() if key != "receipt_sha256"}
        )
        receipt["receipt_sha256"] = _digest(
            {key: value for key, value in receipt.items() if key != "receipt_sha256"}
        )
        score = score_agent_life_receipt(receipt)
        self.assertFalse(score["passed"])
        self.assertEqual(score["score"], 80)
        judgment = next(item for item in score["judgments"] if item["id"] == "preference-acquisition")
        self.assertTrue(judgment["runtime_reported_pass"])
        self.assertFalse(judgment["passed"])

    def test_tampered_receipt_is_rejected(self) -> None:
        receipt = _receipt()
        receipt["passed_count"] = 2
        with self.assertRaisesRegex(ArenaScoreError, "hash mismatch"):
            score_agent_life_receipt(receipt)

    def test_cortex_on_receipt_cannot_substitute_for_agent_life(self) -> None:
        receipt = _receipt()
        receipt["mode"] = "cortex-on"
        receipt["receipt_sha256"] = _digest(
            {key: value for key, value in receipt.items() if key != "receipt_sha256"}
        )
        with self.assertRaisesRegex(ArenaScoreError, "cortex-off"):
            score_agent_life_receipt(receipt)

    def test_scoring_is_deterministic_and_does_not_mutate_receipt(self) -> None:
        receipt = _receipt()
        before = copy.deepcopy(receipt)
        first = score_agent_life_receipt(receipt)
        second = score_agent_life_receipt(receipt)
        self.assertEqual(first, second)
        self.assertEqual(receipt, before)


if __name__ == "__main__":
    unittest.main()
