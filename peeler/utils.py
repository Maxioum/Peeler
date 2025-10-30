# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

import atexit
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from re import sub
from shutil import copy2
from tempfile import TemporaryDirectory
from typing import Dict, NoReturn, Tuple

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


_BLENDER_TO_WHEEL_PLATFORM_TAGS: Dict[str, Tuple[str, str]] = {
    "windows-x64": ("win", "amd64"),
    "windows-arm64": ("win", "32"),
    "linux-x64": ("manylinux", "x86_64"),  # muslinux not supported by blender,
    "macos-arm64": ("macosx", "arm64"),
    "macos-x64": ("macosx", "x86_64"),
}


def parse_blender_supported_platform(platform: str) -> Tuple[str, str]:
    """Normalize a platform from blender manifest supported platfrom.

    from: https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html#manifest

    :param platform: the platform string
    :return: a tuple with platform and arch
    """

    if (_platform := _BLENDER_TO_WHEEL_PLATFORM_TAGS.get(platform, None)) is None:
        raise ClickException(
            f"""Invalid platform: `{platform}` .
Expected one the following platform:
{" ".join([f"`{platform_}`" for platform_ in _BLENDER_TO_WHEEL_PLATFORM_TAGS.keys()])}
see https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html#manifest """
        )

    return _platform


import re

PLATFORM_REGEX = re.compile(
    r"^(?P<platform>macosx|manylinux|musllinux|win|linux|any)"
    r"(?:[_\-]?(?P<version>\d+(?:[_\-]\d+)*))?"  # version ex: 11_0, 2014, 2_17
    r"(?:[_\-](?P<arch>[A-Za-z0-9_]+))?$"  # arch ex: x86_64, arm64, amd64
)


def parse_package_platform_tag(
    platform_tag: str,
) -> Tuple[str, str | None, str | None]:
    """Normalize a platform tag from a wheel url.

    from: https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/#platform-tag

    :param platform: the platform tag
    :return: a tuple with platform optional version number and arch
    """

    if platform_tag == "win32":  # special case
        return ("win", None, "32")

    def _raise() -> NoReturn:
        raise ClickException(f"""Invalid platform tag: `{platform_tag}` .""")

    if (match_ := PLATFORM_REGEX.match(platform_tag)) is None:
        _raise()
    if len(groups_ := match_.groups(default=None)) != 3:
        _raise()

    platform, version, arch = groups_

    if platform == "any":
        if version or arch:
            _raise()
        return platform, version, arch

    if not platform or not arch:
        _raise()

    return platform, version, arch
