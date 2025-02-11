# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Generator
from contextlib import contextmanager, nullcontext
from pathlib import Path
from subprocess import run
from typing import Dict, List

from tomlkit import TOMLDocument
from tomlkit.toml_file import TOMLFile

from peeler.utils import restore_file
from peeler.uv_utils import find_uv_bin

LOCK_FILE = "uv.lock"


def _get_lock_path(pyproject_file: Path) -> Path:
    return Path(pyproject_file).parent / LOCK_FILE


@contextmanager
def _generate_lock_file(pyproject_file: Path, *, unlink: bool) -> Generator[Path, None, None]:
    uv_bin = find_uv_bin()

    run(
        [
            uv_bin,
            "--no-config",
            "--directory",
            pyproject_file.parent,
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
        if unlink:
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
        context = restore_file(lock_file)
    else:
        context = nullcontext

    with context:
        with _generate_lock_file(pyproject_file, unlink = not lock_file.exists()):
            lock_toml = TOMLFile(lock_file).read()

    return _get_wheels_urls_from_lock(lock_toml)
