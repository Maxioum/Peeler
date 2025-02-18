from pathlib import Path

from tomlkit import TOMLDocument

from peeler.wheels.lock import _get_lock_file, _get_wheels_urls_from_lock


def test__get_wheels_urls_from_lock(lock_file: TOMLDocument) -> None:
    assert _get_wheels_urls_from_lock(lock_file) == {
        "package1": ["wheels_url_package1"],
        "package2": ["wheels_url_package2_1", "wheels_url_package2_2"],
    }


def test__get_lock_file(pyproject_path_with_lock: Path) -> None:
    with _get_lock_file(pyproject_path_with_lock) as lock_file:
        assert lock_file.exists()

    assert lock_file.exists()


def test__get_lock_file_no_lock_file(pyproject_path_without_lock: Path) -> None:
    with _get_lock_file(pyproject_path_without_lock) as lock_file:
        assert lock_file.exists()

    assert not lock_file.exists()
