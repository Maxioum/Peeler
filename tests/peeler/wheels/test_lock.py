from pathlib import Path

import pytest
from tomlkit import TOMLDocument

from peeler.wheels.lock import _generate_lock_file, _get_wheels_urls_from_lock


def test__get_wheels_urls_from_lock(lock_file: TOMLDocument) -> None:
    assert _get_wheels_urls_from_lock(lock_file) == {
        "package1": ["wheels_url_package1"],
        "package2": ["wheels_url_package2_1", "wheels_url_package2_2"],
    }


@pytest.mark.parametrize(
    "unlink",
    [True, False],
    ids=["unlink_True", "unlink_False"]
)
def test__generate_lock_file(pyproject_path: Path, unlink: bool) -> None:
    with _generate_lock_file(pyproject_path, unlink=unlink) as lock_file:
        assert lock_file.exists()

    assert unlink != lock_file.exists()
