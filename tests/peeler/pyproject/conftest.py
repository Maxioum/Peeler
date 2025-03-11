from pathlib import Path
from typing import Any, Dict

import tomlkit
from pytest import FixtureRequest, fixture
from tomlkit import TOMLDocument
from tomlkit.items import Table
from tomlkit.toml_file import TOMLFile

from peeler.pyproject.parse import Parser
from peeler.pyproject.validator import Validator

TEST_DATA_DIR = Path(__file__).parent / "data"


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

@fixture(scope="function")
def validator_requires_python(request: FixtureRequest) -> Validator:
    path: Path = TEST_DATA_DIR / "pyproject_minimal.toml"

    document = TOMLFile(path).read()

    project_table: Table = document.get("project")

    project_table.update({"requires-python": request.param})

    return Validator(document, path)

