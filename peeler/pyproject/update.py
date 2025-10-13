# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later


from typing import List

import typer
from dep_logic.specifiers import parse_version_specifier
from packaging.requirements import Requirement
from tomlkit.items import Table

from peeler.pyproject import _BLENDER_SUPPORTED_PYTHON_VERSION
from peeler.pyproject.parser import DependencyGroups, PyprojectParser
from peeler.utils import normalize_package_name


def update_requires_python(pyproject: PyprojectParser) -> PyprojectParser:
    """Update a pyproject file to restrict project supported python version to the versions supported by Blender.

    The specifier set will not be resolved, and can lead to contradictions.

    :param pyproject_file: the pyproject

    :return: the parsed pyproject
    """

    requires_python = parse_version_specifier(
        pyproject.project_table.get("requires-python", "")
    )

    requires_python &= _BLENDER_SUPPORTED_PYTHON_VERSION

    pyproject.project_table.update({"requires-python": str(requires_python)})

    return pyproject


def update_dependencies(
    pyproject: PyprojectParser, excluded_dependencies: List[str]
) -> PyprojectParser:
    """Update a pyproject file to remove dependencies from [project].dependencies table.

    :param pyproject_file: the pyproject

    :return: the parsed pyproject
    """
    dependencies: List[str] | None = pyproject.project_table.get("dependencies", None)

    if not excluded_dependencies or not dependencies:
        return pyproject

    _excluded_dependencies = {
        normalize_package_name(package) for package in excluded_dependencies
    }

    _requirements = [Requirement(dependency) for dependency in dependencies]

    _requirements_filtered = list(
        filter(
            lambda req: normalize_package_name(req.name) not in _excluded_dependencies,
            _requirements,
        )
    )

    pyproject.project_table.update(
        {"dependencies": [str(req) for req in _requirements_filtered]}
    )

    return pyproject


def _warn_non_existant_group(group: str) -> None:
    typer.echo(f"Warning: Excluded dependency group `{group}` not found")


def update_dependency_groups(
    pyproject: PyprojectParser, excluded_dependency_groups: List[str]
) -> PyprojectParser:
    """Update a pyproject file to remove dependency group from [dependecy-groups] table.

    :param pyproject_file: the pyproject

    :return: the parsed pyproject
    """
    dependency_groups = pyproject.dependency_groups

    if not dependency_groups:
        for group in excluded_dependency_groups:
            _warn_non_existant_group(group)
        return pyproject

    for group in excluded_dependency_groups:
        if group in dependency_groups:
            del dependency_groups[group]
        else:
            _warn_non_existant_group(group)

    pyproject.dependency_groups = dependency_groups

    return pyproject
