from typing import Any, Dict
from pathlib import Path

from fastjsonschema import JsonSchemaValueException
from tomlkit import TOMLDocument
from validate_pyproject.api import Validator as _Validator
from validate_pyproject.plugins import PluginWrapper

from .utils import Pyproject
from ..schema import peeler_json_schema


def _peeler_plugin(peeler: str) -> Dict[str, Any]:
    json_schema = peeler_json_schema()
    return {"$id": json_schema["$schema"][:-1], **json_schema}


class Validator:
    """A tool to validate a pyproject.

    :param pyproject: the pyproject as a `TOMLDocument`
    :param pyproject_path: the pyproject path (for error reporting)
    """

    def __init__(self, pyproject: TOMLDocument, pyproject_path: Path) -> None:
        self.pyproject = pyproject
        self.pyproject_path = pyproject_path

    def _validate_has_peeler_table(self, pyproject: TOMLDocument) -> None:
        """Raise an error if the peeler table is missing or empty.

        :param pyproject: the pyproject
        :raises JsonSchemaValueException: on missing or empty [tool.peeler] table.
        """

        table = Pyproject(pyproject).peeler_table

        if table:
            return

        path = self.pyproject_path.resolve()

        if table is None:
            msg = "The pyproject must contain a [tool.peeler] table."
        else:
            msg = "The pyproject [tool.peeler] table must not be empty."

        raise JsonSchemaValueException(message=f"{msg} (at {path})", name="tool.peeler")

    def validate(self) -> None:
        """Validate the file as generic pyproject file, and for peeler purposes.

        :raises ValidationError: on invalid pyproject file.
        """

        validator = _Validator(
            extra_plugins=[PluginWrapper("peeler", _peeler_plugin)],
            extra_validations=[self._validate_has_peeler_table],
        )

        validator(self.pyproject)
