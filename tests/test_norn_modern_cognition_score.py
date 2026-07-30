from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from norn_modern_cognition_score import (  # noqa: E402
    NornModernCognitionScoreError,
    score_norn_modern_cognition_receipt,
)


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _receipt() -> dict[str, object]:
    value: dict[str, object] = {
        "claim_boundary": "Measured modern cognition software behaviors only.",
        "failed_count": 0,
        "measurements": {
            "cortex": {
                "authority_escape_rejected": True,
                "invented_rejected": True,
                "valid_accepted": True,
            },
            "culture": {
                "learner_skill": 0.291063118719517,
                "refused_without_contact": True,
                "teacher_skill": 0.840009000633526,
                "transfer_bound": 0.529205670399121,
            },
            "curiosity": {
                "learnable_progress": 0.314064128,
                "learnable_score": 0.471542225673367,
                "noise_penalty": 0.130969884352302,
                "noisy_score": 0.0555714986092216,
            },
            "delayed_credit": {
                "credited_count": 2,
                "early_value": 0.1584,
                "recent_value": 0.22,
            },
            "development": {
                "adolescent_causal": 1.0,
                "adult_language": 0.55,
                "curriculum_domain": "ecology",
                "infant_causal": 0.45,
                "infant_language": 1.0,
            },
            "persistence": {
                "models": 1,
                "prediction": 0.22,
                "restored": True,
                "sleep_cycles": 1,
            },
            "planning": {
                "expanded": 12,
                "host_validated": True,
                "ids": ["food", "bed"],
                "steps": 2,
            },
        },
        "passed": True,
        "passed_count": 7,
        "scenario_count": 7,
        "schema": "prismtek-norn-modern-cognition-receipt-v1",
    }
    value["receipt_sha256"] = _digest(value)
    return value


def _rehash(receipt: dict[str, object]) -> None:
    receipt["receipt_sha256"] = _digest(
        {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    )


class NornModernCognitionScoreTests(unittest.TestCase):
    def test_exact_green_receipt_scores_one_hundred(self) -> None:
        score = score_norn_modern_cognition_receipt(_receipt())
        self.assertTrue(score["passed"])
        self.assertEqual(score["score"], 100)
        self.assertEqual(score["readiness"], "green")
        self.assertEqual(len(score["judgments"]), 7)

    def test_equal_temporal_credit_cannot_hide_behind_green_summary(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        delayed = measurements["delayed_credit"]
        assert isinstance(delayed, dict)
        delayed["early_value"] = delayed["recent_value"]
        _rehash(receipt)
        score = score_norn_modern_cognition_receipt(receipt)
        self.assertFalse(score["passed"])
        self.assertEqual(score["score"], 85)
        judgment = next(item for item in score["judgments"] if item["id"] == "delayed_credit")
        self.assertFalse(judgment["passed"])

    def test_random_noise_cannot_win_curiosity(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        curiosity = measurements["curiosity"]
        assert isinstance(curiosity, dict)
        curiosity["noisy_score"] = 0.60
        _rehash(receipt)
        score = score_norn_modern_cognition_receipt(receipt)
        self.assertFalse(score["passed"])
        judgment = next(item for item in score["judgments"] if item["id"] == "curiosity")
        self.assertFalse(judgment["passed"])

    def test_unbounded_cultural_transfer_is_rejected(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        culture = measurements["culture"]
        assert isinstance(culture, dict)
        culture["transfer_bound"] = 0.90
        culture["learner_skill"] = 0.88
        _rehash(receipt)
        score = score_norn_modern_cognition_receipt(receipt)
        self.assertFalse(score["passed"])
        judgment = next(item for item in score["judgments"] if item["id"] == "culture")
        self.assertFalse(judgment["passed"])

    def test_cortex_authority_escape_must_be_rejected(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        cortex = measurements["cortex"]
        assert isinstance(cortex, dict)
        cortex["authority_escape_rejected"] = False
        _rehash(receipt)
        score = score_norn_modern_cognition_receipt(receipt)
        self.assertFalse(score["passed"])
        judgment = next(item for item in score["judgments"] if item["id"] == "cortex")
        self.assertFalse(judgment["passed"])

    def test_runtime_summary_disagreement_prevents_green(self) -> None:
        receipt = _receipt()
        receipt["passed_count"] = 6
        receipt["failed_count"] = 1
        _rehash(receipt)
        score = score_norn_modern_cognition_receipt(receipt)
        self.assertEqual(score["score"], 100)
        self.assertFalse(score["runtime_summary_consistent"])
        self.assertFalse(score["passed"])

    def test_missing_measurement_is_rejected(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        del measurements["planning"]
        _rehash(receipt)
        with self.assertRaisesRegex(NornModernCognitionScoreError, "missing required"):
            score_norn_modern_cognition_receipt(receipt)

    def test_payload_tampering_is_rejected(self) -> None:
        receipt = _receipt()
        measurements = receipt["measurements"]
        assert isinstance(measurements, dict)
        planning = measurements["planning"]
        assert isinstance(planning, dict)
        planning["host_validated"] = False
        with self.assertRaisesRegex(NornModernCognitionScoreError, "hash mismatch"):
            score_norn_modern_cognition_receipt(receipt)

    def test_scoring_is_deterministic_and_non_mutating(self) -> None:
        receipt = _receipt()
        before = copy.deepcopy(receipt)
        first = score_norn_modern_cognition_receipt(receipt)
        second = score_norn_modern_cognition_receipt(receipt)
        self.assertEqual(first, second)
        self.assertEqual(receipt, before)


if __name__ == "__main__":
    unittest.main()
