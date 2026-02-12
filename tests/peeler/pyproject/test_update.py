from typing import List

from dep_logic.specifiers import RangeSpecifier, parse_version_specifier
from packaging.version import Version
from pytest import mark

from peeler.pyproject import _BLENDER_SUPPORTED_PYTHON_VERSION
from peeler.pyproject.parser import PyprojectParser
from peeler.pyproject.update import (
    update_dependencies,
    update_dependency_groups,
    update_requires_python,
)

_unsupported_python_versions_sup = RangeSpecifier(
    min=_BLENDER_SUPPORTED_PYTHON_VERSION.max, include_min=True
)
_unsupported_python_versions_inf = RangeSpecifier(max=Version("3.10"), include_max=True)


@mark.parametrize(
    "pyproject_requires_python", (None, ">=3.9.0,<3.14", "==3.11.*"), indirect=True
)
def test_update_requires_python(pyproject_requires_python: PyprojectParser) -> None:
    pyproject = update_requires_python(pyproject_requires_python)
    version_specifier = parse_version_specifier(
        pyproject.project_table["requires-python"]
    )

    assert not (version_specifier & _BLENDER_SUPPORTED_PYTHON_VERSION).is_empty()
    assert (version_specifier & _unsupported_python_versions_sup).is_empty()
    assert (version_specifier & _unsupported_python_versions_inf).is_empty()


@mark.parametrize(
    "pyproject_requires_python",
    (">=3.11.10,<3.12", ">=3.11.7,<3.14", ">3.11.5"),
    indirect=True,
)
def test_update_requires_python_restritive(
    pyproject_requires_python: PyprojectParser,
) -> None:
    pyproject = update_requires_python(pyproject_requires_python)
    version_specifier = parse_version_specifier(
        pyproject.project_table["requires-python"]
    )

    assert Version("3.11.5") not in version_specifier
    assert not (version_specifier & _BLENDER_SUPPORTED_PYTHON_VERSION).is_empty()
    assert (version_specifier & _unsupported_python_versions_sup).is_empty()
    assert (version_specifier & _unsupported_python_versions_inf).is_empty()


@mark.parametrize(
    ("pyproject_dependencies", "excluded_dependencies", "expected_result"),
    (
        [
            [
                [
                    "dep-logic>=0.4.11",
                    "jsonschema>=4.23.0",
                    "packaging>=24.2",
                    "pyproject-metadata>=0.9.0",
                    "rich>=13.9.4",
                ],
                ["packaging"],
                [
                    "dep-logic>=0.4.11",
                    "jsonschema>=4.23.0",
                    "pyproject-metadata>=0.9.0",
                    "rich>=13.9.4",
                ],
            ],
            [
                [
                    "dep-logic>=0.4.11",
                    "jsonschema>=4.23.0",
                    "packaging>=24.2",
                    "pyproject-metadata>=0.9.0",
                    "rich>=13.9.4",
                ],
                ["dep-logic", "packaging", "jsonschema", "pyproject-metadata", "rich"],
                [],
            ],
            [
                [
                    "dep-logic>=0.4.11",
                    "jsonschema>=4.23.0",
                    "packaging>=24.2",
                    "pyproject-metadata>=0.9.0",
                    "rich>=13.9.4",
                ],
                [],
                [
                    "dep-logic>=0.4.11",
                    "jsonschema>=4.23.0",
                    "packaging>=24.2",
                    "pyproject-metadata>=0.9.0",
                    "rich>=13.9.4",
                ],
            ],
            [
                [
                    "dep-logic>=0.4.11",
                    "jsonschema>=4.23.0",
                    "packaging>=24.2",
                    "pyproject-metadata>=0.9.0",
                    "rich>=13.9.4",
                ],
                ["numpy"],
                [
                    "dep-logic>=0.4.11",
                    "jsonschema>=4.23.0",
                    "packaging>=24.2",
                    "pyproject-metadata>=0.9.0",
                    "rich>=13.9.4",
                ],
            ],
            [
                [
                    "dep-logic>=0.4.11",
                    "jsonschema>=4.23.0",
                    "packaging>=24.2",
                    "pyproject-metadata>=0.9.0",
                    "rich>=13.9.4",
                ],
                ["dep_lOgic", "pYproJect.MetadaTA"],
                [
                    "jsonschema>=4.23.0",
                    "packaging>=24.2",
                    "rich>=13.9.4",
                ],
            ],
        ]
    ),
    indirect=["pyproject_dependencies"],
)
def test_update_dependencies(
    pyproject_dependencies: PyprojectParser,
    excluded_dependencies: List[str],
    expected_result: List[str],
) -> None:
    assert (
        update_dependencies(
            pyproject_dependencies, excluded_dependencies
        ).project_table.get("dependencies")
        == expected_result
    )


@mark.parametrize(
    ("pyproject_dependency_groups", "excluded_dependency_groups", "expected_result"),
    (
        [
            [{}, [], {}],
            [{}, ["non_existant_group"], {}],
            [{"group1": ["package1.1"]}, [], {"group1": ["package1.1"]}],
            [
                {"group1": ["package1.1"], "group2": ["pacakge2.1"]},
                ["group2"],
                {"group1": ["package1.1"]},
            ],
            [
                {"group1": ["package1.1"], "group2": ["pacakge2.1"]},
                ["non_existant_group"],
                {"group1": ["package1.1"], "group2": ["pacakge2.1"]},
            ],
            [
                {
                    "group1": ["package1.1"],
                    "group2": ["pacakge2.1", {"include-group": "group1"}],
                },
                ["group2"],
                {"group1": ["package1.1"]},
            ],
            [
                {
                    "group1": ["package1.1", {"include-group": "group2"}],
                    "group2": [
                        "pacakge2.1",
                    ],
                },
                ["group2"],
                {"group1": ["package1.1", {"include-group": "group2"}]},
            ],
        ]
    ),
    indirect=["pyproject_dependency_groups"],
)
def test_update_dependency_groups(
    pyproject_dependency_groups: PyprojectParser,
    excluded_dependency_groups: List[str],
    expected_result: List[str],
) -> None:
    assert (
        update_dependency_groups(
            pyproject_dependency_groups, excluded_dependency_groups
        ).dependency_groups
        == expected_result
    )
