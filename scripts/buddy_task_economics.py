#!/usr/bin/env python3
"""Summarize the complete cost of reaching verified agent outcomes."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

REQUIRED_FIELDS = {
    "task_id",
    "provider",
    "model",
    "attempts",
    "model_cost",
    "tool_cost",
    "elapsed_ms",
    "human_review_minutes",
    "verification_passed",
    "artifacts_accepted",
}


@dataclass(frozen=True)
class TaskRecord:
    task_id: str
    provider: str
    model: str
    attempts: int
    model_cost: float
    tool_cost: float
    elapsed_ms: int
    human_review_minutes: float
    verification_passed: bool
    artifacts_accepted: bool
    rolled_back: bool = False
    repository: str = ""
    workflow: str = ""
    security_gate: str = "not-run"

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TaskRecord":
        missing = REQUIRED_FIELDS - payload.keys()
        if missing:
            raise ValueError(f"task record missing fields: {', '.join(sorted(missing))}")
        attempts = int(payload["attempts"])
        if attempts < 1:
            raise ValueError("attempts must be at least 1")
        for field in ("model_cost", "tool_cost", "human_review_minutes"):
            if float(payload[field]) < 0:
                raise ValueError(f"{field} cannot be negative")
        return cls(
            task_id=str(payload["task_id"]),
            provider=str(payload["provider"]),
            model=str(payload["model"]),
            attempts=attempts,
            model_cost=float(payload["model_cost"]),
            tool_cost=float(payload["tool_cost"]),
            elapsed_ms=int(payload["elapsed_ms"]),
            human_review_minutes=float(payload["human_review_minutes"]),
            verification_passed=bool(payload["verification_passed"]),
            artifacts_accepted=bool(payload["artifacts_accepted"]),
            rolled_back=bool(payload.get("rolled_back", False)),
            repository=str(payload.get("repository", "")),
            workflow=str(payload.get("workflow", "")),
            security_gate=str(payload.get("security_gate", "not-run")),
        )

    @property
    def verified_completion(self) -> bool:
        return self.verification_passed and self.artifacts_accepted and not self.rolled_back and self.security_gate != "block"


def read_records(path: Path) -> list[TaskRecord]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        values = json.loads(text)
    else:
        values = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [TaskRecord.from_dict(value) for value in values]


def summarize(records: Iterable[TaskRecord], human_hour_rate: float = 0.0) -> dict[str, Any]:
    items = list(records)
    tasks = len(items)
    completions = sum(item.verified_completion for item in items)
    attempts = sum(item.attempts for item in items)
    direct_cost = sum(item.model_cost + item.tool_cost for item in items)
    review_minutes = sum(item.human_review_minutes for item in items)
    review_cost = review_minutes / 60.0 * human_hour_rate
    total_cost = direct_cost + review_cost
    completion_rate = completions / tasks if tasks else 0.0
    artifact_acceptance = sum(item.artifacts_accepted for item in items) / tasks if tasks else 0.0
    retry_tasks = sum(item.attempts > 1 for item in items)
    rollbacks = sum(item.rolled_back for item in items)
    security_blocks = sum(item.security_gate == "block" for item in items)
    return {
        "tasks": tasks,
        "attempts": attempts,
        "verified_completions": completions,
        "verified_completion_rate": round(completion_rate, 4),
        "artifact_acceptance_rate": round(artifact_acceptance, 4),
        "retry_rate": round(retry_tasks / tasks, 4) if tasks else 0.0,
        "rollback_rate": round(rollbacks / tasks, 4) if tasks else 0.0,
        "security_block_rate": round(security_blocks / tasks, 4) if tasks else 0.0,
        "direct_cost": round(direct_cost, 6),
        "human_review_minutes": round(review_minutes, 2),
        "human_review_cost": round(review_cost, 6),
        "total_cost": round(total_cost, 6),
        "cost_per_verified_completion": round(total_cost / completions, 6) if completions else None,
        "expected_cost_to_verified_completion": round((total_cost / tasks) / completion_rate, 6) if tasks and completion_rate else None,
        "median_elapsed_ms": _median([item.elapsed_ms for item in items]),
        "median_review_minutes": _median([item.human_review_minutes for item in items]),
    }


def _median(values: list[float | int]) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    middle = len(ordered) // 2
    result = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
    return round(result, 2)


def grouped_summary(records: list[TaskRecord], human_hour_rate: float = 0.0) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[TaskRecord]] = defaultdict(list)
    for record in records:
        groups[(record.provider, record.model)].append(record)
    return {
        "version": 1,
        "human_hour_rate": human_hour_rate,
        "overall": summarize(records, human_hour_rate),
        "providers": [
            {
                "provider": provider,
                "model": model,
                **summarize(items, human_hour_rate),
            }
            for (provider, model), items in sorted(groups.items())
        ],
    }


def render_markdown(summary: dict[str, Any]) -> str:
    overall = summary["overall"]
    lines = [
        "# Buddy task economics",
        "",
        f"- Verified completion rate: {overall['verified_completion_rate'] * 100:.1f}%",
        f"- Cost per verified completion: {_money(overall['cost_per_verified_completion'])}",
        f"- Retry rate: {overall['retry_rate'] * 100:.1f}%",
        f"- Median human review: {overall['median_review_minutes'] or 0:g} minutes",
        f"- Rollback rate: {overall['rollback_rate'] * 100:.1f}%",
        "",
        "| Provider | Model | Tasks | Verified | Cost / verified completion | Retry rate | Median review |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for item in summary["providers"]:
        lines.append(
            f"| {item['provider']} | {item['model']} | {item['tasks']} | "
            f"{item['verified_completion_rate'] * 100:.1f}% | {_money(item['cost_per_verified_completion'])} | "
            f"{item['retry_rate'] * 100:.1f}% | {item['median_review_minutes'] or 0:g} min |"
        )
    lines.extend([
        "",
        "Use this report as routing feedback only after each provider/model group has a meaningful sample. Do not route on token price alone.",
    ])
    return "\n".join(lines) + "\n"


def _money(value: float | None) -> str:
    return "n/a" if value is None or math.isinf(value) else f"${value:,.4f}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate cost to verified completion from Buddy task records.")
    parser.add_argument("records", type=Path, help="JSON array or JSONL task records")
    parser.add_argument("--human-hour-rate", type=float, default=0.0)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.human_hour_rate < 0:
        raise SystemExit("--human-hour-rate cannot be negative")
    result = grouped_summary(read_records(args.records), args.human_hour_rate)
    rendered = json.dumps(result, indent=2) + "\n" if args.format == "json" else render_markdown(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
