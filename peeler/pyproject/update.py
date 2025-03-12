# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

from packaging.specifiers import SpecifierSet

from peeler.pyproject.parser import PyprojectParser

_BLENDER_SUPPORTED_PYTHON_VERSIONS = SpecifierSet(">=3.11,<3.12")


def update_requires_python(pyproject: PyprojectParser) -> PyprojectParser:
    """Update a pyproject file to restrict project supported python version to the versions supported by Blender.

    The specifier set will not be resolved, and can lead to contradictions.

    :param pyproject_file: the pyproject

    :return: the parsed pyproject
    """

    requires_python = SpecifierSet(
        str(pyproject.project_table.get("requires-python", ""))
    )

    requires_python &= _BLENDER_SUPPORTED_PYTHON_VERSIONS

    pyproject.project_table.update({"requires-python": str(requires_python)})

    return pyproject
