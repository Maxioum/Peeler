# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

import tomlkit
from rich import print
from typer import Exit

from ..manifest.validate import validate_manifest
from ..manifest.write import export_to_blender_manifest
from ..pyproject.manifest_adapter import ManifestAdapter
from ..pyproject.validator import PyprojectValidator
from ..schema import blender_manifest_json_schema, peeler_json_schema

PYPROJECT_FILENAME = "pyproject.toml"


def _find_pyproject_file(pyproject_path: Path) -> Path:
    if pyproject_path.is_dir():
        pyproject_path = pyproject_path / PYPROJECT_FILENAME

    if not pyproject_path.is_file():
        raise Exit(
            f"No {PYPROJECT_FILENAME} found at {pyproject_path.parent.resolve()}"
        )

    return pyproject_path


def manifest_command(
    pyproject_path: Path, blender_manifest_path: Path, validate: bool
) -> None:
    """Create or update a blender_manifest.toml from a pyproject.toml.

    :param pyproject_path: the path to the `pyproject.toml` file or directory
    :param blender_manifest_path: path to the `blender_manifest.toml` file or directory to be updated or created
    """
    pyproject_path = _find_pyproject_file(pyproject_path)

    with Path(pyproject_path).open() as file:
        pyproject = tomlkit.load(file)

    if validate:
        validator = PyprojectValidator(pyproject, pyproject_path)
        validator()

    manifest_adapter = ManifestAdapter(
        pyproject, blender_manifest_json_schema(), peeler_json_schema()
    )

    doc = manifest_adapter.to_blender_manifest()

    validate_manifest(doc)

    blender_manifest_path = export_to_blender_manifest(doc, blender_manifest_path)

    blender_manifest_path = blender_manifest_path.resolve()

    print(
        f"[bright_black]Exported manifest to:[/][bright_blue] {blender_manifest_path}"
    )
