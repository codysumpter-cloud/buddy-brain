#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN_DIR = ROOT / "workflows"

TEMPLATES = {
    "diagnose-and-fix": {
        "steps": [
            {"name": "detect", "run": "bash scripts/skill-auto.sh --text \"{input}\""},
            {"name": "recover", "run": "bash scripts/skill-recover-learned.sh --apply --text \"{input}\""},
            {"name": "report", "run": "python3 scripts/skill_stats.py"},
        ]
    },
    "guarded-evolution": {
        "steps": [
            {"name": "validate-scripts", "run": "node --check scripts/validate-skills.mjs && python3 -m py_compile scripts/skill_confidence.py scripts/skill_health.py scripts/skill_decay.py"},
            {"name": "confidence", "run": "python3 scripts/skill_confidence.py --output workflows/guarded-evolution-scorecard.json"},
            {"name": "health", "run": "python3 scripts/skill_health.py"},
            {"name": "decay", "run": "python3 scripts/skill_decay.py"},
        ]
    },
}


def render_template(name: str, user_input: str) -> dict:
    plan = json.loads(json.dumps(TEMPLATES[name]))
    for step in plan["steps"]:
        step["run"] = step["run"].replace("{input}", user_input)
    plan["template_used"] = name
    plan["input"] = user_input
    return plan


def choose_template(goal: str) -> str:
    lower = goal.lower()
    if any(word in lower for word in ["evolve", "improve", "autonomy", "skills", "confidence", "health", "decay", "registry"]):
        return "guarded-evolution"
    return "diagnose-and-fix"


def build_dynamic_plan(goal: str) -> dict:
    template = choose_template(goal)
    plan = render_template(template, goal)
    plan["goal"] = goal
    plan["planner_mode"] = "dynamic"
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate goal-driven skill workflow plans.")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--output", default="dynamic-plan.json")
    args = parser.parse_args()

    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    plan = build_dynamic_plan(args.goal)
    out = PLAN_DIR / args.output
    out.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote plan to {out}")


if __name__ == "__main__":
    main()
