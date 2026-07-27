#!/usr/bin/env python3
"""Score how safely a repository can support coding agents.

This tool intentionally scores evidence, not activity volume. Missing telemetry is a gap,
not proof that a repository is ready.
"""

from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[1] / "config" / "agent-readiness-policy.json"


@dataclass(frozen=True)
class Dimension:
    score: float
    evidence: list[str]
    gaps: list[str]


@dataclass(frozen=True)
class Report:
    version: int
    repository: str
    score: float
    classification: str
    dimensions: dict[str, Dimension]
    blockers: list[str]
    next_actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["score"] = round(self.score, 1)
        for dimension in value["dimensions"].values():
            dimension["score"] = round(dimension["score"], 1)
        return value


def _exists(root: Path, candidates: Iterable[str]) -> list[str]:
    return [candidate for candidate in candidates if (root / candidate).exists()]


def _all_files(root: Path) -> list[str]:
    ignored = {".git", "node_modules", ".venv", "venv", "dist", "build", ".next", ".cache", "__pycache__", ".pytest_cache"}
    files: list[str] = []
    for path in root.rglob("*"):
        if any(part in ignored for part in path.parts):
            continue
        if path.is_file():
            files.append(path.relative_to(root).as_posix())
    return files


def _contains_any(files: list[str], needles: Iterable[str]) -> list[str]:
    lowered = [(item, item.lower()) for item in files]
    return sorted({item for item, low in lowered if any(needle.lower() in low for needle in needles)})


def _instruction_dimension(root: Path, files: list[str]) -> Dimension:
    score = 0.0
    evidence: list[str] = []
    gaps: list[str] = []
    checks = [
        ("AGENTS.md", 30, "Add a root AGENTS.md generated from canonical BUAP source."),
        ("REVIEW.md", 25, "Add a separate REVIEW.md so review policy cannot mutate code."),
        (".buddy/policy.yaml", 25, "Add .buddy/policy.yaml with scoped coding/review/release profiles."),
    ]
    for relative, points, gap in checks:
        if (root / relative).is_file():
            score += points
            evidence.append(relative)
        else:
            gaps.append(gap)
    provider_files = _contains_any(files, [".buddy/providers/", "copilot-instructions", "claude.md", "gemini.md", "codex.md"])
    nested_agents = [item for item in files if item.endswith("/AGENTS.md")]
    if provider_files or nested_agents:
        score += 20
        evidence.extend((provider_files + nested_agents)[:8])
    else:
        gaps.append("Add provider adapters or package-scoped AGENTS.md files where behavior differs.")
    return Dimension(min(score, 100.0), evidence, gaps)


def _setup_dimension(root: Path, files: list[str]) -> Dimension:
    score = 0.0
    evidence: list[str] = []
    gaps: list[str] = []
    lockfiles = _exists(root, ["package-lock.json", "pnpm-lock.yaml", "yarn.lock", "uv.lock", "poetry.lock", "Pipfile.lock", "Cargo.lock", "go.sum"])
    if lockfiles:
        score += 30
        evidence.extend(lockfiles)
    else:
        gaps.append("Commit a dependency lockfile for deterministic setup.")
    setup = _contains_any(files, ["devcontainer", "dockerfile", "setup", "bootstrap", "copilot-code-review.yml"])
    if setup:
        score += 30
        evidence.extend(setup[:6])
    else:
        gaps.append("Provide a deterministic setup/bootstrap path or dedicated agent setup workflow.")
    commands = _exists(root, ["Makefile", "package.json", "pyproject.toml", "justfile", "Taskfile.yml"])
    if commands:
        score += 20
        evidence.extend(commands)
    else:
        gaps.append("Expose standard build/test commands through Make, package scripts, or pyproject.")
    ci = _contains_any(files, [".github/workflows/"])
    if ci:
        score += 20
        evidence.extend(ci[:6])
    else:
        gaps.append("Add CI that reproduces the documented setup and verification path.")
    return Dimension(min(score, 100.0), evidence, gaps)


def _test_dimension(root: Path, files: list[str]) -> Dimension:
    score = 0.0
    evidence: list[str] = []
    gaps: list[str] = []
    test_paths = _contains_any(files, ["/test_", "/tests/", ".test.", ".spec.", "test/"])
    if test_paths or (root / "tests").is_dir():
        score += 35
        evidence.extend(test_paths[:8] or ["tests/"])
    else:
        gaps.append("Add automated tests for the repository's critical paths.")
    workflows = _contains_any(files, [".github/workflows/"])
    test_workflows = [item for item in workflows if any(token in item.lower() for token in ("test", "ci", "check", "verify"))]
    if test_workflows:
        score += 30
        evidence.extend(test_workflows[:6])
    elif workflows:
        score += 15
        evidence.extend(workflows[:4])
        gaps.append("Ensure at least one workflow clearly runs the test/verification command.")
    else:
        gaps.append("Run tests in CI, not only on a developer machine.")
    command_files = _exists(root, ["Makefile", "package.json", "pyproject.toml"])
    if command_files:
        score += 20
        evidence.extend(command_files)
    else:
        gaps.append("Expose one canonical test command.")
    coverage = _contains_any(files, ["coverage", "codecov", "nyc", "pytest.ini", "vitest.config", "jest.config"])
    if coverage:
        score += 15
        evidence.extend(coverage[:5])
    else:
        gaps.append("Add coverage or a critical-path test manifest so test presence is not mistaken for adequacy.")
    return Dimension(min(score, 100.0), evidence, gaps)


def _browser_dimension(files: list[str]) -> Dimension:
    evidence = _contains_any(files, ["playwright", "cypress", "browser-verify", "browser_verify", "screenshot", "visual-regression", "e2e"])
    score = 0.0
    gaps: list[str] = []
    if evidence:
        score += 60
    else:
        gaps.append("Add browser or UI verification for user-facing behavior.")
    workflow_evidence = [item for item in evidence if ".github/workflows/" in item]
    if workflow_evidence:
        score += 25
    else:
        gaps.append("Run browser verification in CI when the repository owns a UI.")
    artifact_evidence = _contains_any(files, ["screenshots", "test-results", "playwright-report", "visual-artifact"])
    if artifact_evidence:
        score += 15
        evidence.extend(artifact_evidence[:4])
    else:
        gaps.append("Retain screenshots or browser artifacts as completion evidence where applicable.")
    return Dimension(min(score, 100.0), evidence[:10], gaps)


def _security_dimension(root: Path, files: list[str]) -> Dimension:
    score = 0.0
    evidence: list[str] = []
    gaps: list[str] = []
    codeql = _contains_any(files, ["codeql"])
    dependabot = _exists(root, [".github/dependabot.yml", ".github/dependabot.yaml"])
    secret_scan = _contains_any(files, ["gitleaks", "trufflehog", "secret-scan", "secret_scan"])
    static = _contains_any(files, ["ruff", "eslint", "mypy", "semgrep", "bandit", "sonar", "static-analysis", "static_analysis"])
    agent_review = _contains_any(files, ["security-review", "security_review", ".buddy/claims.yaml", "copilot-code-review.yml"])
    for found, points, gap in [
        (codeql, 25, "Enable CodeQL or equivalent static security analysis."),
        (dependabot, 20, "Enable dependency update/security monitoring."),
        (secret_scan, 20, "Add a secret scan that runs before merge."),
        (static, 20, "Add language-appropriate static analysis."),
        (agent_review, 15, "Store agent security-review findings with severity, confidence, and resolution state."),
    ]:
        if found:
            score += points
            evidence.extend(found if isinstance(found, list) else [str(found)])
        else:
            gaps.append(gap)
    return Dimension(min(score, 100.0), evidence[:12], gaps)


def _metrics_dimensions(metrics: dict[str, Any] | None) -> tuple[Dimension, Dimension]:
    if not metrics:
        gap = ["Collect repository-level agent PR acceptance and review-rework metrics."]
        return Dimension(0.0, [], gap), Dimension(0.0, [], gap.copy())
    created = int(metrics.get("agent_prs_created", 0))
    merged = int(metrics.get("agent_prs_merged", 0))
    regressions = int(metrics.get("regressions", 0))
    acceptance = (merged / created * 100.0) if created else 0.0
    acceptance = max(0.0, acceptance - min(regressions * 10.0, 50.0))
    acceptance_evidence = [f"agent_prs_created={created}", f"agent_prs_merged={merged}", f"regressions={regressions}"]
    acceptance_gaps = [] if created else ["No completed agent PR sample is available."]

    cycles = [float(value) for value in metrics.get("review_rework_cycles", [])]
    if cycles:
        median = statistics.median(cycles)
        rework_score = max(0.0, 100.0 - median * 20.0)
        rework_evidence = [f"median_review_rework_cycles={median:g}", f"sample_size={len(cycles)}"]
        rework_gaps = []
    else:
        rework_score = 0.0
        rework_evidence = []
        rework_gaps = ["Record review-rework cycles for agent-authored pull requests."]
    return (
        Dimension(min(acceptance, 100.0), acceptance_evidence, acceptance_gaps),
        Dimension(min(rework_score, 100.0), rework_evidence, rework_gaps),
    )


def classify(score: float, thresholds: dict[str, float]) -> str:
    if score >= thresholds["high_confidence"]:
        return "high-confidence"
    if score >= thresholds["ready"]:
        return "ready"
    if score >= thresholds["supervised"]:
        return "supervised"
    return "blocked"


def score_repository(root: Path, policy: dict[str, Any], metrics: dict[str, Any] | None = None) -> Report:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"repository path does not exist: {root}")
    files = _all_files(root)
    acceptance, rework = _metrics_dimensions(metrics)
    dimensions = {
        "instruction_coverage": _instruction_dimension(root, files),
        "deterministic_setup": _setup_dimension(root, files),
        "test_coverage": _test_dimension(root, files),
        "browser_verification": _browser_dimension(files),
        "security_gate": _security_dimension(root, files),
        "agent_pr_acceptance": acceptance,
        "median_review_rework": rework,
    }
    weights = policy["weights"]
    total_weight = sum(float(value) for value in weights.values())
    score = sum(dimensions[name].score * float(weight) for name, weight in weights.items()) / total_weight
    blockers: list[str] = []
    if not (root / "AGENTS.md").is_file():
        blockers.append("missing root AGENTS.md")
    if not (root / "REVIEW.md").is_file():
        blockers.append("missing separate review policy")
    if not (root / ".buddy/policy.yaml").is_file():
        blockers.append("missing scoped .buddy policy")
    if dimensions["test_coverage"].score < 50:
        blockers.append("insufficient automated test evidence")
    if dimensions["security_gate"].score < 50:
        blockers.append("insufficient security gate evidence")
    if dimensions["agent_pr_acceptance"].score == 0:
        blockers.append("no agent acceptance evidence")
    next_actions: list[str] = []
    for name in dimensions:
        for gap in dimensions[name].gaps:
            if gap not in next_actions:
                next_actions.append(gap)
    return Report(
        version=1,
        repository=root.name,
        score=score,
        classification=classify(score, policy["thresholds"]),
        dimensions=dimensions,
        blockers=blockers,
        next_actions=next_actions[:10],
    )


def render_markdown(report: Report) -> str:
    lines = [
        f"# Agent readiness: {report.repository}",
        "",
        f"**Score:** {report.score:.1f}/100  ",
        f"**Classification:** {report.classification}",
        "",
        "| Dimension | Score | Evidence |",
        "|---|---:|---|",
    ]
    for name, dimension in report.dimensions.items():
        evidence = ", ".join(dimension.evidence[:3]) or "none"
        lines.append(f"| {name} | {dimension.score:.1f} | {evidence} |")
    lines.extend(["", "## Blockers"])
    lines.extend([f"- {item}" for item in report.blockers] or ["- None detected by this static scan."])
    lines.extend(["", "## Next actions"])
    lines.extend([f"- {item}" for item in report.next_actions] or ["- Continue collecting acceptance and regression evidence."])
    return "\n".join(lines) + "\n"


def load_json(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Score repository readiness for guarded coding agents.")
    parser.add_argument("repositories", nargs="+", type=Path)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY_PATH)
    parser.add_argument("--metrics", type=Path, help="Optional metrics JSON for a single repository.")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    policy = load_json(args.policy)
    if policy is None:
        raise SystemExit("policy is required")
    if args.metrics and len(args.repositories) != 1:
        raise SystemExit("--metrics can only be used with one repository")
    metrics = load_json(args.metrics)
    reports = [score_repository(root, policy, metrics if index == 0 else None) for index, root in enumerate(args.repositories)]
    if args.format == "json":
        rendered = json.dumps(reports[0].to_dict() if len(reports) == 1 else [item.to_dict() for item in reports], indent=2) + "\n"
    else:
        rendered = "\n".join(render_markdown(item) for item in reports)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
