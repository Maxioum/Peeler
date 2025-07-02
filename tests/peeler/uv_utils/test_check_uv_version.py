import os
from unittest import mock
from unittest.mock import MagicMock, Mock

import pytest
from click import ClickException

from peeler.uv_utils import check_uv_version


@pytest.mark.skipif(
    os.environ.get("CI-on-uv-release") == "true",
    reason="Disable in on-uv-release workflow",
)
def test_check_uv_version() -> None:
    try:
        check_uv_version()
    except ClickException as e:
        pytest.fail(f"Should not raise a ClickException: {e.message}")


@pytest.mark.parametrize(
    "run_stdout",
    ["uv 0.7.2 (481d05d8d 2025-04-30)"],
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
