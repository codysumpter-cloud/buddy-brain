#!/usr/bin/env python3
"""Summarize Trust Fabric admissibility, verification, and economics outcomes."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class TrustRun:
    task_id: str
    decision: str
    risk_level: str
    stale_sources: int
    conflicting_sources: int
    verified: bool
    artifact_accepted: bool
    security_gate: str
    total_cost: float
    human_review_minutes: float

    @classmethod
    def from_directory(cls, directory: Path) -> "TrustRun":
        decision = _read(directory / "policy-decision.json", required=True)
        receipt = _read(directory / "execution-receipt.json", required=False) or {}
        economics = _read(directory / "task-economics.json", required=False) or {}
        return cls(
            task_id=str(decision["task_id"]),
            decision=str(decision["decision"]),
            risk_level=str(decision["risk_level"]),
            stale_sources=len(decision.get("stale_source_ids", [])),
            conflicting_sources=len(decision.get("conflicting_source_ids", [])),
            verified=bool(receipt.get("verified", False)),
            artifact_accepted=bool(receipt.get("artifact_accepted", False)),
            security_gate=str(
                receipt.get("security_gate", economics.get("security_gate", "not-run"))
            ),
            total_cost=float(economics.get("model_cost", 0.0))
            + float(economics.get("tool_cost", 0.0)),
            human_review_minutes=float(economics.get("human_review_minutes", 0.0)),
        )

    @property
    def verified_completion(self) -> bool:
        return self.verified and self.artifact_accepted and self.security_gate == "pass"


def _read(path: Path, *, required: bool) -> dict[str, Any] | None:
    if not path.exists():
        if required:
            raise ValueError(f"missing required Trust Fabric output: {path}")
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def summarize(runs: Iterable[TrustRun]) -> dict[str, Any]:
    items = list(runs)
    total = len(items)
    decisions = {
        name: sum(run.decision == name for run in items)
        for name in ("allow", "review", "block")
    }
    verified = sum(run.verified_completion for run in items)
    direct_cost = sum(run.total_cost for run in items)
    review_minutes = sum(run.human_review_minutes for run in items)
    return {
        "schema_version": "1.0",
        "runs": total,
        "decisions": decisions,
        "allow_rate": round(decisions["allow"] / total, 4) if total else 0.0,
        "review_rate": round(decisions["review"] / total, 4) if total else 0.0,
        "block_rate": round(decisions["block"] / total, 4) if total else 0.0,
        "stale_evidence_rate": round(
            sum(run.stale_sources > 0 for run in items) / total, 4
        )
        if total
        else 0.0,
        "conflict_rate": round(
            sum(run.conflicting_sources > 0 for run in items) / total, 4
        )
        if total
        else 0.0,
        "verified_completions": verified,
        "verified_completion_rate": round(verified / total, 4) if total else 0.0,
        "direct_cost": round(direct_cost, 6),
        "human_review_minutes": round(review_minutes, 2),
        "cost_per_verified_completion": round(direct_cost / verified, 6)
        if verified
        else None,
        "high_risk_blocks": sum(
            run.risk_level in {"high", "critical"} and run.decision == "block"
            for run in items
        ),
    }


def render_markdown(summary: dict[str, Any]) -> str:
    cost = summary["cost_per_verified_completion"]
    cost_text = "n/a" if cost is None else f"${cost:,.4f}"
    return "\n".join(
        [
            "# Buddy Trust Fabric report",
            "",
            f"- Runs evaluated: {summary['runs']}",
            f"- Allowed: {summary['allow_rate'] * 100:.1f}%",
            f"- Human review required: {summary['review_rate'] * 100:.1f}%",
            f"- Blocked: {summary['block_rate'] * 100:.1f}%",
            f"- Stale evidence detected: {summary['stale_evidence_rate'] * 100:.1f}%",
            f"- Conflicts detected: {summary['conflict_rate'] * 100:.1f}%",
            f"- Verified completion rate: {summary['verified_completion_rate'] * 100:.1f}%",
            f"- Cost per verified completion: {cost_text}",
            f"- Human review: {summary['human_review_minutes']:g} minutes",
            "",
            "A retrieval answer is not a verified completion. Only artifact acceptance plus a passing security gate counts as verified.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize one or more Buddy Trust Fabric output directories."
    )
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = summarize(TrustRun.from_directory(path) for path in args.runs)
    rendered = (
        json.dumps(result, indent=2) + "\n"
        if args.format == "json"
        else render_markdown(result)
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
