# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import List

import typer
from click import format_filename
from click.exceptions import ClickException
from tomlkit.toml_file import TOMLFile

from peeler.pyproject.update import update_requires_python
from peeler.pyproject.parser import PyprojectParser
from peeler.utils import find_pyproject_file, restore_file
from peeler.uv_utils import check_uv_version
from peeler.wheels.download import download_wheels
from peeler.wheels.lock import get_wheels_url

PYPROJECT_FILENAME = "pyproject.toml"

# https://docs.blender.org/manual/en/dev/advanced/extensions/python_wheels.html
WHEELS_DIRECTORY = "wheels"


def _resolve_wheels_dir(
    wheels_directory: Path | None,
    blender_manifest_file: Path,
    *,
    allow_non_default_name: bool = False,
) -> Path:
    """Return a complete path of the wheels directory.

    :param wheels_directory: the original path given by the user
    :param blender_manifest_file: the path the blender_manifest.toml file, the wheels directory should be next to this file.
    :param allow_non_default_name: whether to allow the directory to be named other than `wheels`, defaults to False, see `https://docs.blender.org/manual/en/dev/advanced/extensions/python_wheels.html`
    :raises ClickException: if allow_non_default_name is False and the given path is not named `wheels`
    :raises ClickException: if the given path is not None and not a directory
    :return: The valid path

    >>> _resolve_wheels_dir(
    ...     None,
    ...     Path("/path/to/manifest/blender_manifest.toml"),
    ...     allow_non_default_name=False,
    ... )
    Path("/path/to/manifest/wheels")
    >>> _resolve_wheels_dir(
    ...     Path("/path/to/manifest/wheels/"),
    ...     Path("/path/to/manifest/blender_manifest.toml"),
    ...     allow_non_default_name=False,
    ... )
    Path("/path/to/manifest/wheels/")
    >>> _resolve_wheels_dir(
    ...     Path("/path/to/wheels/"),
    ...     Path("/path/to/other_dir/blender_manifest.toml"),
    ...     allow_non_default_name=True,
    ... )
    Path("/path/to/wheels/")
    >>> _resolve_wheels_dir(
    ...     Path("/path/to/wheels/"),
    ...     Path("/path/to/other_dir/blender_manifest.toml"),
    ...     allow_non_default_name=False,
    ... )
    ClickException: The wheels directory "/path/to/wheels" Should be next to the blender_manifest.toml file ...
    """
    if wheels_directory is None:
        wheels_directory = blender_manifest_file.parent / WHEELS_DIRECTORY

    wheels_directory.mkdir(parents=True, exist_ok=True)

    if not wheels_directory.is_dir():
        raise ClickException(
            f"{format_filename(wheels_directory)} is not a directory !"
        )

    if not wheels_directory.name == WHEELS_DIRECTORY:
        msg = f"""The wheels directory {format_filename(wheels_directory)}
Should be named : `{WHEELS_DIRECTORY}` not `{wheels_directory.name}`
See: `https://docs.blender.org/manual/en/dev/advanced/extensions/python_wheels.html`
        """
        if allow_non_default_name:
            typer.echo(f"Warning: {msg}")
        else:
            raise ClickException(msg)

    if not wheels_directory.parent == blender_manifest_file.parent:
        msg = f"""The wheels directory {format_filename(wheels_directory)}
Should be next to the blender_manifest.toml file {format_filename(blender_manifest_file)}
See: `https://docs.blender.org/manual/en/dev/advanced/extensions/python_wheels.html`
        """
        if allow_non_default_name:
            typer.echo(f"Warning: {msg}")
        else:
            raise ClickException(msg)

    return wheels_directory


def _normalize(path: Path, dir: Path) -> str:
    return f"./{path.relative_to(dir).as_posix()}"


def write_wheels_path(blender_manifest_path: Path, wheels_paths: List[Path]) -> None:
    """Write wheels path to blender manifest.

    :param blender_manifest_path: _description_
    :param wheels_paths: _description_
    """

    if not blender_manifest_path.exists():
        raise RuntimeError(f"No blender_manifest at {blender_manifest_path}")

    file = TOMLFile(blender_manifest_path)
    doc = file.read()

    doc.update(
        {
            "wheels": [
                _normalize(wheel, blender_manifest_path.parent)
                for wheel in wheels_paths
            ]
        }
    )

    file.write(doc)


def wheels_command(
    pyproject_file: Path, blender_manifest_file: Path, wheels_directory: Path | None
) -> None:
    """Download wheel from pyproject dependency and write their paths to the blender manifest.

    :param pyproject_file: The pyproject file.
    :param blender_manifest_file: the blender manifest file
    :param wheels_directory: the directory to download wheels into.
    """

    check_uv_version()

    pyproject_file = find_pyproject_file(pyproject_file, allow_non_default_name=False)

    wheels_directory = _resolve_wheels_dir(
        wheels_directory, blender_manifest_file, allow_non_default_name=True
    )

    # temporary modify pyproject file
    # to download only supported wheels by blender
    with restore_file(pyproject_file):
        file = TOMLFile(pyproject_file)
        pyproject = PyprojectParser(file.read())
        pyproject = update_requires_python(pyproject)
        file.write(pyproject._document)

        urls = get_wheels_url(pyproject_file)

    wheels_paths = download_wheels(wheels_directory, urls)

    write_wheels_path(blender_manifest_file, wheels_paths)
