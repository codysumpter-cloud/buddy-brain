from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from agent_life_cross_repo_verify import (  # noqa: E402
    CrossRepoVerificationError,
    verify_cross_repo_chain,
)


class AgentLifeCrossRepoVerifyTests(unittest.TestCase):
    def _write(self, root: Path, name: str, value: object, *, jsonl: bool = False) -> Path:
        path = root / name
        if jsonl:
            path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
        else:
            path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def _fixtures(self, root: Path) -> dict[str, Path]:
        profile_hash = "profile-sha"
        agent_id = "buddy-e2e"
        profile = {
            "schema": "prismtek-agent-life-profile-v1",
            "source_sha256": profile_hash,
            "agent": {"id": agent_id},
        }
        learning = {"applied": True, "duplicate": False}
        raw = {
            "schema": "prismtek-agent-life-event-v1",
            "event_id": "e2e-positive",
            "agent_id": agent_id,
            "profile_sha256": profile_hash,
            "subject": {"type": "tool", "id": "github"},
            "authority": {"kind": "verifier", "actor_id": "agent-life-cross-repo-e2e"},
            "evidence": [{"type": "receipt", "ref": "github-actions:e2e"}],
        }
        canonical = {
            "event_id": "evt-agent-life-e2e-positive",
            "event_type": "agent_life_updated",
            "payload": {
                "agent_id": agent_id,
                "profile_sha256": profile_hash,
                "subject_target": "tool:github",
            },
        }
        graph = {
            "links": [
                {"target": "agent:buddy-e2e"},
                {"target": "tool:github"},
                {"target": "concept:knowledge-vault"},
            ],
            "provenance": {"source": canonical["event_id"]},
        }
        arena = {
            "schema": "prismtek-agent-life-arena-v1",
            "mode": "cortex-off",
            "agent_id": agent_id,
            "profile_sha256": profile_hash,
            "passed": True,
            "passed_count": 6,
            "receipt_sha256": "arena-sha",
        }
        score = {
            "schema": "prismtek-agent-life-arena-score-v1",
            "agent_id": agent_id,
            "profile_sha256": profile_hash,
            "source_receipt_sha256": arena["receipt_sha256"],
            "passed": True,
            "score": 100,
            "readiness": "green",
            "score_sha256": "score-sha",
        }
        return {
            "profile_path": self._write(root, "profile.json", profile),
            "learning_result_path": self._write(root, "learning.json", learning),
            "raw_event_path": self._write(root, "raw.json", raw),
            "canonical_event_path": self._write(root, "canonical.jsonl", canonical, jsonl=True),
            "graph_record_path": self._write(root, "graph.jsonl", graph, jsonl=True),
            "arena_receipt_path": self._write(root, "arena.json", arena),
            "score_receipt_path": self._write(root, "score.json", score),
        }

    def _verify(self, paths: dict[str, Path]) -> dict[str, object]:
        return verify_cross_repo_chain(
            **paths,
            component_shas={
                "buddy-universal-agent-profile": "buap-sha",
                "buddy-agent": "agent-sha",
                "knowledge-vault": "vault-sha",
                "buddy-brain": "brain-sha",
            },
        )

    def test_valid_four_repo_chain_emits_bound_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = self._fixtures(Path(directory))
            receipt = self._verify(paths)
            self.assertTrue(receipt["passed"])
            self.assertEqual(receipt["schema"], "prismtek-agent-life-cross-repo-e2e-v1")
            self.assertEqual(receipt["checks"]["buddy_brain_independent_score"], 100)
            self.assertEqual(len(receipt["evidence_sha256"]), 7)
            self.assertEqual(set(receipt["components"]), {
                "buddy-universal-agent-profile",
                "buddy-agent",
                "knowledge-vault",
                "buddy-brain",
            })
            self.assertTrue(receipt["receipt_sha256"])

    def test_profile_hash_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = self._fixtures(Path(directory))
            raw = json.loads(paths["raw_event_path"].read_text(encoding="utf-8"))
            raw["profile_sha256"] = "wrong"
            paths["raw_event_path"].write_text(json.dumps(raw), encoding="utf-8")
            with self.assertRaisesRegex(CrossRepoVerificationError, "raw event profile hash"):
                self._verify(paths)

    def test_missing_subject_graph_link_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = self._fixtures(Path(directory))
            graph = json.loads(paths["graph_record_path"].read_text(encoding="utf-8"))
            graph["links"] = [item for item in graph["links"] if item["target"] != "tool:github"]
            paths["graph_record_path"].write_text(json.dumps(graph) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(CrossRepoVerificationError, "learned subject scope"):
                self._verify(paths)


if __name__ == "__main__":
    unittest.main()
