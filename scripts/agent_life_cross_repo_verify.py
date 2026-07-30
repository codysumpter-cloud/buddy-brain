#!/usr/bin/env python3
"""Verify the four-repository BUAP Agent Life proof chain."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

CROSS_REPO_SCHEMA = "prismtek-agent-life-cross-repo-e2e-v1"
PROFILE_SCHEMA = "prismtek-agent-life-profile-v1"
RAW_EVENT_SCHEMA = "prismtek-agent-life-event-v1"
ARENA_SCHEMA = "prismtek-agent-life-arena-v1"
SCORE_SCHEMA = "prismtek-agent-life-arena-score-v1"


class CrossRepoVerificationError(ValueError):
    """The cross-repository evidence chain is incomplete or inconsistent."""


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise CrossRepoVerificationError(f"{label} is unreadable") from error
    if not isinstance(parsed, dict):
        raise CrossRepoVerificationError(f"{label} must be a JSON object")
    return parsed


def _load_single_jsonl(path: Path, label: str) -> dict[str, Any]:
    try:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (json.JSONDecodeError, OSError) as error:
        raise CrossRepoVerificationError(f"{label} is unreadable") from error
    if len(rows) != 1 or not isinstance(rows[0], dict):
        raise CrossRepoVerificationError(f"{label} must contain exactly one JSON object")
    return rows[0]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CrossRepoVerificationError(message)


def verify_cross_repo_chain(
    *,
    profile_path: Path,
    learning_result_path: Path,
    raw_event_path: Path,
    canonical_event_path: Path,
    graph_record_path: Path,
    arena_receipt_path: Path,
    score_receipt_path: Path,
    component_shas: dict[str, str],
) -> dict[str, Any]:
    """Validate and bind one complete Agent Life cross-repository run."""
    profile = _load_json(profile_path, "compiled profile")
    learning = _load_json(learning_result_path, "Buddy Agent learning result")
    raw = _load_json(raw_event_path, "raw Agent Life event")
    canonical = _load_single_jsonl(canonical_event_path, "canonical Knowledge Vault event")
    graph = _load_single_jsonl(graph_record_path, "Knowledge Vault graph record")
    arena = _load_json(arena_receipt_path, "Buddy Agent arena receipt")
    score = _load_json(score_receipt_path, "Buddy Brain score receipt")

    _require(profile.get("schema") == PROFILE_SCHEMA, "compiled profile schema is unsupported")
    profile_sha = str(profile.get("source_sha256", "")).strip()
    _require(bool(profile_sha), "compiled profile is missing source_sha256")
    agent = profile.get("agent")
    _require(isinstance(agent, dict), "compiled profile is missing agent identity")
    agent_id = str(agent.get("id", "")).strip() if isinstance(agent, dict) else ""
    _require(bool(agent_id), "compiled profile is missing agent.id")

    _require(learning.get("applied") is True, "Buddy Agent did not apply the evidenced outcome")
    _require(learning.get("duplicate") is not True, "Buddy Agent treated the proof outcome as duplicate")
    _require(raw.get("schema") == RAW_EVENT_SCHEMA, "raw Agent Life event schema is unsupported")
    _require(raw.get("agent_id") == agent_id, "raw event agent identity does not match the profile")
    _require(raw.get("profile_sha256") == profile_sha, "raw event profile hash does not match")
    _require(raw.get("subject") == {"type": "tool", "id": "github"}, "raw event subject is not tool:github")
    authority = raw.get("authority")
    _require(
        isinstance(authority, dict)
        and authority.get("kind") == "verifier"
        and authority.get("actor_id") == "agent-life-cross-repo-e2e",
        "raw event authority is not the independent cross-repo verifier",
    )
    _require(isinstance(raw.get("evidence"), list) and bool(raw["evidence"]), "raw event lacks evidence")

    _require(canonical.get("event_type") == "agent_life_updated", "Knowledge Vault did not adapt agent_life_updated")
    payload = canonical.get("payload")
    _require(isinstance(payload, dict), "canonical event payload is missing")
    _require(payload.get("agent_id") == agent_id, "canonical event agent identity changed")
    _require(payload.get("profile_sha256") == profile_sha, "canonical event profile hash changed")
    _require(payload.get("subject_target") == "tool:github", "canonical event lost subject scope")

    links = graph.get("links")
    _require(isinstance(links, list), "graph record links are missing")
    link_targets = {
        str(item.get("target"))
        for item in links
        if isinstance(item, dict) and isinstance(item.get("target"), str)
    }
    normalized_agent = "".join(character if character.isalnum() else "-" for character in agent_id.lower())
    while "--" in normalized_agent:
        normalized_agent = normalized_agent.replace("--", "-")
    normalized_agent = normalized_agent.strip("-") or "unnamed"
    _require(f"agent:{normalized_agent}" in link_targets, "graph record lost persistent agent identity")
    _require("tool:github" in link_targets, "graph record lost learned subject scope")
    _require("concept:knowledge-vault" in link_targets, "graph record lost compiling provenance")
    provenance = graph.get("provenance")
    _require(
        isinstance(provenance, dict) and provenance.get("source") == canonical.get("event_id"),
        "graph provenance does not point to the canonical event",
    )

    _require(arena.get("schema") == ARENA_SCHEMA, "arena receipt schema is unsupported")
    _require(arena.get("mode") == "cortex-off", "arena did not run cortex-off")
    _require(arena.get("agent_id") == agent_id, "arena agent identity does not match")
    _require(arena.get("profile_sha256") == profile_sha, "arena profile hash does not match")
    _require(arena.get("passed") is True and arena.get("passed_count") == 6, "arena did not pass all six scenarios")

    _require(score.get("schema") == SCORE_SCHEMA, "score receipt schema is unsupported")
    _require(score.get("agent_id") == agent_id, "score agent identity does not match")
    _require(score.get("profile_sha256") == profile_sha, "score profile hash does not match")
    _require(score.get("source_receipt_sha256") == arena.get("receipt_sha256"), "score is not bound to the arena receipt")
    _require(
        score.get("passed") is True and score.get("score") == 100 and score.get("readiness") == "green",
        "Buddy Brain did not independently award a green 100/100 score",
    )

    required_components = {
        "buddy-universal-agent-profile",
        "buddy-agent",
        "knowledge-vault",
        "buddy-brain",
    }
    _require(set(component_shas) == required_components, "component SHA set is incomplete")
    _require(all(value.strip() for value in component_shas.values()), "component SHAs must be non-empty")

    evidence_paths = {
        "compiled_profile": profile_path,
        "learning_result": learning_result_path,
        "raw_life_event": raw_event_path,
        "canonical_event": canonical_event_path,
        "graph_record": graph_record_path,
        "arena_receipt": arena_receipt_path,
        "score_receipt": score_receipt_path,
    }
    receipt: dict[str, Any] = {
        "schema": CROSS_REPO_SCHEMA,
        "passed": True,
        "agent_id": agent_id,
        "profile_sha256": profile_sha,
        "components": dict(sorted(component_shas.items())),
        "checks": {
            "buap_profile_compiled": True,
            "buddy_agent_outcome_applied": True,
            "knowledge_vault_event_adapted": True,
            "knowledge_vault_graph_linked": True,
            "buddy_agent_cortex_off_arena_passed": True,
            "buddy_brain_independent_score": 100,
        },
        "evidence_sha256": {
            name: _file_sha256(path) for name, path in sorted(evidence_paths.items())
        },
        "source_receipts": {
            "raw_event_id": str(raw.get("event_id", "")),
            "canonical_event_id": str(canonical.get("event_id", "")),
            "arena_receipt_sha256": str(arena.get("receipt_sha256", "")),
            "score_receipt_sha256": str(score.get("score_sha256", "")),
        },
        "claim_boundary": (
            "This proves the exact four-repository Agent Life v1 integration and six deterministic "
            "cortex-off behaviors for the tested profile. It does not establish consciousness, "
            "subjective feeling, general intelligence, or Norn parity."
        ),
    }
    receipt["receipt_sha256"] = _digest(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the complete Agent Life cross-repository proof chain.")
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--learning-result", type=Path, required=True)
    parser.add_argument("--raw-event", type=Path, required=True)
    parser.add_argument("--canonical-event", type=Path, required=True)
    parser.add_argument("--graph-record", type=Path, required=True)
    parser.add_argument("--arena-receipt", type=Path, required=True)
    parser.add_argument("--score-receipt", type=Path, required=True)
    parser.add_argument("--buap-sha", required=True)
    parser.add_argument("--buddy-agent-sha", required=True)
    parser.add_argument("--knowledge-vault-sha", required=True)
    parser.add_argument("--buddy-brain-sha", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = verify_cross_repo_chain(
            profile_path=args.profile,
            learning_result_path=args.learning_result,
            raw_event_path=args.raw_event,
            canonical_event_path=args.canonical_event,
            graph_record_path=args.graph_record,
            arena_receipt_path=args.arena_receipt,
            score_receipt_path=args.score_receipt,
            component_shas={
                "buddy-universal-agent-profile": args.buap_sha,
                "buddy-agent": args.buddy_agent_sha,
                "knowledge-vault": args.knowledge_vault_sha,
                "buddy-brain": args.buddy_brain_sha,
            },
        )
    except (CrossRepoVerificationError, OSError) as error:
        parser.error(str(error))
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
