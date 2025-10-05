# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

import atexit
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
from re import sub

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


@contextmanager
def restore_file(
    filepath: Path, *, missing_ok: bool = False
) -> Generator[None, None, None]:
    """Context Manager to ensure that a file contents and metadata are restored after use.

    The file must NOT be opened before calling `restore_file`

    :param filepath: The path of the file
    :param missing_ok: if set to True and the file does not exist, delete the file after use.
    :raises FileNotFoundError: if missing_ok is False and the file does not exist
    """

    file_exist = filepath.exists()

    if not missing_ok and not file_exist:
        raise FileNotFoundError(f"File {format_filename(filepath)} not found.")

    with TemporaryDirectory(ignore_cleanup_errors=True) as tempdir:
        if file_exist:
            temp_path = Path(copy2(Path(filepath), tempdir))

        def restore_file() -> None:
            filepath.unlink(missing_ok=True)
            if file_exist:
                copy2(temp_path, filepath)

        atexit.register(restore_file)

        try:
            yield
        finally:
            restore_file()
            atexit.unregister(restore_file)


def normalize_package_name(name: str) -> str:
    """Normalize a package name for comparison.

    from: https://packaging.python.org/en/latest/specifications/name-normalization/#name-normalization

    :param name: the package name
    :return: the normalized package name
    """
    return sub(r"[-_.]+", "-", name).lower()