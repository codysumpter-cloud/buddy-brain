import pytest

from scripts.buddy_task_economics import HarnessIdentity, TaskRecord, grouped_summary


def complete_harness(**overrides):
    values = {
        "harness": "buddy-agent",
        "effort": "medium",
        "buap_artifact_hash": "abc123",
        "runtime_adapter_version": "local-container-v1",
        "memory_strategy": "knowledge-vault-public-safe",
        "context_strategy": "compact",
        "reasoning_retention": True,
        "tool_policy_version": "policy-v1",
    }
    values.update(overrides)
    return values


def record(task_id: str, **overrides):
    values = {
        "task_id": task_id,
        "provider": "openai",
        "model": "gpt-test",
        "attempts": 1,
        "model_cost": 1.0,
        "tool_cost": 0.5,
        "elapsed_ms": 1000,
        "human_review_minutes": 5,
        "verification_passed": True,
        "artifacts_accepted": True,
        "rolled_back": False,
        "security_gate": "pass",
        "harness_identity": complete_harness(),
    }
    values.update(overrides)
    return TaskRecord.from_dict(values)


def test_verified_completion_excludes_rollbacks_and_security_blocks():
    summary = grouped_summary([
        record("ok"),
        record("rollback", rolled_back=True),
        record("blocked", security_gate="block"),
    ])
    assert summary["overall"]["verified_completions"] == 1
    assert summary["overall"]["verified_completion_rate"] == 0.3333


def test_review_cost_is_included_when_rate_is_supplied():
    summary = grouped_summary([record("one", human_review_minutes=60)], human_hour_rate=100)
    assert summary["overall"]["direct_cost"] == 1.5
    assert summary["overall"]["human_review_cost"] == 100.0
    assert summary["overall"]["cost_per_verified_completion"] == 101.5


def test_retry_rate_counts_tasks_requiring_more_than_one_attempt():
    summary = grouped_summary([record("one"), record("two", attempts=3)])
    assert summary["overall"]["retry_rate"] == 0.5
    assert summary["overall"]["attempts"] == 4


def test_same_model_with_different_harnesses_is_not_averaged_together():
    summary = grouped_summary([
        record("compact"),
        record(
            "truncate",
            harness_identity=complete_harness(
                context_strategy="truncate",
                reasoning_retention=False,
            ),
        ),
    ])
    assert summary["version"] == 2
    assert len(summary["harnesses"]) == 2
    fingerprints = {
        item["harness_identity"]["fingerprint"] for item in summary["harnesses"]
    }
    assert len(fingerprints) == 2


def test_legacy_records_remain_readable_but_are_marked_incomplete():
    legacy = record("legacy")
    payload = {
        "task_id": legacy.task_id,
        "provider": legacy.provider,
        "model": legacy.model,
        "attempts": legacy.attempts,
        "model_cost": legacy.model_cost,
        "tool_cost": legacy.tool_cost,
        "elapsed_ms": legacy.elapsed_ms,
        "human_review_minutes": legacy.human_review_minutes,
        "verification_passed": legacy.verification_passed,
        "artifacts_accepted": legacy.artifacts_accepted,
    }
    parsed = TaskRecord.from_dict(payload)
    assert parsed.harness_identity == HarnessIdentity()
    summary = grouped_summary([parsed])
    assert summary["overall"]["incomplete_harness_records"] == 1
    assert summary["harnesses"][0]["harness_identity"]["complete"] is False


def test_invalid_context_strategy_is_rejected():
    with pytest.raises(ValueError, match="context_strategy"):
        record("bad", harness_identity=complete_harness(context_strategy="rolling-mystery"))


def test_negative_elapsed_time_is_rejected():
    with pytest.raises(ValueError, match="elapsed_ms"):
        record("bad-time", elapsed_ms=-1)
