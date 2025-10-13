# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

import sys
from abc import ABC, abstractmethod
from functools import reduce
from os import fspath
from pathlib import Path
from subprocess import run
from typing import Dict, Iterable, List, Optional, Protocol, Set, Tuple

import typer
from click import ClickException
from typer import progressbar
from wheel_filename import ParsedWheelFilename, parse_wheel_filename

from peeler.utils import normalize_package_name
from peeler.uv_utils import find_uv_bin, has_uv


def _parse_implementation_and_python_version(python_tag: str) -> Tuple[str, str]:
    return python_tag[:2], python_tag[2:]


def _wheel_path(destination_directory: Path, wheel_info: ParsedWheelFilename) -> Path:
    return destination_directory / str(wheel_info)


def _pip_cmd(url: str, destination_directory: Path) -> List[str]:
    wheel_info = parse_wheel_filename(url)

    platform = wheel_info.platform_tags[0]
    implementation, python_version = _parse_implementation_and_python_version(
        wheel_info.python_tags[0]
    )
    abi = wheel_info.abi_tags[0]

    _destination_directory = fspath(destination_directory.resolve())

    cmd = [
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
        url,
    ]

    if len(python_version) > 1:
        cmd.extend(["--python-version", python_version])

    return cmd


class UrlsFilter(Protocol):
    """
    Protocol defining a callable that filters a list of wheel URLs.

    Implementations should return a list of URLs matching a specific criterion.
    """

    def __call__(self, urls: Iterable[str]) -> List[str]:
        """
        Filter the given list of URLs.

        :param urls: The list of wheel URLs to filter.
        :return: A filtered list of wheel URLs.
        """
        ...


class HasValidImplementation(UrlsFilter):
    """
    Filter wheel URLs to retain only those with Blender compatible implementation tags.

    Valid implementations include `cp` (CPython) and `py` (generic Python).
    :param package_name: Optional name of the package, used in warning messages.
    """

    _VALID_IMPLEMENTATIONS = {"cp", "py"}

    def __init__(self, package_name: str | None = None) -> None:
        self.package_name = package_name

    def has_valid_implementation(self, url: str) -> bool:
        """
        Check if the wheel URL has a valid implementation tag.

        :param url: The wheel URL to check.
        :return: True if the implementation is valid, False otherwise.
        """
        wheel_info = parse_wheel_filename(url)

        result = any(
            _parse_implementation_and_python_version(tag)[0].lower()
            in self._VALID_IMPLEMENTATIONS
            for tag in wheel_info.python_tags
        )

        return result

    def __call__(self, urls: Iterable[str]) -> List[str]:
        """
        Filter out URLs that do not match valid implementation tags.

        :param urls: List of wheel URLs to filter.
        :return: List of URLs matching the valid implementation criteria.
        """

        if not urls:
            return []

        urls = list(filter(self.has_valid_implementation, urls))

        if not urls:
            if self.package_name:
                msg = f"No suitable implementation found for {self.package_name}, not downloading."
                typer.echo(f"Warning: {msg}")

        return urls


class IsNotAlreadyDownloaded(UrlsFilter):
    """
    Filter wheel URLs to exclude those already downloaded to a given directory.

    :param destination_directory: Directory where wheels are downloaded.
    """

    def __init__(self, destination_directory: Path) -> None:
        self.destination_directory = destination_directory

    def _is_downloaded(self, url: str) -> bool:
        """
        Check whether the wheel corresponding to the given URL is already downloaded.

        :param url: The wheel URL to check.
        :return: True if the wheel is not already downloaded, False otherwise.
        """
        wheel_info = parse_wheel_filename(url)
        path = _wheel_path(self.destination_directory, wheel_info)

        return not path.is_file()

    def __call__(self, urls: Iterable[str]) -> List[str]:
        """
        Filter out wheel URLs that are already downloaded.

        :param urls: Iterable of wheel URLs to filter.
        :return: List of URLs not yet downloaded.
        """
        return list(filter(self._is_downloaded, urls))


class PackageIsNotExcluded(UrlsFilter):
    """Filter out URLs for excluded packages.

    :param package_name: Name of the package to check.
    :param excluded_packages: Set of package names to exclude.
    """

    def __init__(self, package_name: str, excluded_packages: List[str]) -> None:
        self.package_name = normalize_package_name(package_name)
        self.excluded_packages = {
            normalize_package_name(package_name) for package_name in excluded_packages
        }

    def __call__(self, urls: Iterable[str]) -> List[str]:
        """Return URLs if the package is not excluded.

        :param urls: List of wheel URLs to filter.
        :return: List of URLs if the package is not excluded, else an empty list.
        """

        if self.package_name in self.excluded_packages:
            msg = f"Excluded package `{self.package_name}`, not downloading."
            typer.echo(f"Info: {msg}")
            return []

        return list(urls)


class AbstractWheelsDownloader(ABC):
    """
    Abstract base class defining the interface for wheel downloaders.

    Subclasses must implement the `download_wheel` method to handle the
    download of Python wheels to a specified directory.
    """

    @abstractmethod
    def download_wheel(self, url: str, destination_directory: Path) -> Path:
        """
        Download a wheel file from the given URL and stores it in the destination directory.

        :param url: The URL pointing to the wheel file to download.
        :param destination_directory: The directory where the wheel should be saved.
        :return: The full path to the downloaded wheel file.
        """
        raise NotImplementedError


class UVPipWheelsDownloader(AbstractWheelsDownloader):
    """
    Wheel downloader that uses `uv` to download wheels.

    This implementation runs `pip` through uv commands to download the specified
    wheel file to a given destination directory.
    """

    def download_wheel(self, url: str, destination_directory: Path) -> Path:
        """
        Download a wheel file from the given URL using `uv` and stores it in the destination directory.

        :param url: The URL pointing to the wheel file to download.
        :param destination_directory: The directory where the wheel should be saved.
        :return: The full path to the downloaded wheel file.
        :raises ClickException: If the wheel file is not found after download.
        """

        uv_bin = find_uv_bin()
        cmd = [
            uv_bin,
            "--isolated",
            "tool",
            "run",
            "--no-config",
            "--no-python-downloads",
            "--no-build",
            *_pip_cmd(url=url, destination_directory=destination_directory),
        ]

        result = run(cmd, capture_output=True, text=True)

        wheel_info = parse_wheel_filename(url)
        path = _wheel_path(destination_directory, wheel_info)

        if not path.is_file():
            stderr = result.stderr
            platforms = wheel_info.platform_tags
            msg = f"Error when downloading wheel for package `{wheel_info.project}` for platform(s) `{' '.join(platforms)}`"
            raise ClickException(f"{msg}{stderr}")

        return path


class PipWheelsDownloader(AbstractWheelsDownloader):
    """
    Wheel downloader that uses the standard pip module to download wheels.

    This implementation constructs and runs a pip command to download the specified
    wheel file to a given destination directory.
    """

    def download_wheel(self, url: str, destination_directory: Path) -> Path:
        """
        Download a wheel file from the given URL using pip and stores it in the destination directory.

        :param url: The URL pointing to the wheel file to download.
        :param destination_directory: The directory where the wheel should be saved.
        :return: The full path to the downloaded wheel file.
        :raises ClickException: If the wheel file is not found after download.
        """

        cmd = [sys.executable, "-m", *_pip_cmd(url, destination_directory)]

        result = run(cmd, capture_output=True, text=True)

        wheel_info = parse_wheel_filename(url)
        path = _wheel_path(destination_directory, wheel_info)

        if not path.is_file():
            stderr = result.stderr
            platforms = wheel_info.platform_tags
            msg = f"Error when downloading wheel for package `{wheel_info.project}` for platform(s) `{' '.join(platforms)}`"
            raise ClickException(f"{msg}{stderr}")

        return path


class WheelsDownloaderCreator:
    """
    Factory class for selecting an appropriate wheel download strategy.

    Depending on the environment, this class decides whether to use the `uv`-based
    wheel downloader or the standard pip-based downloader.
    """

    def get_wheel_download_strategy(self) -> AbstractWheelsDownloader:
        """
        Return the appropriate wheel download strategy based on the current environment.

        If `uv` is available, returns a `UVPipWheelsDownloader` instance.
        Otherwise, returns a `PipWheelsDownloader` instance.

        :return: The selected wheel download strategy.
        """
        if has_uv():
            return UVPipWheelsDownloader()
        else:
            return PipWheelsDownloader()


def download_wheels(
    wheels_directory: Path,
    urls: Dict[str, List[str]],
    *,
    excluded_packages: Optional[List[str]] = None,
) -> List[Path]:
    """Download the wheels from urls with pip download into wheels_directory.

    :param wheels_directory: The directory to download wheels into
    :param urls: A Dict with package name as key and a list of package urls as values.
    :return: the list of the downloaded wheels path
    """
    wheels_directory.mkdir(parents=True, exist_ok=True)

    wheels_paths: List[Path] = []

    wheel_downloader = WheelsDownloaderCreator().get_wheel_download_strategy()

    _max_package_name_len = max(
        (len(package_name) for package_name in urls.keys()), default=0
    )

    for package_name, package_urls in urls.items():
        filters: Set[UrlsFilter] = {HasValidImplementation(package_name)}

        if excluded_packages:
            filters.add(PackageIsNotExcluded(package_name, excluded_packages))

        package_urls = reduce(lambda acc, filter_: filter_(acc), filters, package_urls)

        if not package_urls:
            continue

        with progressbar(
            package_urls,
            label=package_name.ljust(_max_package_name_len),
            color=True,
            width=_max_package_name_len,
        ) as _package_urls:
            for url in _package_urls:
                destination_path = _wheel_path(
                    wheels_directory, parse_wheel_filename(url)
                )
                if not destination_path.exists():
                    wheel_downloader.download_wheel(url, wheels_directory)
                wheels_paths.append(destination_path)

    return wheels_paths
