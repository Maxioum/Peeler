from pathlib import Path

from packaging.specifiers import SpecifierSet
from packaging.version import Version
from pytest import mark

from peeler.pyproject.update import update_requires_python
from peeler.pyproject.parser import PyprojectParser


@mark.parametrize(
    "pyproject_requires_python", (None, ">=3.9.0,<3.14", "==3.11.*"), indirect=True
)
def test_update_requires_python(pyproject_requires_python: PyprojectParser) -> None:
    pyproject = update_requires_python(pyproject_requires_python)
    requires_python = SpecifierSet(pyproject.project_table["requires-python"])

    assert requires_python  # no canonical ways to test version range intersection


@mark.parametrize(
    "pyproject_requires_python",
    (">=3.11.10,<3.12", ">=3.11.7,<=3.13", ">3.11.5"),
    indirect=True,
)
def test_update_requires_python_restritive(
    pyproject_requires_python: PyprojectParser,
) -> None:
    pyproject = update_requires_python(pyproject_requires_python)
    requires_python = SpecifierSet(pyproject.project_table["requires-python"])

    assert Version("3.11.5") not in requires_python
