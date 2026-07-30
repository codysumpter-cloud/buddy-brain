#!/usr/bin/env python3
"""Independently validate and score Prismtek Norn memory/navigation/skills receipts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

RECEIPT_SCHEMA = "prismtek-norn-memory-navigation-skills-receipt-v1"
SCORE_SCHEMA = "prismtek-norn-memory-navigation-skills-score-v1"
REQUIRED_MEASUREMENTS = {
    "autobiographical_recall": 15,
    "semantic_knowledge": 15,
    "spatial_routing": 15,
    "hierarchical_skill": 15,
    "skill_adaptation": 15,
    "stack_integration": 15,
    "persistence": 10,
}


class NornMemoryNavigationSkillsScoreError(ValueError):
    """The source receipt is malformed, tampered with, or incomplete."""


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
        raise NornMemoryNavigationSkillsScoreError("receipt is missing receipt_sha256")
    if supplied != _digest(_without_hash(receipt)):
        raise NornMemoryNavigationSkillsScoreError("receipt hash mismatch")


def _number(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise NornMemoryNavigationSkillsScoreError(f"{field} must be numeric")
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise NornMemoryNavigationSkillsScoreError(f"{field} must be numeric") from error


def _measurement_map(receipt: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = receipt.get("measurements")
    if not isinstance(raw, dict):
        raise NornMemoryNavigationSkillsScoreError("receipt.measurements must be an object")
    result: dict[str, dict[str, Any]] = {}
    for key, value in raw.items():
        if not isinstance(value, dict):
            raise NornMemoryNavigationSkillsScoreError(f"measurement {key} must be an object")
        result[str(key)] = value
    missing = sorted(set(REQUIRED_MEASUREMENTS) - set(result))
    extra = sorted(set(result) - set(REQUIRED_MEASUREMENTS))
    if missing:
        raise NornMemoryNavigationSkillsScoreError(
            f"missing required measurements: {', '.join(missing)}"
        )
    if extra:
        raise NornMemoryNavigationSkillsScoreError(
            f"unknown measurements: {', '.join(extra)}"
        )
    return result


def _judge_autobiographical(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    selected = str(row.get("selected_target", ""))
    match = _number(row.get("match_score"), "autobiographical_recall.match_score")
    retrievals = int(_number(row.get("retrievals"), "autobiographical_recall.retrievals"))
    passed = selected == "red_ball" and match >= 0.45 and retrievals == 1
    return passed, {
        "selected_target": selected,
        "match_score": match,
        "retrievals": retrievals,
        "minimum_match_score": 0.45,
    }


def _judge_semantic(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    before_object = row.get("object_before")
    before_confidence = _number(
        row.get("confidence_before"), "semantic_knowledge.confidence_before"
    )
    after_object = row.get("object_after_weak_contradiction")
    contradictions = int(
        _number(row.get("contradictions"), "semantic_knowledge.contradictions")
    )
    retained = _number(
        row.get("retained_confidence"), "semantic_knowledge.retained_confidence"
    )
    passed = (
        before_object is True
        and after_object is True
        and before_confidence >= 0.55
        and contradictions == 1
        and retained >= 0.50
        and retained <= before_confidence
    )
    return passed, {
        "object_before": before_object,
        "confidence_before": before_confidence,
        "object_after_weak_contradiction": after_object,
        "contradictions": contradictions,
        "retained_confidence": retained,
        "minimum_retained_confidence": 0.50,
    }


def _judge_spatial(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    raw_rooms = row.get("route_rooms")
    if not isinstance(raw_rooms, list):
        raise NornMemoryNavigationSkillsScoreError("spatial_routing.route_rooms must be an array")
    rooms = [str(value) for value in raw_rooms]
    steps = int(_number(row.get("steps"), "spatial_routing.steps"))
    host_validated = bool(row.get("host_validated", False))
    passed = rooms == ["hall", "garden"] and steps == 2 and host_validated
    return passed, {
        "route_rooms": rooms,
        "steps": steps,
        "host_validation_preserved": host_validated,
        "dangerous_shortcut_avoided": rooms != ["garden"],
    }


def _judge_hierarchical_skill(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    learned = bool(row.get("learned", False))
    proposals = int(_number(row.get("proposal_count"), "hierarchical_skill.proposal_count"))
    expanded = int(_number(row.get("expanded_steps"), "hierarchical_skill.expanded_steps"))
    host_validated = bool(row.get("host_validated", False))
    reliability = _number(row.get("reliability"), "hierarchical_skill.reliability")
    passed = (
        learned
        and proposals == 1
        and expanded == 3
        and host_validated
        and reliability >= 0.75
    )
    return passed, {
        "learned": learned,
        "proposal_count": proposals,
        "expanded_steps": expanded,
        "host_validation_preserved": host_validated,
        "reliability": reliability,
        "minimum_reliability": 0.75,
    }


def _judge_skill_adaptation(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    before = _number(row.get("reliability_before"), "skill_adaptation.reliability_before")
    after = _number(row.get("reliability_after"), "skill_adaptation.reliability_after")
    failures = int(_number(row.get("failed_executions"), "skill_adaptation.failed_executions"))
    passed = before >= 0.75 and after < before and after <= 0.70 and failures == 1
    return passed, {
        "reliability_before": before,
        "reliability_after": after,
        "reliability_drop": before - after,
        "failed_executions": failures,
    }


def _judge_integration(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    episode = str(row.get("episode_id", ""))
    memories = int(_number(row.get("memory_count"), "stack_integration.memory_count"))
    confidence = _number(row.get("fact_confidence"), "stack_integration.fact_confidence")
    rooms = int(_number(row.get("mapped_rooms"), "stack_integration.mapped_rooms"))
    passed = bool(episode) and memories == 1 and confidence >= 0.35 and rooms == 1
    return passed, {
        "episode_id": episode,
        "memory_count": memories,
        "fact_confidence": confidence,
        "mapped_rooms": rooms,
    }


def _judge_persistence(row: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    restored = bool(row.get("restored", False))
    episodes = int(_number(row.get("episodes"), "persistence.episodes"))
    facts = int(_number(row.get("facts"), "persistence.facts"))
    rooms = int(_number(row.get("rooms"), "persistence.rooms"))
    skills = int(_number(row.get("skills"), "persistence.skills"))
    passed = restored and episodes == 1 and facts == 1 and rooms == 1 and skills == 1
    return passed, {
        "restored": restored,
        "episodes": episodes,
        "facts": facts,
        "rooms": rooms,
        "skills": skills,
    }


Judge = Callable[[dict[str, Any]], tuple[bool, dict[str, Any]]]
JUDGES: dict[str, Judge] = {
    "autobiographical_recall": _judge_autobiographical,
    "semantic_knowledge": _judge_semantic,
    "spatial_routing": _judge_spatial,
    "hierarchical_skill": _judge_hierarchical_skill,
    "skill_adaptation": _judge_skill_adaptation,
    "stack_integration": _judge_integration,
    "persistence": _judge_persistence,
}


def score_norn_memory_navigation_skills_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Recompute the source hash and independently judge all seven domains."""
    if receipt.get("schema") != RECEIPT_SCHEMA:
        raise NornMemoryNavigationSkillsScoreError("unsupported receipt schema")
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
            "A green score establishes the seven measured bounded memory, navigation "
            "and skill software behaviors for the exact receipt. It does not establish "
            "human autobiographical memory, perfect navigation, unrestricted autonomy, "
            "or behavior outside the tested environments."
        ),
    }
    score["score_sha256"] = _digest(score)
    return score


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Independently score a Prismtek Norn memory/navigation/skills receipt."
    )
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    try:
        parsed = json.loads(args.receipt.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            raise NornMemoryNavigationSkillsScoreError("receipt root must be an object")
        score = score_norn_memory_navigation_skills_receipt(parsed)
    except (OSError, json.JSONDecodeError, NornMemoryNavigationSkillsScoreError) as error:
        print(f"memory/navigation/skills score failed: {error}")
        return 1
    encoded = json.dumps(score, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if score["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
