from __future__ import annotations

from hashlib import sha256
from typing import Any, Mapping


class BuddyValidationError(ValueError):
    pass


def _is_positive_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _base(asset: Mapping[str, Any], style: str) -> list[str]:
    issues: list[str] = []
    spec = asset.get("spec") if isinstance(asset, Mapping) else None
    if not isinstance(spec, Mapping):
        spec = {}
        issues.append("asset.spec must be an object")
    identity = spec.get("identity") if isinstance(spec.get("identity"), Mapping) else {}
    canvas = spec.get("canvas") if isinstance(spec.get("canvas"), Mapping) else {}
    if asset.get("version") != "1.0":
        issues.append("asset.version must be 1.0")
    if spec.get("version") != "1.0":
        issues.append("spec.version must be 1.0")
    if spec.get("style") != style:
        issues.append(f"spec.style must be {style}")
    if not identity.get("species"):
        issues.append("identity.species is required")
    if not identity.get("stage"):
        issues.append("identity.stage is required")
    if not identity.get("stylePackId"):
        issues.append("identity.stylePackId is required")
    if not _is_positive_integer(canvas.get("width")):
        issues.append("canvas.width must be a positive integer")
    if not _is_positive_integer(canvas.get("height")):
        issues.append("canvas.height must be a positive integer")
    if (asset.get("metadata") or {}).get("normalized") is not True:
        issues.append("asset must be normalized")
    frames = asset.get("frames")
    if not frames:
        issues.append("asset.frames is required")
    elif not isinstance(frames, Mapping):
        issues.append("asset.frames must be an object")
    return issues


def _frame_map(asset: Mapping[str, Any]) -> Mapping[str, Any]:
    frames = asset.get("frames")
    if isinstance(frames, Mapping):
        return frames
    return {}


def validate_ascii_asset(asset: Mapping[str, Any]) -> dict[str, Any]:
    issues = _base(asset, "ascii")
    canvas = (asset.get("spec") or {}).get("canvas") or {}
    width = canvas.get("width", 0)
    height = canvas.get("height", 0)
    for animation, frames in _frame_map(asset).items():
        if not isinstance(frames, list) or not frames:
            issues.append(f"{animation}: frames must be non-empty")
            continue
        for index, frame in enumerate(frames):
            lines = frame.get("lines") if isinstance(frame, dict) else None
            if not isinstance(lines, list):
                issues.append(f"{animation}[{index}]: lines must be a list")
                continue
            if len(lines) != height:
                issues.append(f"{animation}[{index}]: expected {height} lines")
            for line_number, line in enumerate(lines):
                if not isinstance(line, str) or len(line) != width:
                    issues.append(f"{animation}[{index}].line[{line_number}] expected width {width}")
    return {"valid": not issues, "issues": issues}


def validate_pixel_asset(asset: Mapping[str, Any]) -> dict[str, Any]:
    issues = _base(asset, "pixel")
    canvas = (asset.get("spec") or {}).get("canvas") or {}
    width = canvas.get("width", 0)
    height = canvas.get("height", 0)
    for animation, frames in _frame_map(asset).items():
        if not isinstance(frames, list) or not frames:
            issues.append(f"{animation}: frames must be non-empty")
            continue
        for index, frame in enumerate(frames):
            if not isinstance(frame, dict):
                issues.append(f"{animation}[{index}]: frame must be an object")
                continue
            if frame.get("width") != width:
                issues.append(f"{animation}[{index}]: frame width must equal canvas width")
            if frame.get("height") != height:
                issues.append(f"{animation}[{index}]: frame height must equal canvas height")
            if not frame.get("imagePath"):
                issues.append(f"{animation}[{index}]: imagePath is required")
    return {"valid": not issues, "issues": issues}


def _clamp_score(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


def score_ascii_asset(asset: Mapping[str, Any]) -> dict[str, float]:
    validation = validate_ascii_asset(asset)
    if not validation["valid"]:
        return {
            "readability": 0.0,
            "silhouette": 0.0,
            "animation": 0.0,
            "charm": 0.0,
            "styleCompliance": 0.0,
        }
    metadata = asset.get("metadata") or {}
    frames = _frame_map(asset)
    total_frames = sum(len(frame_list) for frame_list in frames.values() if isinstance(frame_list, list))
    animation_count = len(frames)
    return {
        "readability": _clamp_score(float(metadata.get("readabilityScore", 0.85))),
        "silhouette": _clamp_score(float(metadata.get("silhouetteScore", 0.85))),
        "animation": _clamp_score(float(metadata.get("animationScore", 0.65)) + min(total_frames, 8) * 0.02),
        "charm": _clamp_score(float(metadata.get("charmScore", 0.8))),
        "styleCompliance": _clamp_score(0.75 + min(animation_count, 4) * 0.05),
    }


def score_pixel_asset(asset: Mapping[str, Any]) -> dict[str, float]:
    validation = validate_pixel_asset(asset)
    if not validation["valid"]:
        return {
            "readability": 0.0,
            "silhouette": 0.0,
            "animation": 0.0,
            "charm": 0.0,
            "styleCompliance": 0.0,
        }
    metadata = asset.get("metadata") or {}
    color_count = metadata.get("colorCount", 16)
    palette_score = 1.0 if isinstance(color_count, int) and not isinstance(color_count, bool) and color_count <= 16 else 0.65
    frames = _frame_map(asset)
    total_frames = sum(len(frame_list) for frame_list in frames.values() if isinstance(frame_list, list))
    return {
        "readability": _clamp_score(0.88),
        "silhouette": _clamp_score(0.86),
        "animation": _clamp_score(0.66 + min(total_frames, 8) * 0.025),
        "charm": _clamp_score(0.82),
        "styleCompliance": _clamp_score(palette_score),
    }


def _asset_key(asset: Mapping[str, Any]) -> str:
    spec = asset.get("spec") or {}
    identity = spec.get("identity") or {}
    species = identity.get("species", "unknown")
    stage = identity.get("stage", "unknown")
    style = spec.get("style", "unknown")
    digest = sha256(repr(asset).encode("utf-8")).hexdigest()[:12]
    return f"{style}:{species}:{stage}:{digest}"


def make_asset_provenance_receipt(asset: Mapping[str, Any], source: str, generator: str) -> dict[str, Any]:
    spec = asset.get("spec") or {}
    identity = spec.get("identity") or {}
    return {
        "kind": "buddy_visual_asset_receipt",
        "asset": f"{identity.get('species')}:{identity.get('stage')}",
        "source": source,
        "generator": generator,
        "style": spec.get("style"),
        "stylePackId": identity.get("stylePackId"),
    }


def make_asset_compilation_receipt(
    asset: Mapping[str, Any], source: str, compiler: str = "buddy_art.compiler"
) -> dict[str, Any]:
    receipt = make_asset_provenance_receipt(asset, source=source, generator=compiler)
    receipt["kind"] = "buddy_visual_asset_compilation_receipt"
    receipt["compiledAssetId"] = _asset_key(asset)
    return receipt


def compile_ascii_asset(
    asset: Mapping[str, Any], source: str, compiler: str = "buddy_art.compiler"
) -> dict[str, Any]:
    validation = validate_ascii_asset(asset)
    if not validation["valid"]:
        raise BuddyValidationError("ASCII asset must be valid before compilation")
    scores = score_ascii_asset(asset)
    return {
        "version": "1.0",
        "kind": "compiled_buddy_visual_asset",
        "compiledAssetId": _asset_key(asset),
        "style": "ascii",
        "spec": asset.get("spec"),
        "frames": asset.get("frames"),
        "previewFrame": asset.get("previewFrame"),
        "validation": validation,
        "scores": scores,
        "metadata": {"normalized": True, "compiled": True},
        "receipt": make_asset_compilation_receipt(asset, source=source, compiler=compiler),
    }


def compile_pixel_asset(
    asset: Mapping[str, Any], source: str, compiler: str = "buddy_art.compiler"
) -> dict[str, Any]:
    validation = validate_pixel_asset(asset)
    if not validation["valid"]:
        raise BuddyValidationError("Pixel asset must be valid before compilation")
    scores = score_pixel_asset(asset)
    return {
        "version": "1.0",
        "kind": "compiled_buddy_visual_asset",
        "compiledAssetId": _asset_key(asset),
        "style": "pixel",
        "spec": asset.get("spec"),
        "frames": asset.get("frames"),
        "previewFrame": asset.get("previewFrame"),
        "validation": validation,
        "scores": scores,
        "metadata": {"normalized": True, "compiled": True},
        "receipt": make_asset_compilation_receipt(asset, source=source, compiler=compiler),
    }
