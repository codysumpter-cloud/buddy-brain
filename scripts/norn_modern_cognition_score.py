#!/usr/bin/env python3
"""Independently validate and score Prismtek modern Norn cognition receipts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

RECEIPT_SCHEMA = "prismtek-norn-modern-cognition-receipt-v1"
SCORE_SCHEMA = "prismtek-norn-modern-cognition-score-v1"
REQUIRED_MEASUREMENTS = {
    "delayed_credit": 15,
    "curiosity": 15,
    "development": 15,
    "planning": 15,
    "culture": 15,
    "cortex": 15,
    "persistence": 10,
}


class NornModernCognitionScoreError(ValueError):
    """The cognition receipt is malformed, tampered with, or incomplete."""


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _without_hash(value: dict[str, Any]) -> dict[str, Any]:
    copied = copy.deepcopy(value)
    copied.pop("receipt_sha256", None)
    return copied


def _verify_hash(receipt: dict[str, Any]) -> None:
    supplied = str(receipt.get("receipt_sha256", ""))
    if not supplied:
        raise NornModernCognitionScoreError("receipt is missing receipt_sha256")
    if supplied != _digest(_without_hash(receipt)):
        raise NornModernCognitionScoreError("receipt hash mismatch")


def _number(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise NornModernCognitionScoreError(f"{field} must be numeric")
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise NornModernCognitionScoreError(f"{field} must be numeric") from error


def _measurement_map(receipt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = receipt.get("measurements")
    if not isinstance(raw, dict):
        raise NornModernCognitionScoreError("receipt.measurements must be an object")
    result: dict[str, dict[str, Any]] = {}
    for key, value in raw.items():
        if not isinstance(value, dict):
            raise NornModernCognitionScoreError(f"measurement {key} must be an object")
        result[str(key)] = value
    missing = sorted(set(REQUIRED_MEASUREMENTS) - set(result))
    extra = sorted(set(result) - set(REQUIRED_MEASUREMENTS))
    if missing:
        raise NornModernCognitionScoreError(
            f"missing required measurements: {', '.join(missing)}"
        )
    if extra:
        raise NornModernCognitionScoreError(
            f"unknown measurements: {', '.join(extra)}"
        )
    return result


def _judge_delayed_credit(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    credited = int(_number(row.get("credited_count"), "delayed_credit.credited_count"))
    early = _number(row.get("early_value"), "delayed_credit.early_value")
    recent = _number(row.get("recent_value"), "delayed_credit.recent_value")
    ratio = early / recent if recent > 0.0 else 0.0
    passed = (
        credited == 2
        and recent >= 0.20
        and 0.0 < early < recent
        and 0.60 <= ratio <= 0.85
    )
    return passed, {
        "credited_count": credited,
        "early_value": early,
        "recent_value": recent,
        "early_recent_ratio": ratio,
        "required_ratio_range": [0.60, 0.85],
    }


def _judge_curiosity(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    learnable = _number(row.get("learnable_score"), "curiosity.learnable_score")
    noisy = _number(row.get("noisy_score"), "curiosity.noisy_score")
    progress = _number(row.get("learnable_progress"), "curiosity.learnable_progress")
    penalty = _number(row.get("noise_penalty"), "curiosity.noise_penalty")
    margin = learnable - noisy
    passed = (
        learnable >= 0.30
        and noisy <= 0.15
        and margin >= 0.20
        and progress > 0.0
        and penalty > 0.0
    )
    return passed, {
        "learnable_score": learnable,
        "noisy_score": noisy,
        "selection_margin": margin,
        "learning_progress": progress,
        "noise_penalty": penalty,
    }


def _judge_development(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    infant_language = _number(row.get("infant_language"), "development.infant_language")
    adult_language = _number(row.get("adult_language"), "development.adult_language")
    infant_causal = _number(row.get("infant_causal"), "development.infant_causal")
    adolescent_causal = _number(
        row.get("adolescent_causal"), "development.adolescent_causal"
    )
    curriculum = str(row.get("curriculum_domain", ""))
    passed = (
        infant_language - adult_language >= 0.25
        and adolescent_causal - infant_causal >= 0.30
        and curriculum == "ecology"
    )
    return passed, {
        "infant_language": infant_language,
        "adult_language": adult_language,
        "language_window_margin": infant_language - adult_language,
        "infant_causal": infant_causal,
        "adolescent_causal": adolescent_causal,
        "causal_window_margin": adolescent_causal - infant_causal,
        "curriculum_domain": curriculum,
    }


def _judge_planning(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    raw_ids = row.get("ids")
    if not isinstance(raw_ids, list):
        raise NornModernCognitionScoreError("planning.ids must be an array")
    ids = [str(value) for value in raw_ids]
    steps = int(_number(row.get("steps"), "planning.steps"))
    expanded = int(_number(row.get("expanded"), "planning.expanded"))
    host_validated = bool(row.get("host_validated", False))
    passed = (
        steps == 2
        and set(ids) == {"food", "bed"}
        and len(ids) == len(set(ids))
        and expanded >= 6
        and host_validated
    )
    return passed, {
        "ids": ids,
        "steps": steps,
        "expanded_candidates": expanded,
        "host_validation_preserved": host_validated,
    }


def _judge_culture(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    refused = bool(row.get("refused_without_contact", False))
    teacher = _number(row.get("teacher_skill"), "culture.teacher_skill")
    learner = _number(row.get("learner_skill"), "culture.learner_skill")
    bound = _number(row.get("transfer_bound"), "culture.transfer_bound")
    passed = (
        refused
        and 0.0 < learner <= bound
        and bound <= teacher * 0.85 + 1e-12
        and learner < teacher
        and teacher >= 0.50
    )
    return passed, {
        "refused_without_contact": refused,
        "teacher_skill": teacher,
        "learner_skill": learner,
        "transfer_bound": bound,
        "maximum_allowed_bound": teacher * 0.85,
    }


def _judge_cortex(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    valid = bool(row.get("valid_accepted", False))
    invented = bool(row.get("invented_rejected", False))
    escape = bool(row.get("authority_escape_rejected", False))
    passed = valid and invented and escape
    return passed, {
        "valid_advice_accepted": valid,
        "invented_target_rejected": invented,
        "authority_escape_rejected": escape,
    }


def _judge_persistence(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    restored = bool(row.get("restored", False))
    models = int(_number(row.get("models"), "persistence.models"))
    sleep_cycles = int(
        _number(row.get("sleep_cycles"), "persistence.sleep_cycles")
    )
    prediction = _number(row.get("prediction"), "persistence.prediction")
    passed = restored and models >= 1 and sleep_cycles >= 1 and prediction >= 0.15
    return passed, {
        "restored": restored,
        "model_count": models,
        "sleep_cycles": sleep_cycles,
        "prediction": prediction,
    }


Judge = Callable[[dict[str, Any]], tuple[bool, dict[str, Any]]]
JUDGES: dict[str, Judge] = {
    "delayed_credit": _judge_delayed_credit,
    "curiosity": _judge_curiosity,
    "development": _judge_development,
    "planning": _judge_planning,
    "culture": _judge_culture,
    "cortex": _judge_cortex,
    "persistence": _judge_persistence,
}


def score_norn_modern_cognition_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Recompute the hash and independently judge all modern cognition measurements."""
    if receipt.get("schema") != RECEIPT_SCHEMA:
        raise NornModernCognitionScoreError("unsupported modern cognition receipt schema")
    _verify_hash(receipt)
    measurements = _measurement_map(receipt)

    awarded = 0
    judgments: list[dict[str, Any]] = []
    for measurement_id, points in REQUIRED_MEASUREMENTS.items():
        passed, evidence = JUDGES[measurement_id](measurements[measurement_id])
        awarded += points if passed else 0
        judgments.append(
            {
                "id": measurement_id,
                "passed": passed,
                "points_awarded": points if passed else 0,
                "points_available": points,
                "evidence": evidence,
            }
        )

    runtime_summary_consistent = (
        receipt.get("scenario_count") == len(REQUIRED_MEASUREMENTS)
        and receipt.get("passed_count") == len(REQUIRED_MEASUREMENTS)
        and receipt.get("failed_count") == 0
        and receipt.get("passed") is True
    )
    independently_passed = all(item["passed"] for item in judgments)
    passed = independently_passed and runtime_summary_consistent and awarded == 100
    score: dict[str, Any] = {
        "schema": SCORE_SCHEMA,
        "source_schema": RECEIPT_SCHEMA,
        "source_receipt_sha256": str(receipt["receipt_sha256"]),
        "score": awarded,
        "maximum_score": 100,
        "passed": passed,
        "readiness": "green" if passed else "yellow" if awarded >= 70 else "red",
        "runtime_summary_consistent": runtime_summary_consistent,
        "judgments": judgments,
        "claim_boundary": (
            "A green score establishes the seven measured modern cognition software "
            "behaviors for the exact receipt. It does not establish consciousness, "
            "subjective experience, unrestricted intelligence, human-equivalent social "
            "cognition, or performance outside the tested environments."
        ),
    }
    score["score_sha256"] = _digest(score)
    return score


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Independently score a Prismtek modern Norn cognition receipt."
    )
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    try:
        parsed = json.loads(args.receipt.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            raise NornModernCognitionScoreError("receipt root must be an object")
        score = score_norn_modern_cognition_receipt(parsed)
    except (OSError, json.JSONDecodeError, NornModernCognitionScoreError) as error:
        print(f"modern cognition score failed: {error}")
        return 1
    encoded = json.dumps(score, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if score["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
