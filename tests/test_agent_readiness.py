import json
from pathlib import Path

from scripts.buddy_agent_readiness import score_repository


def policy() -> dict:
    return json.loads((Path(__file__).parents[1] / "config" / "agent-readiness-policy.json").read_text())


def test_empty_repo_is_blocked(tmp_path):
    report = score_repository(tmp_path, policy())
    assert report.classification == "blocked"
    assert report.score < 25
    assert "missing root AGENTS.md" in report.blockers


def test_policy_test_security_and_metrics_raise_readiness(tmp_path):
    (tmp_path / ".buddy/providers").mkdir(parents=True)
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    for relative in [
        "AGENTS.md",
        "REVIEW.md",
        ".buddy/policy.yaml",
        ".buddy/claims.yaml",
        ".buddy/providers/codex.yaml",
        "package-lock.json",
        "package.json",
        "tests/example.test.js",
        ".github/workflows/ci.yml",
        ".github/workflows/codeql.yml",
        ".github/dependabot.yml",
        ".github/workflows/secret-scan.yml",
        "eslint.config.js",
        "playwright.config.ts",
        ".github/workflows/browser-verify.yml",
        "test-results/example.png",
    ]:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("test", encoding="utf-8")
    metrics = {
        "agent_prs_created": 10,
        "agent_prs_merged": 9,
        "regressions": 0,
        "review_rework_cycles": [0, 1, 1, 1, 2],
    }
    report = score_repository(tmp_path, policy(), metrics)
    assert report.score >= 75
    assert report.classification in {"ready", "high-confidence"}
    assert report.dimensions["agent_pr_acceptance"].score == 90
