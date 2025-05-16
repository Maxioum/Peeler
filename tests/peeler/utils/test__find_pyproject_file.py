from pathlib import Path

from clypi import AbortException
from pytest import fixture, raises

from peeler.command.manifest import PYPROJECT_FILENAME, _find_pyproject_file


@fixture
def pyproject_file(tmp_path: Path) -> Path:
    pyproject = tmp_path / PYPROJECT_FILENAME
    with pyproject.open("w") as file:
        file.write("some text")

    return pyproject


@fixture
def pyproject_directory(pyproject_file: Path) -> Path:
    return pyproject_file.parent


def test__find_pyproject_file_no_pyproject(tmp_path: Path) -> None:
    with raises(AbortException, match=f"No {PYPROJECT_FILENAME} found at"):
        _find_pyproject_file(tmp_path)


def test__find_pyproject_file(pyproject_file: Path) -> None:
    assert _find_pyproject_file(pyproject_file) == pyproject_file


def test__find_pyproject_dir(pyproject_directory: Path, pyproject_file: Path) -> None:
    assert _find_pyproject_file(pyproject_directory) == pyproject_file
