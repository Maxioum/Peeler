from pathlib import Path
import tomlkit

from typer import Exit

from ..pyproject.validator import Validator

PYPROJECT_FILENAME = "pyproject.toml"


def _find_pyproject_file(pyproject_path: Path) -> Path:
    if pyproject_path.is_dir():
        pyproject_path = pyproject_path / PYPROJECT_FILENAME

    if not pyproject_path.is_file():
        raise Exit(
            f"No {PYPROJECT_FILENAME} found at {pyproject_path.parent.resolve()}"
        )

    return pyproject_path


def manifest_command(pyproject_path: Path, blender_manifest_path: Path) -> None:
    """Create or update a blender_manifest.toml from a pyproject.toml.

    :param pyproject_path: the path to the `pyproject.toml` file or directory
    :param blender_manifest_path: path to the `blender_manifest.toml` file or directory to be updated or created
    """
    pyproject_path = _find_pyproject_file(pyproject_path)

    with Path(pyproject_path).open() as file:
        pyproject = tomlkit.load(file)

    Validator(pyproject, pyproject_path).validate()
