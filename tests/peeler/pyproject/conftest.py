from pytest import fixture, FixtureRequest
from pathlib import Path
import tomlkit
from tomlkit import TOMLDocument

from peeler.pyproject.validator import Validator


TEST_DATA_DIR = Path(__file__).parent / "data"
pyprojects = [p for p in TEST_DATA_DIR.glob("pyproject*.toml") if p.is_file()]


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
