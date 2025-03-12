from dep_logic.specifiers import RangeSpecifier, parse_version_specifier
from packaging.version import Version
from pytest import mark

from peeler.pyproject import _BLENDER_SUPPORTED_PYTHON_VERSION
from peeler.pyproject.update import update_requires_python
from peeler.pyproject.parser import PyprojectParser

_unsupported_python_versions_sup = RangeSpecifier(min=Version("3.12"), include_min=True)
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
