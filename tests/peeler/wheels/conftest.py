import shutil
from pathlib import Path

import tomlkit
from pytest import TempdirFactory, fixture
from tomlkit import TOMLDocument

TEST_DATA_DIR = Path(__file__).parent / "data"


@fixture
def lock_file() -> TOMLDocument:
    path: Path = TEST_DATA_DIR / "lock_file.lock"
    with path.open() as file:
        return tomlkit.load(file)


@fixture
def pyproject_path(tmpdir_factory: TempdirFactory) -> Path:
    return shutil.copy2(
        TEST_DATA_DIR / "pyproject.toml",
        Path(tmpdir_factory.mktemp("temp_dir")) / "pyproject.toml",
    )
