import pytest
from validate_pyproject.error_reporting import ValidationError

from peeler.pyproject.validator import PyprojectValidator


@pytest.mark.parametrize(
    "validator",
    [
        "pyproject_minimal.toml",
    ],
    indirect=True,
)
def test_validator(validator: PyprojectValidator) -> None:
    try:
        validator()
    except ValidationError as e:
        pytest.fail(f"Should not raise a ValidationError: {e.message}")


@pytest.mark.parametrize(
    ("validator", "match"),
    [
        (
            "pyproject_no_manifest_table.toml",
            r"(tool.peeler).+(contain).+(manifest).+(properties)",
        ),
        ("pyproject_no_peeler_table.toml", r"(contain).+(tool.peeler).+(table)"),
        (
            "pyproject_peeler_table_empty.toml",
            r"(tool.peeler).+(contain).+(manifest).+(properties)",
        ),
    ],
    indirect=["validator"],
)
def test_validator_invalid(validator: PyprojectValidator, match: str) -> None:
    with pytest.raises(ValidationError, match=match):
        validator()


@pytest.mark.parametrize(
    "validator",
    [
        "pyproject_minimal.toml",
    ],
    indirect=True,
)
def test_validator_requires_python_empty(validator: PyprojectValidator) -> None:
    try:
        validator()
    except ValidationError as e:
        pytest.fail(f"Should not raise a ValidationError: {e.message}")


@pytest.mark.parametrize(
    "validator_requires_python",
    [">=3.6", "==3.11.*", ">=3.11.9,<3.13", "~=3.11.2", "==3.11.7"],
    indirect=True,
)
def test_validator_requires_python(
    validator_requires_python: PyprojectValidator,
) -> None:
    try:
        validator_requires_python()
    except ValidationError as e:
        pytest.fail(f"Should not raise a ValidationError: {e.message}")


@pytest.mark.parametrize(
    "validator_requires_python",
    [
        "<=3.5",
        "<3.11",
        ">=3.12.0,<3.13",
        "~=3.12.0",
        "~=3.7.0",
    ],
    indirect=True,
)
def test_validator_requires_python_invalid(
    validator_requires_python: PyprojectValidator,
) -> None:
    with pytest.raises(ValidationError, match="requires-python"):
        validator_requires_python()
