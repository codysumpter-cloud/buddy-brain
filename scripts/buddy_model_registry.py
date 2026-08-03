#!/usr/bin/env python3
"""Quarantine-first lifecycle governance for Buddy model routing."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

STATUSES = (
    "discovered",
    "quarantined",
    "benchmarked",
    "security_reviewed",
    "supervised",
    "approved",
    "deprecated",
)
ROUTABLE_STATUSES = {"supervised", "approved"}
EVIDENCE_REQUIRED_STATUSES = {
    "benchmarked",
    "security_reviewed",
    "supervised",
    "approved",
    "deprecated",
}
ALLOWED_TRANSITIONS = {
    "discovered": {"quarantined", "deprecated"},
    "quarantined": {"benchmarked", "deprecated"},
    "benchmarked": {"security_reviewed", "quarantined", "deprecated"},
    "security_reviewed": {"supervised", "quarantined", "deprecated"},
    "supervised": {"approved", "quarantined", "deprecated"},
    "approved": {"quarantined", "deprecated"},
    "deprecated": {"quarantined"},
}


@dataclass(frozen=True)
class ModelEntry:
    model_id: str
    provider: str
    model: str
    status: str = "quarantined"
    task_classes: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    discovered_at: str = ""
    reviewed_by: str = ""
    notes: str = ""

    @classmethod
    def from_dict(cls, model_id: str, payload: dict[str, Any]) -> "ModelEntry":
        entry = cls(
            model_id=model_id,
            provider=str(payload.get("provider", "")).strip(),
            model=str(payload.get("model", "")).strip(),
            status=str(payload.get("status", "quarantined")).strip(),
            task_classes=tuple(str(item) for item in payload.get("task_classes", [])),
            evidence_refs=tuple(str(item) for item in payload.get("evidence_refs", [])),
            discovered_at=str(payload.get("discovered_at", "")).strip(),
            reviewed_by=str(payload.get("reviewed_by", "")).strip(),
            notes=str(payload.get("notes", "")).strip(),
        )
        entry.validate()
        return entry

    def validate(self) -> None:
        if not self.model_id or not self.provider or not self.model:
            raise ValueError("model_id, provider, and model are required")
        if self.status not in STATUSES:
            raise ValueError(f"unsupported model status: {self.status}")
        if len(set(self.task_classes)) != len(self.task_classes):
            raise ValueError(f"duplicate task class for {self.model_id}")
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise ValueError(f"duplicate evidence reference for {self.model_id}")
        if self.status in EVIDENCE_REQUIRED_STATUSES and not self.evidence_refs:
            raise ValueError(f"status {self.status} requires evidence for {self.model_id}")
        if self.status in {"security_reviewed", "supervised", "approved"} and not self.reviewed_by:
            raise ValueError(f"status {self.status} requires reviewed_by for {self.model_id}")
        if self.status == "approved" and not self.task_classes:
            raise ValueError(f"approved model requires task_classes: {self.model_id}")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("model_id")
        payload["task_classes"] = list(self.task_classes)
        payload["evidence_refs"] = list(self.evidence_refs)
        return payload


@dataclass(frozen=True)
class ModelRegistry:
    schema: str
    default_status: str
    models: dict[str, ModelEntry]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ModelRegistry":
        schema = str(payload.get("schema", "buddy.model-registry.v1"))
        if schema != "buddy.model-registry.v1":
            raise ValueError(f"unsupported registry schema: {schema}")
        default_status = str(payload.get("default_status", "quarantined"))
        if default_status not in {"discovered", "quarantined"}:
            raise ValueError("default_status must be discovered or quarantined")
        raw_models = payload.get("models", {})
        if not isinstance(raw_models, dict):
            raise ValueError("models must be an object")
        models = {
            str(model_id): ModelEntry.from_dict(str(model_id), model_payload)
            for model_id, model_payload in raw_models.items()
        }
        return cls(schema=schema, default_status=default_status, models=models)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "default_status": self.default_status,
            "models": {
                model_id: entry.to_dict()
                for model_id, entry in sorted(self.models.items())
            },
        }


def load_registry(path: Path) -> ModelRegistry:
    return ModelRegistry.from_dict(json.loads(path.read_text(encoding="utf-8")))


def save_registry(path: Path, registry: ModelRegistry) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry.to_dict(), indent=2) + "\n", encoding="utf-8")


def discover_model(
    registry: ModelRegistry,
    *,
    model_id: str,
    provider: str,
    model: str,
    discovered_at: str = "",
    evidence_ref: str = "",
) -> ModelRegistry:
    if model_id in registry.models:
        existing = registry.models[model_id]
        if existing.provider != provider or existing.model != model:
            raise ValueError(f"model identity collision: {model_id}")
        return registry
    entry = ModelEntry(
        model_id=model_id,
        provider=provider.strip(),
        model=model.strip(),
        status=registry.default_status,
        discovered_at=discovered_at.strip(),
        evidence_refs=(evidence_ref.strip(),) if evidence_ref.strip() else (),
    )
    entry.validate()
    return replace(registry, models={**registry.models, model_id: entry})


def transition_model(
    registry: ModelRegistry,
    *,
    model_id: str,
    status: str,
    evidence_ref: str = "",
    reviewed_by: str = "",
    task_classes: tuple[str, ...] | None = None,
    notes: str | None = None,
) -> ModelRegistry:
    try:
        current = registry.models[model_id]
    except KeyError as error:
        raise ValueError(f"unknown model: {model_id}") from error
    if status not in STATUSES:
        raise ValueError(f"unsupported model status: {status}")
    if status == current.status:
        return registry
    if status not in ALLOWED_TRANSITIONS[current.status]:
        raise ValueError(f"invalid transition for {model_id}: {current.status} -> {status}")
    evidence = list(current.evidence_refs)
    if evidence_ref.strip() and evidence_ref.strip() not in evidence:
        evidence.append(evidence_ref.strip())
    updated = replace(
        current,
        status=status,
        evidence_refs=tuple(evidence),
        reviewed_by=reviewed_by.strip() or current.reviewed_by,
        task_classes=current.task_classes if task_classes is None else tuple(task_classes),
        notes=current.notes if notes is None else notes.strip(),
    )
    updated.validate()
    return replace(registry, models={**registry.models, model_id: updated})


def route_allowed(
    registry: ModelRegistry,
    model_id: str,
    task_class: str,
    *,
    allow_supervised: bool = False,
) -> bool:
    entry = registry.models.get(model_id)
    if entry is None or entry.status not in ROUTABLE_STATUSES:
        return False
    if entry.status == "supervised" and not allow_supervised:
        return False
    return task_class in entry.task_classes


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and inspect Buddy's model lifecycle registry.")
    parser.add_argument("registry", type=Path)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--check-route", nargs=2, metavar=("MODEL_ID", "TASK_CLASS"))
    parser.add_argument("--allow-supervised", action="store_true")
    args = parser.parse_args()

    registry = load_registry(args.registry)
    if args.check_route:
        model_id, task_class = args.check_route
        allowed = route_allowed(
            registry,
            model_id,
            task_class,
            allow_supervised=args.allow_supervised,
        )
        result = {"model_id": model_id, "task_class": task_class, "allowed": allowed}
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(f"{'allow' if allowed else 'deny'} {model_id} {task_class}")
        return 0 if allowed else 1

    if args.format == "json":
        print(json.dumps(registry.to_dict(), indent=2))
    else:
        for model_id, entry in sorted(registry.models.items()):
            tasks = ",".join(entry.task_classes) or "none"
            print(f"{entry.status:17} {model_id} tasks={tasks}")
        print(f"ok model-registry models={len(registry.models)} default={registry.default_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
