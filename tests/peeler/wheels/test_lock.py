from pathlib import Path
from typing import Type

from pytest import mark
from tomlkit import TOMLDocument

from peeler.wheels.lock import AbstractURLFetcherStrategy, PylockUrlFetcher, PyprojectUVLockFetcher, UVLockUrlFetcher, UrlFetcherCreator, _generate_uv_lock, _get_wheels_urls_from_lock


def test__get_wheels_urls_from_lock(lock_file: TOMLDocument) -> None:
    assert _get_wheels_urls_from_lock(lock_file) == {
        "package1": ["wheels_url_package1"],
        "package2": ["wheels_url_package2_1", "wheels_url_package2_2"],
    }


def test__get_lock_file(pyproject_path_with_lock: Path) -> None:
    with _generate_uv_lock(pyproject_path_with_lock) as lock_file:
        assert lock_file.exists()

    assert lock_file.exists()


def test__get_lock_file_no_lock_file(pyproject_path_without_lock: Path) -> None:
    with _generate_uv_lock(pyproject_path_without_lock) as lock_file:
        assert lock_file.exists()

    assert not lock_file.exists()

_DATA = Path(__file__).parent / "data"

@mark.parametrize(
    ("url_fetcher_creator", "expected_strategy"),
    [
        (_DATA / "pyproject.toml", PyprojectUVLockFetcher),
        (_DATA / "uv.lock", UVLockUrlFetcher),
        (_DATA / "pylock.toml", PylockUrlFetcher),
        (_DATA / "pylock.test.toml", PylockUrlFetcher),
    ],
    indirect=["url_fetcher_creator"]
)
def test_url_fetcher_creator_get_fetch_url_strategy(url_fetcher_creator: UrlFetcherCreator, expected_strategy: Type[AbstractURLFetcherStrategy]) -> None:

    assert isinstance(url_fetcher_creator.get_fetch_url_strategy(), expected_strategy)