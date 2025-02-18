from collections.abc import Generator
from pathlib import Path
from tempfile import NamedTemporaryFile

from pytest import fixture, raises

from peeler.utils import restore_file

_ORIGINAL_CONTENT = "Original Content"
_TEMP_CONTENT = "Temporary Content"


@fixture
def original_file() -> Generator[Path, None, None]:
    with NamedTemporaryFile(mode="w", delete=False) as tmp:
        tmp.write(_ORIGINAL_CONTENT)

    try:
        yield Path(tmp.name)
    finally:
        tmp.close()


def test_restore_file(original_file: Path) -> None:
    with restore_file(original_file):
        original_file.write_text(_TEMP_CONTENT)

    assert original_file.read_text() == _ORIGINAL_CONTENT


def test_restore_file_on_exception(original_file: Path) -> None:
    class SomeError(Exception):
        pass

    try:
        with restore_file(original_file):
            original_file.write_text(_TEMP_CONTENT)
            raise SomeError()
    except SomeError:
        ...

    assert original_file.read_text() == _ORIGINAL_CONTENT


def test_restore_file_on_deleted(original_file: Path) -> None:
    with restore_file(original_file):
        original_file.unlink()

    assert original_file.exists()
    assert original_file.read_text() == _ORIGINAL_CONTENT


def test_restore_file_on_exit(original_file: Path) -> None:
    try:
        with restore_file(original_file):
            original_file.write_text(_TEMP_CONTENT)
            exit(0)
    except SystemExit:
        ...

    assert original_file.read_text() == _ORIGINAL_CONTENT


def test_restore_file_file_missing(original_file: Path) -> None:
    original_file.unlink()

    with restore_file(original_file, missing_ok=True):
        original_file.write_text(_TEMP_CONTENT)

    assert not original_file.exists()


def test_restore_file_file_missing_raises(original_file: Path) -> None:
    original_file.unlink()

    with raises(FileNotFoundError):
        with restore_file(original_file, missing_ok=False):
            original_file.write_text(_TEMP_CONTENT)

    assert not original_file.exists()


def test_restore_file_twice(original_file: Path) -> None:
    with restore_file(original_file):
        original_file.write_text(_TEMP_CONTENT)

        with restore_file(original_file):
            original_file.write_text(_TEMP_CONTENT + _TEMP_CONTENT)

        assert original_file.read_text() == _TEMP_CONTENT

    assert original_file.read_text() == _ORIGINAL_CONTENT
