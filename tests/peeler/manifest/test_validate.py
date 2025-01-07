import pytest
from tomlkit import TOMLDocument
from jsonschema.exceptions import ValidationError

from peeler.manifest.validate import validate_manifest


@pytest.mark.parametrize(("toml_document"), [("blender_manifest.toml")], indirect=True)
def test_validate_manifest(toml_document: TOMLDocument) -> None:
    try:
        validate_manifest(toml_document)
    except ValidationError as e:
        pytest.fail(f"Should not raise a ValidationError: {e.message}")


def test_validate_manifest_empty_dict() -> None:
    with pytest.raises(ValidationError):
        validate_manifest({})
