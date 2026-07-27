from scripts.buddy_task_economics import TaskRecord, grouped_summary


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
