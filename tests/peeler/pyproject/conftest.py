from typing import Any, Dict
from pytest import fixture, FixtureRequest
from pathlib import Path
import tomlkit
from tomlkit import TOMLDocument

from peeler.pyproject.validator import Validator
from peeler.pyproject.parse import Parser


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
