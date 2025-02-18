import shutil
from pathlib import Path

import tomlkit
from pytest import TempdirFactory, fixture
from tomlkit import TOMLDocument

TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_PYPROJECT = TEST_DATA_DIR / "pyproject.toml"
TEST_LOCK = TEST_DATA_DIR / "uv.lock"


@fixture
def lock_file() -> TOMLDocument:
    path: Path = TEST_DATA_DIR / "lock_file.lock"
    with path.open() as file:
        return tomlkit.load(file)


@fixture
def pyproject_path_with_lock(tmp_path: Path) -> Path:
    shutil.copy2(TEST_LOCK, tmp_path / TEST_LOCK.name)
    return shutil.copy2(TEST_PYPROJECT, tmp_path / TEST_PYPROJECT.name)


@fixture
def pyproject_path_without_lock(tmp_path: Path) -> Path:
    return shutil.copy2(TEST_PYPROJECT, tmp_path / TEST_PYPROJECT.name)
