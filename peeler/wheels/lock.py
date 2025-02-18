# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Generator
from contextlib import contextmanager
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
def _get_lock_file(pyproject_file: Path) -> Generator[Path, None, None]:
    uv_bin = find_uv_bin()

    lock_path = _get_lock_path(pyproject_file)

    with restore_file(lock_path, missing_ok=True):
        run(
            [
                uv_bin,
                "--no-config",
                "--directory",
                pyproject_file.parent,
                "--no-python-downloads",
                "lock",
                "--no-build",
            ],
            cwd=pyproject_file.parent,
        )

        yield lock_path


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

    with _get_lock_file(pyproject_file) as lock_file:
        # open lock file to retrieve wheels url for all platform
        lock_toml = TOMLFile(lock_file).read()

    return _get_wheels_urls_from_lock(lock_toml)
