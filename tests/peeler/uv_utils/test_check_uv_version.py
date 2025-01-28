from collections.abc import Generator
from typing import Any
from unittest import mock
from unittest.mock import MagicMock, Mock

import pytest
from click import ClickException
from pytest import fixture

from peeler import uv_utils
from peeler.uv_utils import check_uv_version, find_uv_bin


@fixture(autouse=True)
def patch_find_uv_bin() -> Generator[None, Any, None]:
    with mock.patch(
        f"{uv_utils.__name__}.{find_uv_bin.__name__}",
        return_value="uv",
    ) as find_uv_bin_mock:
        yield


@pytest.mark.parametrize(
    "run_stdout",
    ["uv 0.5.17 (c198e2233 2025-01-10)", "uv 0.5.24 (42fae925c 2025-01-23)"],
)
@mock.patch("peeler.uv_utils.run")
def test_check_uv_version_valid(mock_run: Mock, run_stdout: str) -> None:
    mock_stdout = MagicMock()
    mock_stdout.configure_mock(**{"stdout": run_stdout})
    mock_run.return_value = mock_stdout
    try:
        check_uv_version()
    except ClickException as e:
        pytest.fail(f"Should not raise a ClickException: {e.message}")


@pytest.mark.parametrize("run_stdout", ["uv 0.4.0", "uv not found"])
@mock.patch("peeler.uv_utils.run")
def test_check_uv_version_raises(mock_run: Mock, run_stdout: str) -> None:
    mock_stdout = MagicMock()
    mock_stdout.configure_mock(**{"stdout": run_stdout})
    mock_run.return_value = mock_stdout
    with pytest.raises(ClickException):
        check_uv_version()
