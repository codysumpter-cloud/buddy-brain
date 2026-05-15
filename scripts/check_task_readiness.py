#!/usr/bin/env python3
from __future__ import annotations

import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REQUIRED_PLAN_HEADINGS = [
    "## Problem",
    "## Smallest useful wedge",
    "## Verification plan",
    "## Rollback plan",
]
REQUIRED_PRODUCT_SPEC_HEADINGS = [
    "## Summary",
    "## Problem",
    "## Goals",
    "## Non-goals / scope boundaries",
    "## User experience / behavior requirements",
    "## Success criteria",
    "## Validation",
    "## Open product questions",
]
REQUIRED_TECH_SPEC_HEADINGS = [
    "## Problem",
    "## Relevant code",
    "## Current state",
    "## Proposed changes",
    "## End-to-end flow",
    "## Risks and mitigations",
    "## Testing and validation",
    "## Rollback plan",
    "## Follow-ups / open technical questions",
]
SPEC_TECH_PATH_RE = re.compile(r"^specs/GH\d+/tech\.md$")


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def info(message: str) -> None:
    print(f"INFO: {message}")


def normalize_markdown(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def extract_plan_path(pr_body: str) -> str | None:
    pattern = re.compile(r"Plan:\s*`([^`]+)`|Plan:\s*([^\s]+)")
    match = pattern.search(pr_body)
    if not match:
        return None
    return (match.group(1) or match.group(2)).strip().strip("`")


def has_heading(markdown: str, heading: str) -> bool:
    return any(line.strip() == heading for line in markdown.splitlines())


def validate_headings(markdown: str, required_headings: list[str], context: str) -> int:
    for heading in required_headings:
        if not has_heading(markdown, heading):
            return fail(f"{context} is missing required section: {heading}")
    return 0


def validate_plan_path(plan_ref: str) -> tuple[pathlib.Path | None, int]:
    if plan_ref == "PR_BODY":
        return None, 0

    if plan_ref.startswith("/") or ".." in pathlib.PurePosixPath(plan_ref).parts:
        return None, fail(f"plan reference must stay inside the repository: {plan_ref}")

    if plan_ref.startswith("specs/") and not SPEC_TECH_PATH_RE.match(plan_ref):
        return None, fail("spec-backed plans must reference specs/GH<number>/tech.md")

    plan_path = ROOT / plan_ref
    if not plan_path.exists():
        return None, fail(f"referenced plan file does not exist: {plan_ref}")

    if plan_path.is_dir():
        return None, fail(f"referenced plan path is a directory: {plan_ref}")

    return plan_path, 0


def validate_spec_backed_plan(plan_path: pathlib.Path, plan_ref: str, plan_text: str) -> int:
    status = validate_headings(plan_text, REQUIRED_TECH_SPEC_HEADINGS, "tech spec")
    if status != 0:
        return status

    product_path = plan_path.with_name("product.md")
    if not product_path.exists():
        return fail(f"spec-backed plan is missing sibling product spec: {product_path.relative_to(ROOT)}")

    product_text = normalize_markdown(product_path.read_text(encoding="utf-8"))
    status = validate_headings(product_text, REQUIRED_PRODUCT_SPEC_HEADINGS, "product spec")
    if status != 0:
        return status

    info(f"validated spec-backed plan: {plan_ref}")
    return 0


def main() -> int:
    event_name = os.environ.get("GITHUB_EVENT_NAME", "").strip()
    event_action = os.environ.get("GITHUB_EVENT_ACTION", "").strip()
    pr_body = os.environ.get("PR_BODY", "")

    if event_name and event_name != "pull_request":
        info(f"skipping task readiness outside pull_request events: {event_name}")
        return 0

    if event_action == "closed":
        info("skipping task readiness for closed pull_request event")
        return 0

    if not pr_body.strip():
        info("skipping task readiness because pull request body is empty or unavailable")
        return 0

    pr_body = normalize_markdown(pr_body)

    if "## task contract" not in pr_body.lower():
        return fail("pull request body is missing the '## Task contract' block")

    plan_ref = extract_plan_path(pr_body)
    if not plan_ref:
        return fail("pull request body is missing a plan reference")

    plan_path, status = validate_plan_path(plan_ref)
    if status != 0:
        return status

    if plan_path is None:
        plan_text = pr_body
        status = validate_headings(plan_text, REQUIRED_PLAN_HEADINGS, "plan")
    else:
        plan_text = normalize_markdown(plan_path.read_text(encoding="utf-8"))
        if SPEC_TECH_PATH_RE.match(plan_ref):
            status = validate_spec_backed_plan(plan_path, plan_ref, plan_text)
        else:
            status = validate_headings(plan_text, REQUIRED_PLAN_HEADINGS, "plan")

    if status != 0:
        return status

    normalized = pr_body.lower()
    if "- verification: yes" not in normalized:
        return fail("pull request body must declare '- Verification: yes'")
    if "- rollback: yes" not in normalized:
        return fail("pull request body must declare '- Rollback: yes'")

    print("task readiness contract satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
