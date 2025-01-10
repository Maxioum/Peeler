from tomlkit import TOMLDocument
import jsonschema

from ..schema import blender_manifest_json_schema


def validate_manifest(blender_manifest: TOMLDocument) -> None:
    """Validate a blender_manifest.

    Validate using a json schema.

    :param blender_manifest: the blender_manifest as `TOMLDocument`
    """

    schema = blender_manifest_json_schema()

    jsonschema.validate(blender_manifest, schema)
