import json
from pathlib import Path
from typing import Any, Dict

from . import DATA_DIR


peeler_json_schema_path = DATA_DIR / "peeler_pyproject_schema.json"


def peeler_json_schema() -> Dict[str, Any]:
    """Return the [tool.peeler] table json schema.

    :return: the schema as a Dict
    """

    with Path(peeler_json_schema_path).open() as file:
        return json.load(file)
