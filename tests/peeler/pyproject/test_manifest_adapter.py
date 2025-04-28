import pytest

from peeler.pyproject.manifest_adapter import ManifestAdapter


@pytest.mark.parametrize(
    "manifest_adapter", [("pyproject_minimal.toml")], indirect=["manifest_adapter"]
)
def test_parser(manifest_adapter: ManifestAdapter) -> None:
    assert manifest_adapter.to_blender_manifest()
