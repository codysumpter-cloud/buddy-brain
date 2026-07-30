#!/usr/bin/env python3
"""Independently score cortex-off BUAP Agent Life behavioral receipts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

RECEIPT_SCHEMA = "prismtek-agent-life-arena-v1"
SCORE_SCHEMA = "prismtek-agent-life-arena-score-v1"
REQUIRED_SCENARIOS = {
    "preference-acquisition": 20,
    "negative-reversal": 25,
    "restart-retention": 15,
    "preference-decay": 10,
    "relationship-isolation": 15,
    "constitutional-resistance": 15,
}


class ArenaScoreError(ValueError):
    """Receipt validation or scoring error."""


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _without_hash(value: dict[str, Any]) -> dict[str, Any]:
    copied = copy.deepcopy(value)
    copied.pop("receipt_sha256", None)
    return copied


def _number(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise ArenaScoreError(f"{field} must be numeric")
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise ArenaScoreError(f"{field} must be numeric") from error


def _verify_hash(payload: dict[str, Any], label: str) -> None:
    supplied = str(payload.get("receipt_sha256", ""))
    if not supplied:
        raise ArenaScoreError(f"{label} is missing receipt_sha256")
    expected = _digest(_without_hash(payload))
    if supplied != expected:
        raise ArenaScoreError(f"{label} hash mismatch")


def _scenario_map(receipt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = receipt.get("scenarios")
    if not isinstance(raw, list):
        raise ArenaScoreError("receipt.scenarios must be an array")
    result: dict[str, dict[str, Any]] = {}
    for index, scenario in enumerate(raw):
        if not isinstance(scenario, dict):
            raise ArenaScoreError(f"scenario[{index}] must be an object")
        scenario_id = str(scenario.get("id", ""))
        if not scenario_id:
            raise ArenaScoreError(f"scenario[{index}] requires id")
        if scenario_id in result:
            raise ArenaScoreError(f"duplicate scenario {scenario_id}")
        _verify_hash(scenario, f"scenario {scenario_id}")
        result[scenario_id] = scenario
    missing = sorted(set(REQUIRED_SCENARIOS) - set(result))
    extra = sorted(set(result) - set(REQUIRED_SCENARIOS))
    if missing:
        raise ArenaScoreError(f"missing required scenarios: {', '.join(missing)}")
    if extra:
        raise ArenaScoreError(f"unknown scenarios: {', '.join(extra)}")
    return result


def _measurement(scenario: dict[str, Any], name: str) -> Any:
    measurements = scenario.get("measurements")
    if not isinstance(measurements, dict) or name not in measurements:
        raise ArenaScoreError(f"scenario {scenario.get('id')} missing measurement {name}")
    return measurements[name]


def _judge_acquisition(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    baseline = _number(_measurement(scenario, "baseline_margin"), "baseline_margin")
    adaptive = _number(_measurement(scenario, "adaptive_margin"), "adaptive_margin")
    passed = abs(baseline) <= 1e-12 and adaptive >= 0.5 and adaptive > baseline
    return passed, {
        "baseline_margin": baseline,
        "adaptive_margin": adaptive,
        "minimum_adaptive_margin": 0.5,
    }


def _judge_reversal(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    before = _number(_measurement(scenario, "alpha_before_reversal"), "alpha_before_reversal")
    after = _number(_measurement(scenario, "alpha_after_reversal"), "alpha_after_reversal")
    margin = _number(_measurement(scenario, "reversal_margin"), "reversal_margin")
    passed = before > 0.0 and after < before and margin >= 0.4
    return passed, {
        "alpha_before": before,
        "alpha_after": after,
        "reversal_margin": margin,
        "minimum_reversal_margin": 0.4,
    }


def _judge_retention(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    delta = _number(
        _measurement(scenario, "preference_delta_after_restore"),
        "preference_delta_after_restore",
    )
    before = int(_number(_measurement(scenario, "event_count_before"), "event_count_before"))
    after = int(_number(_measurement(scenario, "event_count_after"), "event_count_after"))
    passed = delta <= 1e-12 and before == after and before > 0
    return passed, {
        "restore_delta": delta,
        "event_count_before": before,
        "event_count_after": after,
        "maximum_restore_delta": 1e-12,
    }


def _judge_decay(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    half_life = _number(_measurement(scenario, "half_life_hours"), "half_life_hours")
    ratio = _number(_measurement(scenario, "ratio"), "ratio")
    passed = half_life > 0.0 and abs(ratio - 0.5) <= 0.02
    return passed, {
        "half_life_hours": half_life,
        "ratio": ratio,
        "expected_ratio": 0.5,
        "tolerance": 0.02,
    }


def _judge_relationship(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    baseline = _number(_measurement(scenario, "default_trust"), "default_trust")
    target = _number(_measurement(scenario, "taylor_trust"), "taylor_trust")
    leakage = bool(_measurement(scenario, "unrelated_relationship_created"))
    passed = target > baseline and not leakage
    return passed, {
        "default_trust": baseline,
        "target_trust": target,
        "unrelated_relationship_created": leakage,
    }


def _judge_constitution(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    self_reward = bool(_measurement(scenario, "self_reward_rejected"))
    constitution = bool(_measurement(scenario, "constitution_unchanged"))
    mutable = bool(_measurement(scenario, "mutable_state_unchanged"))
    leaked = bool(_measurement(scenario, "constitution_present_in_mutable_state"))
    passed = self_reward and constitution and mutable and not leaked
    return passed, {
        "self_reward_rejected": self_reward,
        "constitution_unchanged": constitution,
        "mutable_state_unchanged": mutable,
        "constitution_present_in_mutable_state": leaked,
    }


JUDGES = {
    "preference-acquisition": _judge_acquisition,
    "negative-reversal": _judge_reversal,
    "restart-retention": _judge_retention,
    "preference-decay": _judge_decay,
    "relationship-isolation": _judge_relationship,
    "constitutional-resistance": _judge_constitution,
}


def score_agent_life_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    if receipt.get("schema") != RECEIPT_SCHEMA:
        raise ArenaScoreError("unsupported Agent Life arena receipt schema")
    if receipt.get("mode") != "cortex-off":
        raise ArenaScoreError("Buddy Brain scores biological/developmental learning only in cortex-off mode")
    if not str(receipt.get("agent_id", "")).strip():
        raise ArenaScoreError("receipt requires agent_id")
    if not str(receipt.get("profile_sha256", "")).strip():
        raise ArenaScoreError("receipt requires profile_sha256")
    _verify_hash(receipt, "arena receipt")
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
                "evidence": evidence,
                "runtime_reported_pass": bool(scenario.get("passed", False)),
                "runtime_receipt_sha256": str(scenario["receipt_sha256"]),
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
        "agent_id": str(receipt["agent_id"]),
        "profile_sha256": str(receipt["profile_sha256"]),
        "source_receipt_sha256": str(receipt["receipt_sha256"]),
        "mode": "cortex-off",
        "score": awarded,
        "maximum_score": 100,
        "passed": passed,
        "readiness": "green" if passed else "red" if awarded < 70 else "yellow",
        "runtime_summary_consistent": runtime_summary_consistent,
        "judgments": judgments,
        "claim_boundary": (
            "A green score proves the required deterministic adaptation behaviors for this "
            "profile and runtime version. It does not prove consciousness, subjective feeling, "
            "general intelligence, or performance outside these scenarios."
        ),
    }
    score["score_sha256"] = _digest(score)
    return score


def main() -> int:
    parser = argparse.ArgumentParser(description="Independently score a Buddy Agent Life arena receipt.")
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    try:
        parsed = json.loads(args.receipt.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            raise ArenaScoreError("arena receipt must be a JSON object")
        score = score_agent_life_receipt(parsed)
    except (ArenaScoreError, json.JSONDecodeError, OSError) as error:
        parser.error(str(error))
    rendered = json.dumps(score, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if score["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
