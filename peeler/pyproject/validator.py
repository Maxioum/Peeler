# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Any, Dict

from click import format_filename
from fastjsonschema import JsonSchemaValueException
from packaging.specifiers import SpecifierSet
from tomlkit import TOMLDocument
from validate_pyproject.api import Validator as _Validator
from validate_pyproject.plugins import PluginWrapper

from ..schema import peeler_json_schema
from .utils import Pyproject

_BLENDER_SUPPORTED_PYTHON_VERSION = {"3.11"}

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

    def _validate_has_peeler_table(self, pyproject: TOMLDocument) -> TOMLDocument:
        """Raise an error if the peeler table is missing or empty.

        :param pyproject: the pyproject document
        :raises JsonSchemaValueException: on missing or empty [tool.peeler] table.
        :return: the pyproject document
        """

        table = Pyproject(pyproject).peeler_table

        if table:
            return pyproject

        path = self.pyproject_path.resolve()

        if table is None:
            msg = "The pyproject must contain a [tool.peeler] table."
        else:
            msg = "The pyproject [tool.peeler] table must not be empty."

        raise JsonSchemaValueException(message=f"{msg} (at {path})", name="tool.peeler")
    
        

    def _validate_python_version(self, pyproject: TOMLDocument) -> TOMLDocument:
        """Raise an error the python versions in project requires-python don't contains a supported python version by Blender.

        If requires-python is not specified, do nothing.

        :param pyproject: the pyproject document
        :raises JsonSchemaValueException: on invalid python versions.
        :return: the pyproject document
        """
        table = Pyproject(pyproject).project_table

        if (python_versions := table.get("requires-python", None)) is None:
            return pyproject

        s = SpecifierSet(python_versions)
        
        if not any(s.contains(py_version) for py_version in _BLENDER_SUPPORTED_PYTHON_VERSION):
            msg = f"The python versions {s} specified in your pyproject 'project.requires-python' are not supported by Blender"
            raise JsonSchemaValueException(message=f"{msg} (at {format_filename(self.pyproject_path.resolve())})", name="project.requires-python")

        return pyproject
    
    def validate(self) -> None:
        """Validate the file as generic pyproject file, and for peeler purposes.

        :raises ValidationError: on invalid pyproject file.
        """

        validator = _Validator(
            extra_plugins=[PluginWrapper("peeler", _peeler_plugin)],
            extra_validations=[
                self._validate_has_peeler_table,
                self._validate_python_version,
                ],
        )

        validator(self.pyproject)
