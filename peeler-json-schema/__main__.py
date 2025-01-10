from pathlib import Path
from typing import Dict, Any
import json


def main() -> None:
    """Create a json schema for peeler."""

    # load blender_manifest schema
    # Downloaded from `https://extensions.blender-defender.com/api/blender_manifest_v1.schema.json`
    with Path(
        Path(__file__).parent / "data" / "blender_manifest_schema.json"
    ).open() as input_file:
        bl_manifest_schema: Dict[str, Any] = json.load(input_file)

    # load peeler properties schema
    with Path(
        Path(__file__).parent / "data" / "peeler_schema.json"
    ).open() as input_file:
        peeler_prop: Dict[str, Any] = json.load(input_file)

    # write blender manifest properties into peeler manifest properties
    peeler_prop["properties"]["manifest"]["properties"] = bl_manifest_schema[
        "properties"
    ]

    with Path(Path(__file__).parent / "data" / "peeler_pyproject_schema.json").open(
        "w"
    ) as output_file:
        json.dump(peeler_prop, output_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
