import re
from pathlib import Path
from subprocess import run
from typing import List

from tomlkit.toml_file import TOMLFile
import typer
from click import format_filename
from click.exceptions import ClickException
from packaging.version import Version

from peeler.uv_utils import find_uv_bin

from ..utils import find_pyproject_file
from ..wheels.download import download_wheels
from ..wheels.lock import get_wheels_url

version_regex = r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"

PYPROJECT_FILENAME = "pyproject.toml"

# https://docs.blender.org/manual/en/dev/advanced/extensions/python_wheels.html
WHEELS_DIRECTORY = "wheels"

_MIN_UV_VERSION = Version("0.5.17")


def _resolve_wheels_dir(
    wheels_directory: Path | None,
    blender_manifest_file: Path,
    *,
    allow_non_default_name: bool = False,
) -> Path:
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
Should be next to the pyproject file {format_filename(blender_manifest_file)}
See: `https://docs.blender.org/manual/en/dev/advanced/extensions/python_wheels.html`
        """
        if allow_non_default_name:
            typer.echo(f"Warning: {msg}")
        else:
            raise ClickException(msg)

    return wheels_directory


def _check_uv_version() -> None:
    uv_bin = find_uv_bin()

    result = run([uv_bin, "version"], capture_output=True, text=True, check=True)
    output = result.stdout.strip()
    match = re.search(version_regex, output)

    if not match:
        raise ClickException(
            f"""Error when checking uv version
To use {peeler.__name__} wheels feature uv must be at least {_MIN_UV_VERSION}
Run `uv self update` to update uv"""
        )

    uv_version = Version(match.group(0))

    if uv_version < _MIN_UV_VERSION:
        import peeler

        raise ClickException(
            f"""uv version is {uv_version}
To use {peeler.__name__} wheels feature uv must be at least {_MIN_UV_VERSION}
Run `uv self update` to update uv"""
        )


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

    _check_uv_version()

    pyproject_file = find_pyproject_file(pyproject_file, allow_non_default_name=False)
    wheels_directory = _resolve_wheels_dir(
        wheels_directory, blender_manifest_file, allow_non_default_name=True
    )

    urls = get_wheels_url(pyproject_file)

    wheels_paths = download_wheels(wheels_directory, urls)

    write_wheels_path(blender_manifest_file, wheels_paths)
