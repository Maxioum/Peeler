import tomllib
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from subprocess import run
from typing import Dict, List

from tomlkit import TOMLDocument

from peeler.uv_utils import find_uv_bin

LOCK_FILE = "uv.lock"


def _get_lock_path(pyproject_file: Path) -> Path:
    return Path(pyproject_file).parent / LOCK_FILE


@contextmanager
def _generate_lock_file(pyproject_file: Path) -> Generator[Path, None, None]:
    uv_bin = find_uv_bin()

    run(
        [
            uv_bin,
            "--isolated",
            "--directory",
            pyproject_file.parent,
            "--no-config",
            "--no-python-downloads",
            "lock",
            "--no-build",
            "--script",
            pyproject_file,
        ],
        cwd=pyproject_file.parent,
    )

    lock_file = _get_lock_path(pyproject_file)

    try:
        yield lock_file
    finally:
        lock_file.unlink()


def _get_wheels_urls_from_lock(lock_toml: TOMLDocument) -> Dict[str, List[str]]:
    urls: Dict[str, List[str]] = {}

    if (packages := lock_toml.get("package", None)) is None:
        return {}

    for package in packages:
        if "wheels" not in package:
            continue

        urls[package["name"]] = [wheels["url"] for wheels in package["wheels"]]

    return urls


def get_wheels_url(pyproject_file: Path) -> Dict[str, List[str]]:
    """Return a Dict containing wheels urls from a pyproject.toml dependencies table.

    :param pyproject_file: the pyproject file.
    :return: A Dict with package name as key and a list of package urls as values.
    """
    if (lock_file := _get_lock_path(pyproject_file)).exists():
        with lock_file.open("rb") as file:
            lock_toml = tomllib.load(file)

    else:
        with _generate_lock_file(pyproject_file) as lock_file:
            # open lock file to retrieve wheels url for all platform
            with lock_file.open("rb") as file:
                lock_toml = tomllib.load(file)

    return _get_wheels_urls_from_lock(lock_toml)
