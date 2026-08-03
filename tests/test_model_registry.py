import json
from pathlib import Path

import pytest

from scripts.buddy_model_registry import (
    ModelRegistry,
    discover_model,
    load_registry,
    route_allowed,
    save_registry,
    transition_model,
)


def empty_registry() -> ModelRegistry:
    return ModelRegistry.from_dict(
        {
            "schema": "buddy.model-registry.v1",
            "default_status": "quarantined",
            "models": {},
        }
    )


def test_discovered_provider_models_default_to_quarantine():
    registry = discover_model(
        empty_registry(),
        model_id="provider/new-model",
        provider="provider",
        model="new-model",
        discovered_at="2026-08-03",
    )
    assert registry.models["provider/new-model"].status == "quarantined"
    assert route_allowed(registry, "provider/new-model", "bounded_edit") is False


def test_model_cannot_skip_benchmark_and_security_review():
    registry = discover_model(
        empty_registry(),
        model_id="provider/model",
        provider="provider",
        model="model",
    )
    with pytest.raises(ValueError, match="invalid transition"):
        transition_model(
            registry,
            model_id="provider/model",
            status="approved",
            evidence_ref="evidence://shortcut",
            reviewed_by="reviewer",
            task_classes=("bounded_edit",),
        )


def test_full_lifecycle_requires_evidence_and_explicit_review():
    registry = discover_model(
        empty_registry(),
        model_id="provider/model",
        provider="provider",
        model="model",
    )
    with pytest.raises(ValueError, match="requires evidence"):
        transition_model(registry, model_id="provider/model", status="benchmarked")

    registry = transition_model(
        registry,
        model_id="provider/model",
        status="benchmarked",
        evidence_ref="benchmark://suite-v1",
    )
    with pytest.raises(ValueError, match="requires reviewed_by"):
        transition_model(
            registry,
            model_id="provider/model",
            status="security_reviewed",
            evidence_ref="security://review-v1",
        )
    registry = transition_model(
        registry,
        model_id="provider/model",
        status="security_reviewed",
        evidence_ref="security://review-v1",
        reviewed_by="peppermint-butler",
    )
    registry = transition_model(
        registry,
        model_id="provider/model",
        status="supervised",
        evidence_ref="supervised://run-set-v1",
        reviewed_by="neptr",
        task_classes=("bounded_edit",),
    )
    assert route_allowed(registry, "provider/model", "bounded_edit") is False
    assert (
        route_allowed(
            registry,
            "provider/model",
            "bounded_edit",
            allow_supervised=True,
        )
        is True
    )
    registry = transition_model(
        registry,
        model_id="provider/model",
        status="approved",
        evidence_ref="approval://routing-v1",
        reviewed_by="prismo",
    )
    assert route_allowed(registry, "provider/model", "bounded_edit") is True
    assert route_allowed(registry, "provider/model", "security_review") is False


def test_approved_model_can_be_requarantined_immediately():
    registry = ModelRegistry.from_dict(
        {
            "schema": "buddy.model-registry.v1",
            "default_status": "quarantined",
            "models": {
                "provider/model": {
                    "provider": "provider",
                    "model": "model",
                    "status": "approved",
                    "task_classes": ["bounded_edit"],
                    "evidence_refs": ["approval://v1"],
                    "reviewed_by": "prismo",
                }
            },
        }
    )
    registry = transition_model(
        registry,
        model_id="provider/model",
        status="quarantined",
        notes="Unexpected tool behavior under observation.",
    )
    assert registry.models["provider/model"].status == "quarantined"
    assert route_allowed(registry, "provider/model", "bounded_edit") is False


def test_registry_round_trip_is_deterministic(tmp_path: Path):
    registry = discover_model(
        empty_registry(),
        model_id="provider/model",
        provider="provider",
        model="model",
        evidence_ref="discovery://provider-catalog",
    )
    path = tmp_path / "registry.json"
    save_registry(path, registry)
    loaded = load_registry(path)
    assert loaded == registry
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert list(payload["models"]) == ["provider/model"]


def test_identity_collision_is_rejected():
    registry = discover_model(
        empty_registry(),
        model_id="provider/model",
        provider="provider",
        model="model",
    )
    with pytest.raises(ValueError, match="identity collision"):
        discover_model(
            registry,
            model_id="provider/model",
            provider="other-provider",
            model="different-model",
        )
