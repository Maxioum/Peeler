import shutil
from pathlib import Path

import tomlkit
from pytest import FixtureRequest, fixture
from tomlkit import TOMLDocument

from peeler.wheels.lock import UrlFetcherCreator

TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_PYPROJECT = TEST_DATA_DIR / "pyproject.toml"
TEST_LOCK = TEST_DATA_DIR / "uv.lock"


@fixture
def uv_lock_file() -> TOMLDocument:
    path: Path = TEST_DATA_DIR / "lock_file_uv.toml"
    with path.open() as file:
        return tomlkit.load(file)

@fixture
def pylock_file() -> TOMLDocument:
    path: Path = TEST_DATA_DIR / "lock_file_pylock.toml"
    with path.open() as file:
        return tomlkit.load(file)


@fixture
def pyproject_path_with_lock(tmp_path: Path) -> Path:
    shutil.copy2(TEST_LOCK, tmp_path / TEST_LOCK.name)
    return Path(shutil.copy2(TEST_PYPROJECT, tmp_path / TEST_PYPROJECT.name))


@fixture
def pyproject_path_without_lock(tmp_path: Path) -> Path:
    return Path(shutil.copy2(TEST_PYPROJECT, tmp_path / TEST_PYPROJECT.name))



@fixture
def url_fetcher_creator(request: FixtureRequest) -> UrlFetcherCreator:
    return UrlFetcherCreator(request.param)