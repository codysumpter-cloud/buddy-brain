from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from norn_memory_navigation_skills_score import (  # noqa: E402
    NornMemoryNavigationSkillsScoreError,
    score_norn_memory_navigation_skills_receipt,
)


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _receipt() -> dict[str, object]:
    value: dict[str, object] = {
        "claim_boundary": "Bounded memory, navigation and skill behaviors only.",
        "failed_count": 0,
        "measurements": {
            "autobiographical_recall": {
                "match_score": 0.533466533466534,
                "retrievals": 1,
                "selected_target": "red_ball",
            },
            "hierarchical_skill": {
                "expanded_steps": 3,
                "host_validated": True,
                "learned": True,
                "proposal_count": 1,
                "reliability": 0.8,
            },
            "persistence": {
                "episodes": 1,
                "facts": 1,
                "restored": True,
                "rooms": 1,
                "skills": 1,
            },
            "semantic_knowledge": {
                "confidence_before": 0.6192,
                "contradictions": 1,
                "object_after_weak_contradiction": True,
                "object_before": True,
                "retained_confidence": 0.564895969258655,
            },
            "skill_adaptation": {
                "failed_executions": 1,
                "reliability_after": 0.666666666666667,
                "reliability_before": 0.8,
            },
            "spatial_routing": {
                "host_validated": True,
                "route_rooms": ["hall", "garden"],
                "steps": 2,
            },
            "stack_integration": {
                "episode_id": "episode_1",
                "fact_confidence": 0.405,
                "mapped_rooms": 1,
                "memory_count": 1,
            },
        },
        "passed": True,
        "passed_count": 7,
        "receipt_sha256": "",
        "scenario_count": 7,
        "schema": "prismtek-norn-memory-navigation-skills-receipt-v1",
    }
    value["receipt_sha256"] = _digest(
        {key: item for key, item in value.items() if key != "receipt_sha256"}
    )
    return value


def _rehash(receipt: dict[str, object]) -> None:
    receipt["receipt_sha256"] = _digest(
        {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    )


class NornMemoryNavigationSkillsScoreTests(unittest.TestCase):
    def test_exact_green_receipt_scores_one_hundred(self) -> None:
        score = score_norn_memory_navigation_skills_receipt(_receipt())
        self.assertTrue(score["passed"])
        self.assertEqual(score["score"], 100)
        self.assertEqual(score["readiness"], "green")
        self.assertEqual(len(score["judgments"]), 7)

    def test_wrong_autobiographical_memory_fails_independently(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        memory = measurements["autobiographical_recall"]
        assert isinstance(memory, dict)
        memory["selected_target"] = "berry"
        _rehash(receipt)
        score = score_norn_memory_navigation_skills_receipt(receipt)
        self.assertFalse(score["passed"])
        self.assertEqual(score["score"], 85)

    def test_weak_rumor_cannot_overwrite_supported_fact(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        semantic = measurements["semantic_knowledge"]
        assert isinstance(semantic, dict)
        semantic["object_after_weak_contradiction"] = False
        semantic["retained_confidence"] = 0.20
        _rehash(receipt)
        score = score_norn_memory_navigation_skills_receipt(receipt)
        judgment = next(item for item in score["judgments"] if item["id"] == "semantic_knowledge")
        self.assertFalse(score["passed"])
        self.assertFalse(judgment["passed"])

    def test_dangerous_shortcut_cannot_claim_safe_routing(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        spatial = measurements["spatial_routing"]
        assert isinstance(spatial, dict)
        spatial["route_rooms"] = ["garden"]
        spatial["steps"] = 1
        _rehash(receipt)
        score = score_norn_memory_navigation_skills_receipt(receipt)
        judgment = next(item for item in score["judgments"] if item["id"] == "spatial_routing")
        self.assertFalse(score["passed"])
        self.assertFalse(judgment["passed"])

    def test_unlearned_or_unvalidated_skill_fails(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        skill = measurements["hierarchical_skill"]
        assert isinstance(skill, dict)
        skill["learned"] = False
        skill["host_validated"] = False
        _rehash(receipt)
        score = score_norn_memory_navigation_skills_receipt(receipt)
        judgment = next(item for item in score["judgments"] if item["id"] == "hierarchical_skill")
        self.assertFalse(score["passed"])
        self.assertFalse(judgment["passed"])

    def test_failed_execution_must_reduce_reliability(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        adaptation = measurements["skill_adaptation"]
        assert isinstance(adaptation, dict)
        adaptation["reliability_after"] = 0.8
        _rehash(receipt)
        score = score_norn_memory_navigation_skills_receipt(receipt)
        judgment = next(item for item in score["judgments"] if item["id"] == "skill_adaptation")
        self.assertFalse(score["passed"])
        self.assertFalse(judgment["passed"])

    def test_incomplete_persistence_fails(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        persistence = measurements["persistence"]
        assert isinstance(persistence, dict)
        persistence["skills"] = 0
        _rehash(receipt)
        score = score_norn_memory_navigation_skills_receipt(receipt)
        judgment = next(item for item in score["judgments"] if item["id"] == "persistence")
        self.assertFalse(score["passed"])
        self.assertFalse(judgment["passed"])

    def test_runtime_summary_disagreement_prevents_green(self) -> None:
        receipt = _receipt()
        receipt["passed_count"] = 6
        receipt["failed_count"] = 1
        _rehash(receipt)
        score = score_norn_memory_navigation_skills_receipt(receipt)
        self.assertEqual(score["score"], 100)
        self.assertFalse(score["runtime_summary_consistent"])
        self.assertFalse(score["passed"])

    def test_missing_measurement_is_rejected(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        del measurements["spatial_routing"]
        _rehash(receipt)
        with self.assertRaisesRegex(NornMemoryNavigationSkillsScoreError, "missing required"):
            score_norn_memory_navigation_skills_receipt(receipt)

    def test_payload_tampering_is_rejected(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        persistence = measurements["persistence"]
        assert isinstance(persistence, dict)
        persistence["restored"] = False
        with self.assertRaisesRegex(NornMemoryNavigationSkillsScoreError, "hash mismatch"):
            score_norn_memory_navigation_skills_receipt(receipt)

    def test_scoring_is_deterministic_and_non_mutating(self) -> None:
        receipt = _receipt()
        before = copy.deepcopy(receipt)
        first = score_norn_memory_navigation_skills_receipt(receipt)
        second = score_norn_memory_navigation_skills_receipt(receipt)
        self.assertEqual(first, second)
        self.assertEqual(receipt, before)


if __name__ == "__main__":
    unittest.main()
