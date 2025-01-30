import re
import shutil
from os import PathLike, fspath
from subprocess import run

import typer
import typer.rich_utils
from click import ClickException, format_filename
from packaging.version import Version

version_regex = r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
_MIN_UV_VERSION = Version("0.5.17")


def get_uv_bin_version(uv_bin: PathLike) -> Version | None:
    """Return the uv version.

    :param uv_bin: path to a uv bin
    :return: the version of the provided binary
    """

    uv_bin = fspath(uv_bin)

    result = run([uv_bin, "version"], capture_output=True, text=True, check=True)
    output = result.stdout.strip()
    match = re.search(version_regex, output)

    if not match:
        return None

    return Version(match.group(0))


def find_uv_bin() -> str:
    """Return the path to the uv bin.

    :raises ClickException: if the bin cannot be found.
    """

    try:
        import uv

        uv_bin = uv._find_uv.find_uv_bin()
    except (ModuleNotFoundError, FileNotFoundError):
        uv_bin = shutil.which("uv")

    if uv_bin is None:
        raise ClickException(
            f"""Cannot find uv bin
Install uv `https://astral.sh/blog/uv` or
Install peeler optional dependency uv (eg: pip install peeler[uv])
"""
        )

    return uv_bin


def get_uv_version() -> Version | None:
    """Return uv version."""

    return get_uv_bin_version(find_uv_bin())


def check_uv_version() -> None:
    """Check the current uv version is at least 0.5.17.

    :raises ClickException: if uv version cannot be determined or is lower than the minimum version.
    """

    uv_version = get_uv_bin_version(find_uv_bin())

    if not uv_version:
        import peeler

        raise ClickException(
            f"""Error when checking uv version
To use {peeler.__name__} wheels feature uv must be at least {_MIN_UV_VERSION}
Run `uv self update` to update uv"""
        )

    if uv_version < _MIN_UV_VERSION:
        import peeler

        raise ClickException(
            f"""uv version is {uv_version}
To use {peeler.__name__} wheels feature uv must be at least {_MIN_UV_VERSION}
Run `uv self update` to update uv"""
        )
