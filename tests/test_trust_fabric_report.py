from __future__ import annotations

import json
from pathlib import Path

from scripts.buddy_trust_fabric_report import TrustRun, render_markdown, summarize


def write(path: Path, name: str, payload: dict) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / name).write_text(json.dumps(payload), encoding="utf-8")


def run_dir(tmp_path: Path, name: str, decision: str, *, verified: bool = False) -> Path:
    directory = tmp_path / name
    write(
        directory,
        "policy-decision.json",
        {
            "task_id": name,
            "decision": decision,
            "risk_level": "high" if decision == "block" else "medium",
            "stale_source_ids": ["old"] if decision == "review" else [],
            "conflicting_source_ids": ["a", "b"] if decision == "block" else [],
        },
    )
    write(
        directory,
        "execution-receipt.json",
        {
            "verified": verified,
            "artifact_accepted": verified,
            "security_gate": "pass" if verified else "not-run",
        },
    )
    if verified:
        write(
            directory,
            "task-economics.json",
            {
                "model_cost": 0.1,
                "tool_cost": 0.02,
                "human_review_minutes": 2,
            },
        )
    return directory


def test_summarizes_policy_and_verified_outcomes(tmp_path: Path):
    paths = [
        run_dir(tmp_path, "allowed", "allow", verified=True),
        run_dir(tmp_path, "review", "review"),
        run_dir(tmp_path, "blocked", "block"),
    ]
    result = summarize(TrustRun.from_directory(path) for path in paths)
    assert result["runs"] == 3
    assert result["decisions"] == {"allow": 1, "review": 1, "block": 1}
    assert result["verified_completions"] == 1
    assert result["high_risk_blocks"] == 1
    assert result["cost_per_verified_completion"] == 0.12


def test_markdown_states_verification_boundary(tmp_path: Path):
    result = summarize(
        [TrustRun.from_directory(run_dir(tmp_path, "allowed", "allow", verified=True))]
    )
    rendered = render_markdown(result)
    assert "retrieval answer is not a verified completion" in rendered
