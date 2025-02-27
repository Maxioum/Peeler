import pytest
from validate_pyproject.error_reporting import ValidationError

from peeler.pyproject.validator import Validator


@pytest.mark.parametrize(
    "validator",
    [
        "pyproject_minimal.toml",
    ],
    indirect=True,
)
def test_validator(validator: Validator) -> None:
    try:
        validator.validate()
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
def test_validator_invalid(validator: Validator, match: str) -> None:
    with pytest.raises(ValidationError, match=match):
        validator.validate()


@pytest.mark.parametrize(
    "validator_requires_python",
    [
        ">=3.6",
        "==3.11",
    ],
    indirect=True,
)
def test_validator_requires_python(validator_requires_python: Validator) -> None:

    validator_requires_python.validate()

@pytest.mark.parametrize(
    "validator_requires_python",
    [
        "<=3.5",
        "<3.11",
    ],
    indirect=True,
)
def test_validator_requires_python_invalid(validator_requires_python: Validator) -> None:
    with pytest.raises(ValidationError):
        validator_requires_python.validate()