# # SPDX-FileCopyrightText: 2025-2026 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Dict, List, Self

from tomlkit import TOMLDocument
from tomlkit.items import Table
from tomlkit.toml_file import TOMLFile

from peeler.utils import find_pyproject_file

DependencyGroups = Dict[str, List[str | Dict[str, str]]]


class PyprojectParser:
    """A class to parse values from a `pyproject.toml` with a peeler tool table.

    :param document: The TOML document representing the `pyproject.toml` file.
    """

    def __init__(self, document: TOMLDocument) -> None:
        self._document = document

    @classmethod
    def from_file(cls, pyproject_file: Path) -> Self:
        """Construct a PyprojectParser instance from a pyproject.toml file.

        :param pyproject_file: the file to parse
        :return: A new PyprojectParser instance
        """
        return cls(TOMLFile(pyproject_file).read())

    @property
    def project_table(self) -> Table:
        """Retrieve the `[project]` table from the `pyproject.toml`.

        :return: The `[project]` table.
        """
        if not hasattr(self, "_project_table"):
            self._project_table = self._document.get("project")
        return self._project_table

    @property
    def peeler_table(self) -> Table:
        """Retrieve the `[tool.peeler]` table from the `pyproject.toml`.

        :return: The `[tool.peeler]` table.
        """
        if not hasattr(self, "_peeler_table"):
            self._peeler_table = self._document.get("tool", {}).get("peeler")

        return self._peeler_table

    @property
    def settings_table(self) -> Table:
        """Retrieve the `settings` table from the `[tool.peeler]` section, excluding `manifest`.

        :return: The `settings` table.
        """
        if not hasattr(self, "_settings_table"):
            _ = self.manifest_table
            self._settings_table = (
                self.peeler_table.remove("manifest") if self.peeler_table else None
            )
        return self._settings_table

    @property
    def manifest_table(self) -> Table:
        """Retrieve the `manifest` table from the `[tool.peeler]` section.

        :return: The `manifest` table.
        """
        if not hasattr(self, "_manifest_table"):
            self._manifest_table = (
                self.peeler_table.get("manifest") if self.peeler_table else None
            )
        return self._manifest_table

    @property
    def dependency_groups(self) -> Table | None:
        """Retrieve the `dependency-groups` table.

        :return: The `dependency-groups` table.
        """
        if not hasattr(self, "_dependency_groups"):
            self._dependency_groups = self._document.get("dependency-groups")

        return self._dependency_groups

    @dependency_groups.setter
    def dependency_groups(
        self, dependency_groups: DependencyGroups | Table | None
    ) -> None:
        """Set the `dependency-groups` table.

        :param dependency_groups: The `dependency-groups` table.
        """
        self._document["dependency-groups"] = dependency_groups


def get_supported_platforms(
    pyproject_path: Path, allow_non_default_name: bool = False
) -> List[str] | None:
    """Get the platforms from the pyproject manifest table.

    :param pyproject_path: The path to the pyproject file or directory.
    :param allow_non_default_name: Whether to allow non-default pyproject file names.
    :return: The list of platforms or None if not found.
    """
    if not (
        pyproject_file := find_pyproject_file(
            pyproject_path, allow_non_default_name=allow_non_default_name
        )
    ):
        return None

    if not (
        manifest_table := PyprojectParser(
            TOMLFile(pyproject_file).read()
        ).manifest_table
    ):
        return None

    if not "platforms" in manifest_table:
        return None

    return manifest_table["platforms"]
