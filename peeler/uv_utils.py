# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

import re
import shutil
from os import PathLike, fspath
from pathlib import Path
from subprocess import run

from click import ClickException
from packaging.version import Version
from typing import Literal, overload

from peeler import MAX_UV_VERSION, MIN_UV_VERSION

version_regex = r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"


def get_uv_bin_version(uv_bin: PathLike) -> Version | None:
    """Return the uv version.

    :param uv_bin: path to a uv bin
    :return: the version of the provided binary
    """

    uv_bin = fspath(uv_bin)

    result = run([uv_bin, "self", "version"], capture_output=True, text=True, check=True)
    output = result.stdout.strip()
    match = re.search(version_regex, output)

    if not match:
        return None

    return Version(match.group(0))


@overload
def find_uv_bin() -> str:
    ...

@overload
def find_uv_bin(raises: Literal[True]) -> str:
    ...

@overload
def find_uv_bin(raises: Literal[False]) -> str | None:
    ...

def find_uv_bin(raises: bool = True) -> str | None:
    """Return the path to the uv bin.

    :raises ClickException: if the bin cannot be found.
    """

    try:
        from uv import _find_uv

        uv_bin: str | None = _find_uv.find_uv_bin()
    except (ModuleNotFoundError, FileNotFoundError):
        uv_bin = shutil.which("uv")

    if raises and uv_bin is None:
        raise ClickException(
            f"""Cannot find uv bin
Install uv `https://astral.sh/blog/uv` or
Install peeler with uv (eg: pip install peeler[uv])
"""
        )

    return uv_bin


def has_uv() -> bool:
    """Return whether uv is present on the system.

    :return: True if uv is found, False otherwise.
    """
    
    return find_uv_bin(raises=False) is not None
        
        
def get_uv_version() -> Version | None:
    """Return uv version."""

    return get_uv_bin_version(Path(find_uv_bin()))


def check_uv_version() -> None:
    """Check the current uv version is between 0.7.0 and current supported max uv version.

    See .max-uv-version or pyproject.toml files.

    :raises ClickException: if uv version cannot be determined or is lower than the minimum version.
    """

    uv_version = get_uv_bin_version(Path(find_uv_bin()))

    try:
        import uv
    except (ModuleNotFoundError, FileNotFoundError):
        from_pip = False
    else:
        from_pip = True

    from peeler import __name__

    body = f"To use {__name__} wheels feature with a pyproject.toml uv version must be between {MIN_UV_VERSION} and {MAX_UV_VERSION}"

    if from_pip:
        update_uv = """Install peeler with a supported uv version:

pip install peeler[uv]"""
    else:
        update_uv = f"""Use peeler with a supported uv version without changing your current uv installation:

uvx peeler[uv] [OPTIONS] COMMAND [ARGS]"""

    if not uv_version:
        header = "Error when checking uv version. Make sur to have installed, visit: https://docs.astral.sh/uv/getting-started/installation/"
        raise ClickException(f"""{header}

{body}

{update_uv}""")

    if uv_version > MAX_UV_VERSION or uv_version < MIN_UV_VERSION:
        header = f"uv version is {uv_version}"

        raise ClickException(f"""{header}
{body}
{update_uv}""")
