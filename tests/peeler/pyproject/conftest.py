from pathlib import Path
from typing import Any, Dict

import tomlkit
from pytest import FixtureRequest, fixture
from tomlkit import TOMLDocument
from tomlkit.items import Table
from tomlkit.toml_file import TOMLFile

from peeler.pyproject.manifest_adapter import ManifestAdapter
from peeler.pyproject.validator import PyprojectValidator

TEST_DATA_DIR = Path(__file__).parent / "data"
PYPROJECT_MINIMAL = TEST_DATA_DIR / "pyproject_no_peeler_table.toml"


@fixture
def pyproject_requires_python(request: FixtureRequest) -> PyprojectValidator:
    key = "requires-python"

    pyproject = PyprojectValidator(TOMLFile(PYPROJECT_MINIMAL).read())

    requires_python: str | None = request.param

    if requires_python is not None:
        pyproject.project_table.update({key: str(request.param)})
    elif key in pyproject.project_table:
        del pyproject.project_table[key]

    return pyproject


@fixture
def pyproject(request: FixtureRequest) -> TOMLDocument:
    path: Path = TEST_DATA_DIR / Path(request.param)

    with path.open() as file:
        return tomlkit.load(file)


@fixture
def validator(request: FixtureRequest) -> PyprojectValidator:
    path: Path = TEST_DATA_DIR / request.param

    with path.open() as file:
        return PyprojectValidator(tomlkit.load(file), path)


@fixture(scope="function")
def manifest_adapter(
    request: FixtureRequest,
    blender_manifest_schema: Dict[str, Any],
    peeler_manifest_schema: Dict[str, Any],
) -> ManifestAdapter:
    path: Path = TEST_DATA_DIR / request.param

    with path.open() as file:
        return ManifestAdapter(
            tomlkit.load(file), blender_manifest_schema, peeler_manifest_schema
        )


@fixture(scope="function")
def validator_requires_python(request: FixtureRequest) -> PyprojectValidator:
    path: Path = TEST_DATA_DIR / "pyproject_minimal.toml"

    document = TOMLFile(path).read()

    project_table: Table = document.get("project")

    project_table.update({"requires-python": request.param})

    return PyprojectValidator(document, path)
