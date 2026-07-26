from pathlib import Path

import pytest

from peeler.pyproject.parser import get_supported_platforms
from peeler.utils import parse_blender_supported_platform


@pytest.mark.parametrize(
    "pyproject_path",
    [
        "pyproject_minimal.toml",
    ],
    indirect=True,
)
def test_get_supported_platforms(pyproject_path: Path) -> None:

    platforms = get_supported_platforms(pyproject_path, allow_non_default_name=True)

    assert platforms

    for platform in platforms:
        assert parse_blender_supported_platform(platform)


@pytest.mark.parametrize(
    "pyproject_path",
    [
        "pyproject_no_manifest_table.toml",
        "pyproject_no_peeler_table.toml",
        "pyproject_peeler_table_empty.toml",
        "pyproject_no_platforms.toml",
    ],
    indirect=True,
)
def test_get_supported_platforms_empty(pyproject_path: Path) -> None:

    platforms = get_supported_platforms(pyproject_path, allow_non_default_name=True)

    assert not platforms
