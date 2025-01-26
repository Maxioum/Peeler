import shutil
from click import ClickException


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
