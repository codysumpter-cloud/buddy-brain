from __future__ import annotations

from copy import deepcopy

import pytest

from buddy_art.validation import (
    BuddyValidationError,
    compile_ascii_asset,
    compile_pixel_asset,
    make_asset_compilation_receipt,
    make_asset_provenance_receipt,
    score_ascii_asset,
    score_pixel_asset,
    validate_ascii_asset,
    validate_pixel_asset,
)


def ascii_asset():
    lines = ["                "] * 16
    return {
        "version": "1.0",
        "spec": {
            "version": "1.0",
            "style": "ascii",
            "identity": {
                "species": "trex",
                "stage": "baby",
                "stylePackId": "ascii-trex-chibi-v1",
            },
            "canvas": {"width": 16, "height": 16, "frameCount": 1, "fps": 4},
        },
        "frames": {"idle": [{"lines": lines}]},
        "previewFrame": {"lines": lines},
        "metadata": {"normalized": True},
    }


def pixel_asset():
    return {
        "version": "1.0",
        "spec": {
            "version": "1.0",
            "style": "pixel",
            "identity": {
                "species": "trex",
                "stage": "baby",
                "stylePackId": "pixel-tamagotchi-v1",
            },
            "canvas": {"width": 32, "height": 32, "frameCount": 1, "fps": 6},
        },
        "frames": {
            "idle": [
                {
                    "frameId": "trex-baby-idle-0",
                    "width": 32,
                    "height": 32,
                    "imagePath": "assets/buddies/trex/baby/idle-0.png",
                }
            ]
        },
        "previewFrame": {
            "frameId": "trex-baby-idle-0",
            "width": 32,
            "height": 32,
            "imagePath": "assets/buddies/trex/baby/idle-0.png",
        },
        "metadata": {"normalized": True, "colorCount": 2},
    }


def test_valid_ascii_asset_passes():
    result = validate_ascii_asset(ascii_asset())
    assert result["valid"] is True
    assert result["issues"] == []


def test_invalid_ascii_width_fails():
    asset = ascii_asset()
    asset["frames"]["idle"][0]["lines"][0] = "too short"
    result = validate_ascii_asset(asset)
    assert result["valid"] is False
    assert "expected width" in result["issues"][0]


def test_valid_pixel_asset_passes():
    result = validate_pixel_asset(pixel_asset())
    assert result["valid"] is True
    assert result["issues"] == []


def test_invalid_pixel_frame_size_fails():
    asset = pixel_asset()
    asset["frames"]["idle"][0]["width"] = 16
    result = validate_pixel_asset(asset)
    assert result["valid"] is False
    assert "frame width" in result["issues"][0]


def test_non_object_ascii_frames_return_validation_issue_without_crashing():
    asset = ascii_asset()
    asset["frames"] = []
    result = validate_ascii_asset(asset)
    assert result["valid"] is False
    assert "asset.frames must be an object" in result["issues"]


def test_non_object_pixel_frames_return_validation_issue_without_crashing():
    asset = pixel_asset()
    asset["frames"] = "not-a-frame-map"
    result = validate_pixel_asset(asset)
    assert result["valid"] is False
    assert "asset.frames must be an object" in result["issues"]


def test_boolean_ascii_canvas_dimensions_are_rejected():
    asset = ascii_asset()
    asset["spec"]["canvas"]["width"] = True
    result = validate_ascii_asset(asset)
    assert result["valid"] is False
    assert "canvas.width must be a positive integer" in result["issues"]


def test_boolean_pixel_canvas_dimensions_are_rejected():
    asset = pixel_asset()
    asset["spec"]["canvas"]["height"] = True
    result = validate_pixel_asset(asset)
    assert result["valid"] is False
    assert "canvas.height must be a positive integer" in result["issues"]


def test_ascii_scoring_returns_contract_scores():
    scores = score_ascii_asset(ascii_asset())
    assert set(scores) == {
        "readability",
        "silhouette",
        "animation",
        "charm",
        "styleCompliance",
    }
    assert all(0.0 <= value <= 1.0 for value in scores.values())
    assert scores["readability"] > 0.0


def test_pixel_scoring_returns_contract_scores():
    scores = score_pixel_asset(pixel_asset())
    assert set(scores) == {
        "readability",
        "silhouette",
        "animation",
        "charm",
        "styleCompliance",
    }
    assert all(0.0 <= value <= 1.0 for value in scores.values())
    assert scores["styleCompliance"] == 1.0


def test_compile_ascii_asset_requires_valid_asset():
    asset = ascii_asset()
    asset["frames"] = []
    with pytest.raises(BuddyValidationError):
        compile_ascii_asset(asset, source="test")


def test_compile_ascii_asset_produces_runtime_safe_payload():
    compiled = compile_ascii_asset(ascii_asset(), source="test")
    assert compiled["kind"] == "compiled_buddy_visual_asset"
    assert compiled["style"] == "ascii"
    assert compiled["validation"]["valid"] is True
    assert compiled["metadata"]["compiled"] is True
    assert compiled["receipt"]["kind"] == "buddy_visual_asset_compilation_receipt"
    assert compiled["compiledAssetId"] == compiled["receipt"]["compiledAssetId"]


def test_compile_pixel_asset_requires_valid_asset():
    asset = pixel_asset()
    asset["frames"]["idle"][0]["imagePath"] = ""
    with pytest.raises(BuddyValidationError):
        compile_pixel_asset(asset, source="test")


def test_compile_pixel_asset_produces_runtime_safe_payload():
    compiled = compile_pixel_asset(pixel_asset(), source="test")
    assert compiled["kind"] == "compiled_buddy_visual_asset"
    assert compiled["style"] == "pixel"
    assert compiled["validation"]["valid"] is True
    assert compiled["metadata"]["normalized"] is True
    assert compiled["scores"]["styleCompliance"] == 1.0
    assert compiled["receipt"]["kind"] == "buddy_visual_asset_compilation_receipt"


def test_provenance_receipt_records_source_and_style_pack():
    receipt = make_asset_provenance_receipt(
        pixel_asset(), source="pixellab-candidate", generator="validator-test"
    )
    assert receipt["kind"] == "buddy_visual_asset_receipt"
    assert receipt["source"] == "pixellab-candidate"
    assert receipt["stylePackId"] == "pixel-tamagotchi-v1"


def test_compilation_receipt_records_compiled_asset_id():
    receipt = make_asset_compilation_receipt(
        pixel_asset(), source="pixellab-candidate", compiler="compiler-test"
    )
    assert receipt["kind"] == "buddy_visual_asset_compilation_receipt"
    assert receipt["generator"] == "compiler-test"
    assert receipt["compiledAssetId"].startswith("pixel:trex:baby:")
