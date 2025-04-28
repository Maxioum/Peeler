# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

from os import fspath
from pathlib import Path
from subprocess import run
from typing import Dict, List, Tuple

import typer
from click import ClickException
from typer import progressbar
from wheel_filename import parse_wheel_filename

from peeler.uv_utils import find_uv_bin

_VALID_IMPLEMENTATIONS = {"cp", "py"}


def _parse_implementation_and_python_version(python_tag: str) -> Tuple[str, str]:
    return python_tag[:2], python_tag[2:]


def _has_valid_implementation(url: str) -> bool:
    wheel_info = parse_wheel_filename(url)

    return any(
        _parse_implementation_and_python_version(tag)[0].lower()
        in _VALID_IMPLEMENTATIONS
        for tag in wheel_info.python_tags
    )


def _download_from_url(destination_directory: Path, url: str) -> Path:
    wheel_info = parse_wheel_filename(url)
    path = destination_directory / str(wheel_info)

    if path.is_file():
        return path

    platform = wheel_info.platform_tags[0]
    implementation, python_version = _parse_implementation_and_python_version(
        wheel_info.python_tags[0]
    )
    abi = wheel_info.abi_tags[0]

    _destination_directory = fspath(destination_directory.resolve())
    uv_bin = find_uv_bin()
    cmd = [
        uv_bin,
        "--isolated",
        "tool",
        "run",
        "--no-config",
        "--no-python-downloads",
        "--no-build",
        "pip",
        "download",
        "-d",
        _destination_directory,
        "--no-deps",
        "--only-binary",
        ":all:",
        "--platform",
        platform,
        "--abi",
        abi,
        "--implementation",
        implementation,
        "--progress-bar",
        "off",
    ]

    if len(python_version) > 1:
        cmd.extend(["--python-version", python_version])

    cmd.append(url)

    result = run(cmd, capture_output=True, text=True)
    stderr = result.stderr

    if not path.is_file():
        msg = f"Error when downloading wheel for package `{wheel_info.project}` for platform `{platform}`"
        raise ClickException(f"{msg}{stderr}")

    return path


def download_wheels(wheels_directory: Path, urls: Dict[str, List[str]]) -> List[Path]:
    """Download the wheels from urls with pip download into wheels_directory.

    :param wheels_directory: The directory to download wheels into
    :param urls: A Dict with package name as key and a list of package urls as values.
    :return: the list of the downloaded wheels path
    """
    wheels_directory.mkdir(parents=True, exist_ok=True)

    wheels_paths: List[Path] = []

    for package_name, package_urls in urls.items():
        # filter out python implementations not supported by blender
        package_urls = list(filter(_has_valid_implementation, package_urls))

        if not package_urls:
            msg = (
                f"No suitable implementation found for {package_name}, not downloading."
            )
            typer.echo(f"Warning: {msg}")
            continue

        with progressbar(package_urls, label=package_name, color=True) as _package_urls:
            for url in _package_urls:
                filename = _download_from_url(wheels_directory, url)

                wheels_paths.append(filename)

    return wheels_paths
