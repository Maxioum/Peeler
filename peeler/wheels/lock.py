# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

import re
from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import contextmanager
from os import fspath
from pathlib import Path
from subprocess import run
from typing import Any, Dict, List, Optional, Tuple, Type

from click import ClickException, format_filename
from tomlkit import TOMLDocument
from tomlkit.toml_file import TOMLFile

from peeler.pyproject.parser import PyprojectParser
from peeler.pyproject.update import (
    update_dependencies,
    update_dependency_groups,
    update_requires_python,
)
from peeler.utils import restore_file
from peeler.uv_utils import check_uv_version, find_uv_bin

UV_LOCK_FILE = "uv.lock"

from peeler.pyproject.parser import PyprojectParser


@contextmanager
def _generate_uv_lock(pyproject_file: Path) -> Generator[Path, None, None]:
    """Generate or update a uv.lock file from a pyproject.toml files.

    :param pyproject_file: the pyproject filepath
    :yield: the lock file path
    """
    uv_bin = find_uv_bin()

    lock_path = Path(pyproject_file).parent / UV_LOCK_FILE

    cmd: List[str] = [
        uv_bin,
        "--no-config",
        "--directory",
        fspath(pyproject_file.parent),
        "lock",
        "--no-build",
    ]

    python_specifiers = PyprojectParser.from_file(pyproject_file).project_table.get(
        "requires-python"
    )

    if python_specifiers:
        cmd.extend(["--python", str(python_specifiers)])

    with restore_file(lock_path, missing_ok=True):
        run(
            cmd,
            cwd=pyproject_file.parent,
        )

        yield lock_path


def _get_wheels_urls_from_uv_lock(lock_toml: TOMLDocument) -> Dict[str, List[str]]:
    """Retrieve wheels url from a uv.lock toml.

    :param lock_toml: the uv.lock file
    :return: A mapping from package to a list of url.
    """

    urls: Dict[str, List[str]] = {}

    if (packages := lock_toml.get("package", None)) is None:
        return {}

    for package in packages:
        if "wheels" not in package:
            continue

        urls[package["name"]] = [wheels["url"] for wheels in package["wheels"]]

    return urls


def _get_wheels_urls_from_pylock(lock_toml: TOMLDocument) -> Dict[str, List[str]]:
    """Retrieve wheels url from a pylock toml.

    :param lock_toml: the pylock file
    :return: A mapping from package to a list of url.
    """

    urls: Dict[str, List[str]] = {}

    if (packages := lock_toml.get("packages", None)) is None:
        return {}

    for package in packages:
        if "wheels" not in package:
            continue

        urls[package["name"]] = [wheels["url"] for wheels in package["wheels"]]

    return urls


class AbstractURLFetcherStrategy(ABC):
    """Abstract base class for strategies that fetch URLs from a file.

    This class defines the structure for URL fetcher strategies that parse or retrieve
    URLs from a specified file.

    :param path: Path to the file where the URLs to be parsed or retrieved are.
    """

    def __init__(self, path: Path, *arg: Any, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def get_urls(self) -> Dict[str, List[str]]:
        """Fetch and return URLs determined from the file.

        The method should return a mapping where each key is a package name, and each
        value is a list of wheel URLs associated with that package.

        :return: A dictionary mapping package names to a list of URLs.
        """

        raise NotImplementedError


class UVLockUrlFetcher(AbstractURLFetcherStrategy):
    """URL fetcher that extracts wheel URLs from a uv.lock file.

    Parses the given uv.lock file and retrieves a list of wheel URLs for each package
    listed in the lock file.

    :param uv_lock: Path to the uv.lock file to extract wheel url from.
    """

    def __init__(self, uv_lock: Path) -> None:
        self.uv_lock = uv_lock

    def get_urls(self) -> Dict[str, List[str]]:
        """Extract wheel URLs from the uv.lock file.

        Parses the uv.lock file and returns a mapping of package names to lists
        of wheel URLs.

        :return: Dictionary with package names as keys and lists of wheel URLs as values.
        """

        lock_toml = TOMLFile(self.uv_lock).read()
        return _get_wheels_urls_from_uv_lock(lock_toml)


class PyprojectUVLockFetcher(AbstractURLFetcherStrategy):
    """URL fetcher that retrieves wheel URLs from a pyproject.toml file.

    Temporarily modifies the pyproject.toml file to restrict dependencies to a
    Blender-compatible environment, generates a uv.lock file, and extracts the
    corresponding wheel URLs for each package.

    :param pyproject: Path to the pyproject.toml file to process.
    """

    def __init__(
        self,
        pyproject: Path,
        *,
        excluded_dependencies: Optional[List[str]] = None,
        excluded_dependency_groups: Optional[List[str]] = None,
    ):
        self.pyproject = pyproject
        self.excluded_dependencies = excluded_dependencies
        self.excluded_dependency_groups = excluded_dependency_groups

    def get_urls(self) -> Dict[str, List[str]]:
        """Extract wheel URLs from the dependencies listed in pyproject.toml.

        This method temporarily adjusts the pyproject file to ensure compatibility,
        generates a uv.lock file using `uv`, and parses it to collect URLs of
        downloadable wheels for each package.

        :return: Dictionary with package names as keys and lists of wheel URLs as values.
        """

        check_uv_version()

        # Temporarily modify the pyproject file to restrict to Blender-supported wheels
        with restore_file(self.pyproject):
            file = TOMLFile(self.pyproject)
            pyproject = PyprojectParser(file.read())
            pyproject = update_requires_python(pyproject)
            if self.excluded_dependencies:
                pyproject = update_dependencies(pyproject, self.excluded_dependencies)
            if self.excluded_dependency_groups:
                pyproject = update_dependency_groups(
                    pyproject, self.excluded_dependency_groups
                )
            file.write(pyproject._document)

            # Generate a uv.lock file and extract wheel URLs
            with _generate_uv_lock(self.pyproject) as uv_lock:
                uv_lock_toml = TOMLFile(uv_lock).read()
                return _get_wheels_urls_from_uv_lock(uv_lock_toml)


class PylockUrlFetcher(AbstractURLFetcherStrategy):
    """URL fetcher that extracts wheel URLs from a pylock like file.

    Parses the given pylock file and retrieves a list of wheel URLs for
    each package listed in the lock file.

    :param pylock: Path to the pylock file.
    """

    def __init__(self, pylock: Path):
        self.pylock = pylock

    def get_urls(self) -> Dict[str, List[str]]:
        """Extract wheel URLs from the pylock file.

        :return: Dictionary with package names as keys and lists of wheel URLs as values.
        """

        pylock_toml = TOMLFile(self.pylock).read()
        return _get_wheels_urls_from_pylock(pylock_toml)


class UrlFetcherCreator:
    """Factory class to select the appropriate URL fetcher strategy based on the file name.

    This class inspects a given path (file or directory) and determines which
    URL fetcher strategy to use, depending on the presence of known files such as
    `pylock.toml` or `pylock.*.toml`, `pyproject.toml`, or `uv.lock`.

    The matching is based on regular expressions, evaluated in the declared order.

    :param path: Path to a file or a directory containing lock/config files.
    """

    # The order of patterns matters (checked top to bottom)
    regexes_to_strategy: List[Tuple[str, Type[AbstractURLFetcherStrategy]]] = [
        (r"^pylock.toml$", PylockUrlFetcher),
        (r"^pylock\.[^.]+\.toml$", PylockUrlFetcher),
        (r"^pyproject\.toml$", PyprojectUVLockFetcher),
        (r"^uv\.lock$", UVLockUrlFetcher),
    ]

    def __init__(self, path: Path) -> None:
        self.path = path

    def get_fetch_url_strategy(
        self,
        *,
        excluded_dependencies: Optional[List[str]] = None,
        excluded_dependency_groups: Optional[List[str]] = None,
    ) -> AbstractURLFetcherStrategy:
        """Select and return the appropriate URL fetcher strategy based on the given file or directory.

        If the path is a file, check whether it matches one of the known patterns.
        If the path is a directory, look for (in order): a pylock file, uv.lock, then pyproject.toml.

        :return: Instance of a subclass of AbstractURLFetcherStrategy.
        :raises ClickException: If no matching file is found.
        """

        files = (self.path,) if not self.path.is_dir() else self.path.iterdir()

        if has_excluded_dependencies := bool(
            excluded_dependencies or excluded_dependency_groups
        ):
            # if there are excluded dependencies need to have a pyproject.toml file
            regex, strategy = self.regexes_to_strategy[2]
            for filepath in files:
                if re.match(regex, filepath.name):
                    return strategy(
                        filepath,
                        excluded_dependencies=excluded_dependencies,
                        excluded_dependency_groups=excluded_dependency_groups,
                    )
        else:
            for regex, strategy in self.regexes_to_strategy:
                for filepath in files:
                    if re.match(regex, filepath.name):
                        return strategy(filepath)

        if self.path.is_dir():
            msg = f"No supported file found in {format_filename(self.path.resolve())}."
        else:
            msg = f"The file {format_filename(self.path.resolve())} is not a supported type."

        if has_excluded_dependencies:
            msg = f"{msg}\n Expected a `pyproject.toml` file to exclude dependencies"
        else:
            msg = f"{msg}\n"
            f"Expected one of the following:\n"
            f"  - pylock.toml or pylock.*.toml\n"
            f"  - uv.lock\n"
            f"  - pyproject.toml"

        raise ClickException(msg)
