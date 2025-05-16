# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from asyncio import create_subprocess_exec
from os import fspath
from pathlib import Path
from typing import Dict, List, Tuple

from clypi import AbortException, ClypiException, Spin, Spinner, cprint
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


async def _download_from_url(destination_directory: Path, url: str) -> Path:
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
        "on",
    ]

    if len(python_version) > 1:
        cmd.extend(["--python-version", python_version])

    cmd.append(url)

    process = await create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if not path.is_file():
        msg = f"Error when downloading wheel for package `{wheel_info.project}` for platform `{platform}`"
        raise AbortException(f"{msg}{stderr.decode()}")

    return path


async def download_wheels(
    wheels_directory: Path, urls: Dict[str, List[str]]
) -> List[Path]:
    """Download the wheels from urls with pip download into wheels_directory.

    :param wheels_directory: The directory to download wheels into
    :param urls: A Dict with package name as key and a list of package urls as values.
    :return: the list of the downloaded wheels path
    """
    wheels_directory.mkdir(parents=True, exist_ok=True)

    wheels_paths: List[Path] = []
    async with Spinner(
        title="", capture=True, animation=Spin.DOTS2, suffix=""
    ) as spinner:
        for package_name, package_urls in urls.items():
            # filter out python implementations not supported by blender
            package_urls = list(filter(_has_valid_implementation, package_urls))

            if not package_urls:
                msg = f"No suitable implementation found for {package_name}, not downloading."
                cprint(f"Warning: {msg}")
                continue

            for i, url in enumerate(package_urls):
                title = f"Downloading: {package_name}"
                if len(package_urls) > 1:
                    title = f"{title} ({i + 1}/{len(package_urls)})"
                spinner.title = title

                filename = await _download_from_url(wheels_directory, url)

                wheels_paths.append(filename)
        spinner.title = f"Downloaded {len(urls)} packages !"
    return wheels_paths
