#!/usr/bin/env python3
"""Independently score seeded Prismtek Norn robustness receipts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

RECEIPT_SCHEMA = "prismtek-norn-stochastic-arena-v1"
SCORE_SCHEMA = "prismtek-norn-stochastic-score-v1"
EXPECTED_SEED = 90210
EXPECTED_TRIALS = 32
REQUIRED_SCENARIOS = {
    "noisy-adaptation": 25,
    "noisy-unseen-transfer": 20,
    "random-need-planning": 15,
    "random-persistence": 15,
    "ecology-endurance-1000-ticks": 15,
    "two-generation-lineage": 10,
}


class NornStochasticScoreError(ValueError):
    """The stochastic receipt is malformed, tampered with, or insufficient."""


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
        raise NornStochasticScoreError(f"{label} is missing receipt_sha256")
    if supplied != _digest(_without_hash(payload)):
        raise NornStochasticScoreError(f"{label} hash mismatch")


def _number(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise NornStochasticScoreError(f"{field} must be numeric")
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise NornStochasticScoreError(f"{field} must be numeric") from error


def _measurement(scenario: dict[str, Any], name: str) -> Any:
    measurements = scenario.get("measurements")
    if not isinstance(measurements, dict) or name not in measurements:
        raise NornStochasticScoreError(
            f"scenario {scenario.get('id')} is missing measurement {name}"
        )
    return measurements[name]


def _scenario_map(receipt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = receipt.get("scenarios")
    if not isinstance(raw, list):
        raise NornStochasticScoreError("receipt.scenarios must be an array")
    result: dict[str, dict[str, Any]] = {}
    for index, scenario in enumerate(raw):
        if not isinstance(scenario, dict):
            raise NornStochasticScoreError(f"scenario[{index}] must be an object")
        scenario_id = str(scenario.get("id", ""))
        if not scenario_id:
            raise NornStochasticScoreError(f"scenario[{index}] requires id")
        if scenario_id in result:
            raise NornStochasticScoreError(f"duplicate scenario {scenario_id}")
        _verify_hash(scenario, f"scenario {scenario_id}")
        result[scenario_id] = scenario
    missing = sorted(set(REQUIRED_SCENARIOS) - set(result))
    extra = sorted(set(result) - set(REQUIRED_SCENARIOS))
    if missing:
        raise NornStochasticScoreError(f"missing required scenarios: {', '.join(missing)}")
    if extra:
        raise NornStochasticScoreError(f"unknown scenarios: {', '.join(extra)}")
    return result


def _rate_consistent(successes: int, trials: int, rate: float) -> bool:
    return trials > 0 and successes >= 0 and successes <= trials and abs(rate - successes / trials) <= 1e-12


def _judge_adaptation(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    trials = int(_number(_measurement(scenario, "trials"), "trials"))
    acquisition_successes = int(
        _number(_measurement(scenario, "acquisition_successes"), "acquisition_successes")
    )
    reversal_successes = int(
        _number(_measurement(scenario, "reversal_successes"), "reversal_successes")
    )
    acquisition_rate = _number(_measurement(scenario, "acquisition_rate"), "acquisition_rate")
    reversal_rate = _number(_measurement(scenario, "reversal_rate"), "reversal_rate")
    margin = _number(
        _measurement(scenario, "minimum_reversal_margin"), "minimum_reversal_margin"
    )
    noise = _number(_measurement(scenario, "noise_probability"), "noise_probability")
    passed = (
        trials == EXPECTED_TRIALS
        and _rate_consistent(acquisition_successes, trials, acquisition_rate)
        and _rate_consistent(reversal_successes, trials, reversal_rate)
        and acquisition_rate >= 0.90
        and reversal_rate >= 0.90
        and margin >= 0.40
        and abs(noise - 0.15) <= 1e-12
    )
    return passed, {
        "trials": trials,
        "acquisition_rate": acquisition_rate,
        "reversal_rate": reversal_rate,
        "minimum_reversal_margin": margin,
        "noise_probability": noise,
    }


def _judge_transfer(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    trials = int(_number(_measurement(scenario, "trials"), "trials"))
    successes = int(_number(_measurement(scenario, "successes"), "successes"))
    rate = _number(_measurement(scenario, "success_rate"), "success_rate")
    minimum = _number(
        _measurement(scenario, "minimum_category_value"), "minimum_category_value"
    )
    mean = _number(_measurement(scenario, "mean_category_value"), "mean_category_value")
    noise = _number(_measurement(scenario, "noise_probability"), "noise_probability")
    passed = (
        trials == EXPECTED_TRIALS
        and _rate_consistent(successes, trials, rate)
        and rate >= 0.90
        and minimum > 0.0
        and mean >= 0.25
        and abs(noise - 0.15) <= 1e-12
    )
    return passed, {
        "trials": trials,
        "success_rate": rate,
        "minimum_category_value": minimum,
        "mean_category_value": mean,
        "noise_probability": noise,
    }


def _judge_planning(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    trials = int(_number(_measurement(scenario, "trials"), "trials"))
    successes = int(_number(_measurement(scenario, "successes"), "successes"))
    rate = _number(_measurement(scenario, "success_rate"), "success_rate")
    pressure = _number(
        _measurement(scenario, "maximum_final_pressure"), "maximum_final_pressure"
    )
    passed = (
        trials == EXPECTED_TRIALS
        and _rate_consistent(successes, trials, rate)
        and rate == 1.0
        and pressure <= 0.10
    )
    return passed, {
        "trials": trials,
        "success_rate": rate,
        "maximum_final_pressure": pressure,
    }


def _judge_persistence(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    trials = int(_number(_measurement(scenario, "trials"), "trials"))
    successes = int(_number(_measurement(scenario, "successes"), "successes"))
    rate = _number(_measurement(scenario, "success_rate"), "success_rate")
    delta = _number(
        _measurement(scenario, "maximum_value_delta"), "maximum_value_delta"
    )
    passed = (
        trials == EXPECTED_TRIALS
        and _rate_consistent(successes, trials, rate)
        and rate == 1.0
        and delta <= 1e-12
    )
    return passed, {
        "trials": trials,
        "success_rate": rate,
        "maximum_value_delta": delta,
    }


def _judge_ecology(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    ticks = int(_number(_measurement(scenario, "ticks"), "ticks"))
    extinctions = int(_number(_measurement(scenario, "extinctions"), "extinctions"))
    minimum = _number(_measurement(scenario, "minimum_population"), "minimum_population")
    final = _number(_measurement(scenario, "final_population"), "final_population")
    nutrition = _number(
        _measurement(scenario, "total_harvest_nutrition"), "total_harvest_nutrition"
    )
    passed = ticks == 1000 and extinctions == 0 and minimum > 1.0 and final > 1.0 and nutrition > 0.0
    return passed, {
        "ticks": ticks,
        "extinctions": extinctions,
        "minimum_population": minimum,
        "final_population": final,
        "total_harvest_nutrition": nutrition,
    }


def _judge_lineage(scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    first = bool(_measurement(scenario, "first_conception"))
    second = bool(_measurement(scenario, "second_conception"))
    first_births = int(_number(_measurement(scenario, "first_birth_count"), "first_birth_count"))
    second_births = int(
        _number(_measurement(scenario, "second_birth_count"), "second_birth_count")
    )
    child = str(_measurement(scenario, "child_id"))
    grandchild = str(_measurement(scenario, "grandchild_id"))
    generation = int(
        _number(_measurement(scenario, "grandchild_generation"), "grandchild_generation")
    )
    parents = int(
        _number(_measurement(scenario, "grandchild_parent_count"), "grandchild_parent_count")
    )
    passed = (
        first
        and second
        and first_births == 1
        and second_births == 1
        and bool(child)
        and bool(grandchild)
        and child != grandchild
        and generation == 2
        and parents == 2
    )
    return passed, {
        "first_conception": first,
        "second_conception": second,
        "first_birth_count": first_births,
        "second_birth_count": second_births,
        "child_id": child,
        "grandchild_id": grandchild,
        "grandchild_generation": generation,
        "grandchild_parent_count": parents,
    }


Judge = Callable[[dict[str, Any]], tuple[bool, dict[str, Any]]]
JUDGES: dict[str, Judge] = {
    "noisy-adaptation": _judge_adaptation,
    "noisy-unseen-transfer": _judge_transfer,
    "random-need-planning": _judge_planning,
    "random-persistence": _judge_persistence,
    "ecology-endurance-1000-ticks": _judge_ecology,
    "two-generation-lineage": _judge_lineage,
}


def score_norn_stochastic_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    if receipt.get("schema") != RECEIPT_SCHEMA:
        raise NornStochasticScoreError("unsupported stochastic Norn receipt schema")
    if receipt.get("mode") != "cortex-off":
        raise NornStochasticScoreError("stochastic Norn scoring requires cortex-off mode")
    if receipt.get("seed") != EXPECTED_SEED or receipt.get("trials") != EXPECTED_TRIALS:
        raise NornStochasticScoreError("unexpected stochastic seed or trial count")
    _verify_hash(receipt, "stochastic Norn receipt")
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

    summary_consistent = (
        receipt.get("scenario_count") == len(REQUIRED_SCENARIOS)
        and receipt.get("passed_count") == len(REQUIRED_SCENARIOS)
        and receipt.get("failed_count") == 0
        and receipt.get("passed") is True
    )
    passed = all(item["passed"] for item in judgments) and summary_consistent and awarded == 100
    score: dict[str, Any] = {
        "schema": SCORE_SCHEMA,
        "source_schema": RECEIPT_SCHEMA,
        "source_receipt_sha256": str(receipt["receipt_sha256"]),
        "mode": "cortex-off",
        "seed": EXPECTED_SEED,
        "trials": EXPECTED_TRIALS,
        "score": awarded,
        "maximum_score": 100,
        "passed": passed,
        "readiness": "green" if passed else "yellow" if awarded >= 70 else "red",
        "runtime_summary_consistent": summary_consistent,
        "judgments": judgments,
        "claim_boundary": (
            "A green score establishes the measured seeded robustness, 1,000-tick "
            "ecology endurance, and two-generation lineage for the exact receipt. "
            "It does not establish consciousness, unrestricted general intelligence, "
            "OpenC2E behavioral equivalence, or untested distributions."
        ),
    }
    score["score_sha256"] = _digest(score)
    return score


def main() -> int:
    parser = argparse.ArgumentParser(description="Independently score a stochastic Norn receipt.")
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    try:
        parsed = json.loads(args.receipt.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            raise NornStochasticScoreError("receipt must be a JSON object")
        score = score_norn_stochastic_receipt(parsed)
    except (NornStochasticScoreError, json.JSONDecodeError, OSError) as error:
        parser.error(str(error))
    rendered = json.dumps(score, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if score["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
