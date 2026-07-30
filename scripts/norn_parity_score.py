#!/usr/bin/env python3
"""Independently validate and score Prismtek cortex-off Norn parity receipts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

RECEIPT_SCHEMA = "prismtek-norn-parity-arena-v1"
SCORE_SCHEMA = "prismtek-norn-parity-score-v1"
REQUIRED_SCENARIOS = {
    "object-learning-reversal": 20,
    "unseen-category-transfer": 15,
    "multi-step-need-planning": 15,
    "relationship-scoped-social-teaching": 15,
    "ecology-driven-survival": 15,
    "hereditary-lineage": 10,
    "learning-and-plan-persistence": 10,
}


class NornParityScoreError(ValueError):
    """The game receipt is malformed, tampered with, or incomplete."""


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _without_hash(value: dict[str, Any]) -> dict[str, Any]:
    copied = copy.deepcopy(value)
    copied.pop("receipt_sha256", None)
    return copied


def _verify_hash(payload: dict[str, Any], label: str) -> None:
    supplied = str(payload.get("receipt_sha256", ""))
    if not supplied:
        raise NornParityScoreError(f"{label} is missing receipt_sha256")
    expected = _digest(_without_hash(payload))
    if supplied != expected:
        raise NornParityScoreError(f"{label} hash mismatch")


def _number(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise NornParityScoreError(f"{field} must be numeric")
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise NornParityScoreError(f"{field} must be numeric") from error


def _measurement(scenario: dict[str, Any], name: str) -> Any:
    measurements = scenario.get("measurements")
    if not isinstance(measurements, dict) or name not in measurements:
        raise NornParityScoreError(
            f"scenario {scenario.get('id')} is missing measurement {name}"
        )
    return measurements[name]


def _scenario_map(receipt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = receipt.get("scenarios")
    if not isinstance(raw, list):
        raise NornParityScoreError("receipt.scenarios must be an array")
    result: dict[str, dict[str, Any]] = {}
    for index, scenario in enumerate(raw):
        if not isinstance(scenario, dict):
            raise NornParityScoreError(f"scenario[{index}] must be an object")
        scenario_id = str(scenario.get("id", ""))
        if not scenario_id:
            raise NornParityScoreError(f"scenario[{index}] requires id")
        if scenario_id in result:
            raise NornParityScoreError(f"duplicate scenario {scenario_id}")
        _verify_hash(scenario, f"scenario {scenario_id}")
        result[scenario_id] = scenario
    missing = sorted(set(REQUIRED_SCENARIOS) - set(result))
    extra = sorted(set(result) - set(REQUIRED_SCENARIOS))
    if missing:
        raise NornParityScoreError(f"missing required scenarios: {', '.join(missing)}")
    if extra:
        raise NornParityScoreError(f"unknown scenarios: {', '.join(extra)}")
    return result


def _judge_reversal(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    selected_before = str(_measurement(scenario, "selected_after_acquisition"))
    selected_after = str(_measurement(scenario, "selected_after_reversal"))
    alpha_before = _number(_measurement(scenario, "alpha_before_reversal"), "alpha_before_reversal")
    alpha_after = _number(_measurement(scenario, "alpha_after_reversal"), "alpha_after_reversal")
    beta_after = _number(_measurement(scenario, "beta_after_reversal"), "beta_after_reversal")
    passed = (
        selected_before == "alpha"
        and selected_after == "beta"
        and alpha_before >= 0.5
        and alpha_after <= -0.5
        and beta_after >= 0.5
        and alpha_after < alpha_before
    )
    return passed, {
        "selected_before": selected_before,
        "selected_after": selected_after,
        "alpha_before": alpha_before,
        "alpha_after": alpha_after,
        "beta_after": beta_after,
        "required_positive_magnitude": 0.5,
        "required_negative_magnitude": -0.5,
    }


def _judge_transfer(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    category = _number(_measurement(scenario, "learned_food_category"), "learned_food_category")
    exact = _number(_measurement(scenario, "novel_exact_history"), "novel_exact_history")
    selected = str(_measurement(scenario, "selected_novel_subject"))
    passed = category >= 0.25 and abs(exact) <= 1e-12 and selected == "novel_berry"
    return passed, {
        "learned_category_value": category,
        "novel_exact_history": exact,
        "selected_novel_subject": selected,
        "minimum_category_value": 0.25,
    }


def _judge_planning(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    raw_ids = _measurement(scenario, "plan_ids")
    if not isinstance(raw_ids, list):
        raise NornParityScoreError("plan_ids must be an array")
    ids = [str(value) for value in raw_ids]
    steps = int(_number(_measurement(scenario, "steps"), "steps"))
    host_validated = bool(_measurement(scenario, "all_steps_require_host_validation"))
    final_drives = _measurement(scenario, "projected_final_drives")
    if not isinstance(final_drives, dict):
        raise NornParityScoreError("projected_final_drives must be an object")
    hunger = _number(final_drives.get("hunger"), "projected_final_drives.hunger")
    sleepiness = _number(final_drives.get("sleepiness"), "projected_final_drives.sleepiness")
    boredom = _number(final_drives.get("boredom"), "projected_final_drives.boredom")
    required = {"food_bowl", "warm_bed", "toy_ball"}
    passed = (
        steps == 3
        and set(ids) == required
        and len(ids) == len(set(ids))
        and host_validated
        and hunger <= 0.25
        and sleepiness <= 0.1
        and boredom <= 0.1
    )
    return passed, {
        "plan_ids": ids,
        "steps": steps,
        "host_validation_preserved": host_validated,
        "final_drives": {
            "hunger": hunger,
            "sleepiness": sleepiness,
            "boredom": boredom,
        },
    }


def _judge_social_teaching(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    rejected_without_contact = bool(_measurement(scenario, "rejected_without_contact"))
    transfer = _number(_measurement(scenario, "transfer"), "transfer")
    learner_strength = _number(_measurement(scenario, "learner_strength"), "learner_strength")
    learner_word = str(_measurement(scenario, "learner_word"))
    passed = (
        rejected_without_contact
        and 0.0 < transfer <= 0.85
        and 0.0 < learner_strength <= transfer
        and learner_word == "berry"
    )
    return passed, {
        "rejected_without_contact": rejected_without_contact,
        "transfer": transfer,
        "learner_strength": learner_strength,
        "learner_word": learner_word,
        "maximum_transfer": 0.85,
    }


def _judge_ecology(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    food = _number(_measurement(scenario, "food_resource"), "food_resource")
    selected = str(_measurement(scenario, "selected_under_hunger"))
    nutrition = _number(_measurement(scenario, "harvest_nutrition"), "harvest_nutrition")
    passed = food > 0.0 and selected == "species:glow_berry" and nutrition >= 0.5
    return passed, {
        "food_resource": food,
        "selected_under_hunger": selected,
        "harvest_nutrition": nutrition,
        "minimum_nutrition": 0.5,
    }


def _judge_lineage(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    conceived = bool(_measurement(scenario, "conceived"))
    births = int(_number(_measurement(scenario, "birth_count"), "birth_count"))
    child_id = str(_measurement(scenario, "child_id"))
    generation = int(_number(_measurement(scenario, "generation"), "generation"))
    parents = int(_number(_measurement(scenario, "parent_count"), "parent_count"))
    passed = conceived and births == 1 and bool(child_id) and generation == 1 and parents == 2
    return passed, {
        "conceived": conceived,
        "birth_count": births,
        "child_id": child_id,
        "generation": generation,
        "parent_count": parents,
    }


def _judge_persistence(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    restored = bool(_measurement(scenario, "restored"))
    plan_matches = bool(_measurement(scenario, "plan_matches"))
    before = _number(_measurement(scenario, "category_value_before"), "category_value_before")
    after = _number(_measurement(scenario, "category_value_after"), "category_value_after")
    delta = abs(after - before)
    passed = restored and plan_matches and before > 0.0 and delta <= 1e-12
    return passed, {
        "restored": restored,
        "plan_matches": plan_matches,
        "category_value_before": before,
        "category_value_after": after,
        "restore_delta": delta,
        "maximum_restore_delta": 1e-12,
    }


Judge = Callable[[dict[str, Any]], tuple[bool, dict[str, Any]]]
JUDGES: dict[str, Judge] = {
    "object-learning-reversal": _judge_reversal,
    "unseen-category-transfer": _judge_transfer,
    "multi-step-need-planning": _judge_planning,
    "relationship-scoped-social-teaching": _judge_social_teaching,
    "ecology-driven-survival": _judge_ecology,
    "hereditary-lineage": _judge_lineage,
    "learning-and-plan-persistence": _judge_persistence,
}


def score_norn_parity_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Recompute hashes and independently judge every behavioral measurement."""
    if receipt.get("schema") != RECEIPT_SCHEMA:
        raise NornParityScoreError("unsupported Norn parity receipt schema")
    if receipt.get("mode") != "cortex-off":
        raise NornParityScoreError("Norn parity requires a cortex-off receipt")
    _verify_hash(receipt, "Norn parity receipt")
    scenarios = _scenario_map(receipt)

    awarded = 0
    judgments: list[dict[str, Any]] = []
    for scenario_id, points in REQUIRED_SCENARIOS.items():
        scenario = scenarios[scenario_id]
        passed, evidence = JUDGES[scenario_id](scenario)
        awarded += points if passed else 0
        judgments.append(
            {
                "id": scenario_id,
                "passed": passed,
                "points_awarded": points if passed else 0,
                "points_available": points,
                "runtime_reported_pass": bool(scenario.get("passed", False)),
                "runtime_receipt_sha256": str(scenario["receipt_sha256"]),
                "evidence": evidence,
            }
        )

    independently_passed = all(judgment["passed"] for judgment in judgments)
    runtime_summary_consistent = (
        receipt.get("scenario_count") == len(REQUIRED_SCENARIOS)
        and receipt.get("passed_count") == len(REQUIRED_SCENARIOS)
        and receipt.get("failed_count") == 0
        and receipt.get("passed") is True
    )
    passed = independently_passed and runtime_summary_consistent and awarded == 100
    score: dict[str, Any] = {
        "schema": SCORE_SCHEMA,
        "source_schema": RECEIPT_SCHEMA,
        "source_receipt_sha256": str(receipt["receipt_sha256"]),
        "mode": "cortex-off",
        "score": awarded,
        "maximum_score": 100,
        "passed": passed,
        "readiness": "green" if passed else "yellow" if awarded >= 70 else "red",
        "runtime_summary_consistent": runtime_summary_consistent,
        "judgments": judgments,
        "claim_boundary": (
            "A green score establishes the seven measured deterministic Norn-style "
            "artificial-life behaviors for this exact receipt. It does not establish "
            "consciousness, subjective feeling, unrestricted general intelligence, "
            "OpenC2E equivalence, or behavior outside the tested arena."
        ),
    }
    score["score_sha256"] = _digest(score)
    return score


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Independently score a Prismtek cortex-off Norn parity receipt."
    )
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    try:
        parsed = json.loads(args.receipt.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            raise NornParityScoreError("receipt must be a JSON object")
        score = score_norn_parity_receipt(parsed)
    except (NornParityScoreError, json.JSONDecodeError, OSError) as error:
        parser.error(str(error))
    rendered = json.dumps(score, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if score["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
