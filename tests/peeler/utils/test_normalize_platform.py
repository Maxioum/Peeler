from typing import Tuple

import pytest
from click import ClickException
from pytest import mark

from peeler.schema import blender_manifest_json_schema
from peeler.utils import (
    _BLENDER_TO_WHEEL_PLATFORM_TAGS,
    normalize_blender_supported_platform,
    normalize_package_platform_tag,
)


def test_schema_supported_platfrom() -> None:
    """Assert that the comparison table match dthe json schema specifications."""
    blender_manifest_schema = blender_manifest_json_schema()
    supported_platforms = blender_manifest_schema["properties"]["platforms"]["items"][
        "enum"
    ]

    assert set(_BLENDER_TO_WHEEL_PLATFORM_TAGS.keys()) == set(supported_platforms)


@mark.parametrize(
    ("platform", "expected_result"),
    (
        [
            ("windows-x64", ("win", "amd64")),
            ("windows-arm64", ("win", "32")),
            ("linux-x64", ("manylinux", "x86_64")),
            ("macos-arm64", ("macosx", "arm64")),
            ("macos-x64", ("macosx", "x86_64")),
        ]
    ),
)
def test_normalize_blender_supported_platform(
    platform: str, expected_result: Tuple[str, str]
) -> None:
    assert normalize_blender_supported_platform(platform) == expected_result


@mark.parametrize(
    ("platform"),
    (
        [
            "windows",
            "any",
            "",
        ]
    ),
)
def test_normalize_blender_supported_platform_raises(platform: str) -> None:
    with pytest.raises(ClickException):
        normalize_blender_supported_platform(platform)


@pytest.mark.parametrize(
    ("platform_tag", "expected_result"),
    (
        [
            # --- macOS variants ---
            ("macosx_11_0_arm64", ("macosx", "11_0", "arm64")),
            ("macosx_10_9_x86_64", ("macosx", "10_9", "x86_64")),
            ("macosx_10_10_universal2", ("macosx", "10_10", "universal2")),
            ("macosx_14_2_arm64", ("macosx", "14_2", "arm64")),
            ("macosx_10_9_intel", ("macosx", "10_9", "intel")),
            ("macosx_11_0_universal2", ("macosx", "11_0", "universal2")),
            # --- manylinux variants ---
            ("manylinux1_x86_64", ("manylinux", "1", "x86_64")),
            ("manylinux2010_x86_64", ("manylinux", "2010", "x86_64")),
            ("manylinux2014_aarch64", ("manylinux", "2014", "aarch64")),
            ("manylinux_2_17_x86_64", ("manylinux", "2_17", "x86_64")),
            ("manylinux_2_5_aarch64", ("manylinux", "2_5", "aarch64")),
            # --- musllinux variants ---
            ("musllinux_1_1_aarch64", ("musllinux", "1_1", "aarch64")),
            ("musllinux_1_2_x86_64", ("musllinux", "1_2", "x86_64")),
            # --- plain linux (non-many/musl) ---
            ("linux_x86_64", ("linux", None, "x86_64")),
            ("linux_aarch64", ("linux", None, "aarch64")),
            # --- Windows variants ---
            ("win_amd64", ("win", None, "amd64")),
            ("win32", ("win", None, "32")),
            ("win_arm64", ("win", None, "arm64")),
            ("win_arm32", ("win", None, "arm32")),
            # --- universal wheels ---
            ("any", ("any", None, None)),
            # --- edge / uncommon formats ---
            ("manylinux_2_17-x86_64", ("manylinux", "2_17", "x86_64")),
            ("macosx-10_9-x86_64", ("macosx", "10_9", "x86_64")),
        ]
    ),
)
def test_normalize_package_platform_tag(
    platform_tag: str, expected_result: Tuple[str, str | None, str | None]
) -> None:
    assert normalize_package_platform_tag(platform_tag) == expected_result


@mark.parametrize(
    ("platform_tag"),
    (
        [
            # too vague / missing arch
            "win",
            "macosx",
            "manylinux",
            "linux",
            # separators without content
            "win-",
            "win_",
            # unexpected suffix
            "any_extra",
            # uppercase
            "MACOSX_11_0_ARM64",
            "Win_AMD64",
            # .whl suffix should not be tolerated
            "manylinux1_x86_64.whl",
            "win_amd64.whl",
            # punctuation / wrong separators
            "win_amd64.1",
            "musllinux_1.1_aarch64",  # dot in version
            # missing platform but has arch
            "_x86_64",
            "-x86_64",
            # duplicate archs or malformed tail
            "manylinux_2_17_x86_64-x86_64",
        ]
    ),
)
def test_normalize_package_platform_tag_raises(platform_tag: str) -> None:
    with pytest.raises(ClickException):
        normalize_package_platform_tag(platform_tag)
