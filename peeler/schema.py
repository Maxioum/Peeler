import json
from pathlib import Path
from typing import Any, Dict

from . import DATA_DIR


peeler_json_schema_path = DATA_DIR / "peeler_pyproject_schema.json"
blender_manifest_schema_path = DATA_DIR / "blender_manifest_schema.json"


def peeler_json_schema() -> Dict[str, Any]:
    """Return the [tool.peeler] table json schema.

    :return: the schema as a Dict
    """

    with Path(peeler_json_schema_path).open() as file:
        return json.load(file)


def blender_manifest_json_schema() -> Dict[str, Any]:
    """Return the blender_manifest.toml json schema.

    Downloaded from `https://extensions.blender-defender.com/api/blender_manifest_v1.schema.json`

    :return: the schema as a Dict
    """
    with Path(blender_manifest_schema_path).open() as file:
        return json.load(file)
