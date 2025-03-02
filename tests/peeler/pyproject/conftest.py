from pathlib import Path
from typing import Any, Dict

import tomlkit
from pytest import FixtureRequest, fixture
from tomlkit import TOMLDocument
from tomlkit.toml_file import TOMLFile

from peeler.pyproject.parse import Parser
from peeler.pyproject.utils import Pyproject
from peeler.pyproject.validator import Validator

TEST_DATA_DIR = Path(__file__).parent / "data"
PYPROJECT_MINIMAL = TEST_DATA_DIR / "pyproject_no_peeler_table.toml"


@fixture
def pyproject_requires_python(request: FixtureRequest) -> Pyproject:
    key = "requires-python"

    pyproject = Pyproject(TOMLFile(PYPROJECT_MINIMAL).read())

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
def validator(request: FixtureRequest) -> Validator:
    path: Path = TEST_DATA_DIR / request.param

    with path.open() as file:
        return Validator(tomlkit.load(file), path)


@fixture(scope="function")
def parser(
    request: FixtureRequest,
    blender_manifest_schema: Dict[str, Any],
    peeler_manifest_schema: Dict[str, Any],
) -> Parser:
    path: Path = TEST_DATA_DIR / request.param

    with path.open() as file:
        return Parser(
            tomlkit.load(file), blender_manifest_schema, peeler_manifest_schema
        )
