from typing import Dict, Any
from pytest import FixtureRequest, fixture
from pathlib import Path
import json
from peeler import DATA_DIR
import tomlkit
from tomlkit import TOMLDocument

TEST_DATA_DIR = Path(__file__).parent / "data"


@fixture
def json_schema(request: FixtureRequest) -> Dict[str, Any]:
    path: Path = DATA_DIR / request.param

    with path.open() as file:
        return json.load(file)


@fixture
def toml_document(request: FixtureRequest) -> TOMLDocument:
    path: Path = TEST_DATA_DIR / request.param

    with path.open() as file:
        return tomlkit.load(file)
