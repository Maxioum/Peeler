from pathlib import Path
from typing import Dict, List, Set, Type

from pytest import fixture, mark
from tomlkit import TOMLDocument

from peeler.wheels.lock import AbstractURLFetcherStrategy, PylockUrlFetcher, PyprojectUVLockFetcher, UVLockUrlFetcher, UrlFetcherCreator, _generate_uv_lock, _get_wheels_urls_from_uv_lock, _get_wheels_urls_from_pylock


def test__get_wheels_urls_from_uv_lock(uv_lock_file: TOMLDocument) -> None:
    assert _get_wheels_urls_from_uv_lock(uv_lock_file) == {
        "package1": ["wheels_url_package1"],
        "package2": ["wheels_url_package2_1", "wheels_url_package2_2"],
    }

def test__get_wheels_urls_from_pylock(pylock_file: TOMLDocument) -> None:
    assert _get_wheels_urls_from_pylock(pylock_file) == {
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


@fixture
def urls() -> Set[str]:
    return {
        "https://files.pythonhosted.org/packages/11/57/baae43d14fe163fa0e4c47f307b6b2511ab8d7d30177c491960504252053/numpy-1.26.4-cp311-cp311-macosx_10_9_x86_64.whl",
        "https://files.pythonhosted.org/packages/1a/2e/151484f49fd03944c4a3ad9c418ed193cfd02724e138ac8a9505d056c582/numpy-1.26.4-cp311-cp311-macosx_11_0_arm64.whl",
        "https://files.pythonhosted.org/packages/79/ae/7e5b85136806f9dadf4878bf73cf223fe5c2636818ba3ab1c585d0403164/numpy-1.26.4-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl",
        "https://files.pythonhosted.org/packages/3a/d0/edc009c27b406c4f9cbc79274d6e46d634d139075492ad055e3d68445925/numpy-1.26.4-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
        "https://files.pythonhosted.org/packages/09/bf/2b1aaf8f525f2923ff6cfcf134ae5e750e279ac65ebf386c75a0cf6da06a/numpy-1.26.4-cp311-cp311-musllinux_1_1_aarch64.whl",
        "https://files.pythonhosted.org/packages/df/a0/4e0f14d847cfc2a633a1c8621d00724f3206cfeddeb66d35698c4e2cf3d2/numpy-1.26.4-cp311-cp311-musllinux_1_1_x86_64.whl",
        "https://files.pythonhosted.org/packages/d2/b7/a734c733286e10a7f1a8ad1ae8c90f2d33bf604a96548e0a4a3a6739b468/numpy-1.26.4-cp311-cp311-win32.whl",
        "https://files.pythonhosted.org/packages/3f/6b/5610004206cf7f8e7ad91c5a85a8c71b2f2f8051a0c0c4d5916b76d6cbb2/numpy-1.26.4-cp311-cp311-win_amd64.whl",
    }

@mark.parametrize(
    "url_fetcher",
    [
        UVLockUrlFetcher(_DATA / "uv.lock"),
        PyprojectUVLockFetcher(_DATA / "pyproject.toml"),
        PylockUrlFetcher(_DATA / "pylock.toml")
    ],
    ids=["uv_lock", "pyproject", "pylock"]
)
def test_url_fetcher(url_fetcher: AbstractURLFetcherStrategy, urls: Set[str]) -> None:

    assert set(url_fetcher.get_urls()["numpy"]) == urls