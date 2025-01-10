from typing import Dict, Any
from pytest import FixtureRequest, fixture
from pathlib import Path
import json

import tomlkit
from tomlkit import TOMLDocument

from peeler import DATA_DIR

TEST_DATA_DIR = Path(__file__).parent / "data"


@fixture
def blender_manifest_schema() -> Dict[str, Any]:
    path: Path = DATA_DIR / "blender_manifest_schema.json"
    with path.open() as file:
        return json.load(file)


@fixture
def peeler_manifest_schema() -> Dict[str, Any]:
    path: Path = DATA_DIR / "peeler_pyproject_schema.json"
    with path.open() as file:
        return json.load(file)


@fixture
def toml_document(request: FixtureRequest) -> TOMLDocument:
    path: Path = TEST_DATA_DIR / request.param

    with path.open() as file:
        return tomlkit.load(file)
