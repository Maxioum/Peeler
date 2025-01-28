import re
import shutil
from subprocess import run

from click import ClickException
from packaging.version import Version


def find_uv_bin() -> str:
    """Return the path to the uv bin.

    :raises ClickException: if the bin cannot be found.
    """

    uv_bin = shutil.which("uv")

    if uv_bin is None:
        raise ClickException(
            f"""cannot find uv bin
Install uv `https://astral.sh/blog/uv` or
Install peeler optional dependency uv (eg: pip install peeler[uv])
"""
        )

    return uv_bin


version_regex = r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
_MIN_UV_VERSION = Version("0.5.17")


def check_uv_version() -> None:
    """Check the current uv version is at least 0.5.17."""

    uv_bin = find_uv_bin()

    result = run([uv_bin, "version"], capture_output=True, text=True, check=True)
    output = result.stdout.strip()
    match = re.search(version_regex, output)

    if not match:
        import peeler

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
