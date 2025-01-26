import shutil
from pathlib import Path
from subprocess import run
from typing import Iterable

import typer
from click import ClickException
from typer import format_filename

PYPROJECT_FILENAME = "pyproject.toml"


def find_pyproject_file(
    pyproject_path: Path, *, allow_non_default_name: bool = False
) -> Path:
    """Ensure that the file exists at the given path.

    :param pyproject_path: file or directory path
    :param allow_non_default_name: whether to allow a file to be named other than `pyproject.toml`
    :raises ClickException: on missing file
    :raises ClickException: if allow_non_default_name is set to False, on file named other than `pyproject.toml`
    :return: the pyproject file path
    """

    if pyproject_path.is_dir():
        pyproject_path = pyproject_path / PYPROJECT_FILENAME

    if not pyproject_path.is_file():
        raise ClickException(
            f"No {PYPROJECT_FILENAME} found at {format_filename(pyproject_path.parent.resolve())}"
        )

    if not pyproject_path.name == PYPROJECT_FILENAME:
        msg = f"""The pyproject file at {format_filename(pyproject_path.parent)}
Should be named : `{PYPROJECT_FILENAME}` not `{pyproject_path.name}`
        """
        if allow_non_default_name:
            typer.echo(f"Warning: {msg}")
        else:
            raise ClickException(msg)

    return pyproject_path
