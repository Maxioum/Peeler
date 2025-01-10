from pathlib import Path

import pytest
from tomlkit import TOMLDocument
from tomlkit.toml_file import TOMLFile

from peeler.manifest.write import (
    _write,
    export_to_blender_manifest,
    BLENDER_MANIFEST_FILENAME,
)


@pytest.mark.parametrize(("toml_document"), [("blender_manifest.toml")], indirect=True)
def test_write_manifest(toml_document: TOMLDocument, tmpdir: str) -> None:
    output_path = Path(tmpdir) / "blender_manifest.toml"

    _write(toml_document, output_path)

    assert Path(output_path).exists()


@pytest.mark.parametrize(("toml_document"), [("blender_manifest.toml")], indirect=True)
def test_write_manifest_unchanged(toml_document: TOMLDocument, tmpdir: str) -> None:
    output_path = Path(tmpdir) / "blender_manifest.toml"

    _write(toml_document, output_path)

    content = Path(output_path).read_text()
    assert content == toml_document.as_string()


@pytest.mark.parametrize(
    ("toml_document", "overwrite"),
    [("simple.toml", True), ("simple.toml", False)],
    indirect=["toml_document"],
)
def test_write_manifest_update(
    toml_document: TOMLDocument, tmpdir: str, overwrite: bool
) -> None:
    # write first toml to disk
    path = Path(tmpdir, "temp_simple.toml")
    TOMLFile(path).write(toml_document)

    # create copy and modify a value
    toml_copy = toml_document.copy()
    toml_copy.update({"boolean": not toml_document["boolean"]})

    # call the function with overwrite arg
    _write(toml_copy, path, overwrite=overwrite)

    # check if the value has changed according to the overwrite parameter
    value = TOMLFile(path).read()["boolean"]

    if overwrite:
        assert value != toml_document["boolean"]
    else:
        assert value == toml_document["boolean"]


@pytest.mark.parametrize(("toml_document"), [("blender_manifest.toml")], indirect=True)
def test_export_to_blender_manifest_dirname(
    toml_document: TOMLDocument, tmpdir: str
) -> None:
    assert export_to_blender_manifest(
        toml_document, Path(tmpdir), allow_non_default_name=False
    ).exists()


@pytest.mark.parametrize(("toml_document"), [("blender_manifest.toml")], indirect=True)
def test_export_to_blender_manifest_value_error(
    toml_document: TOMLDocument, tmpdir: str
) -> None:
    with pytest.raises(ValueError):
        export_to_blender_manifest(
            toml_document,
            Path(tmpdir, "3dsmax_manifest.toml"),
            allow_non_default_name=False,
        )


@pytest.mark.parametrize(("toml_document"), [("blender_manifest.toml")], indirect=True)
def test_export_to_blender_manifest_filename(
    toml_document: TOMLDocument, tmpdir: str
) -> None:
    assert export_to_blender_manifest(
        toml_document,
        Path(tmpdir) / BLENDER_MANIFEST_FILENAME,
        allow_non_default_name=False,
    ).exists()
