from __future__ import annotations

from functools import partial
from typing import Dict, Any, Set
from collections.abc import Callable

from tomlkit import TOMLDocument

from .utils import Pyproject


class Parser:
    """A tool to parse a TOML Document representing a pyproject into a TOML Document representing a blender manifest.

    :param pyproject: the pyproject to extract values from.
    :param blender_manifest_jsonschema: the blender manifest json schema, specifying required fields etc.
    :param peeler_jsonschema: the peeler json schema, specifying required fields in the `[tool.peeler.manifest]` pyproject table.
    """

    def __init__(
        self,
        pyproject: TOMLDocument,
        blender_manifest_jsonschema: Dict[str, Any],
        peeler_jsonschema: Dict[str, Any],
    ) -> None:
        self.pyproject = Pyproject(pyproject)
        self.blender_manifest_jsonschema = blender_manifest_jsonschema
        self.peeler_jsonschema = peeler_jsonschema

    @property
    def _blender_manifest_required_fields(self) -> Dict[str, Any]:
        """Fields required by the blender manifest specifications.

        :return: A dictionary mapping properties names to their json schema
        """
        blender_manifest_required_fields_names = self.blender_manifest_jsonschema[
            "required"
        ]
        return {
            field: self.blender_manifest_jsonschema["properties"][field]
            for field in blender_manifest_required_fields_names
        }

    @property
    def _fields_to_fill(self) -> Set[str]:
        """Required fields in the blender manifest, and not in the peeler pyproject table.

        These fields will be inferred by peeler if possible.
        (For 1.0.0) example: "name", "schema_version" etc
        :return: The field names
        """
        return set(self._blender_manifest_required_fields.keys()) - set(
            self.pyproject.manifest_table.keys()
        )

    @property
    def _strictly_required_fields(self) -> Set[str]:
        """Required fields in the blender manifest, that cannot be inferred by peeler.

        These fields will be inferred by peeler if possible.
        (For 1.0.0) example: "id", "maintainer"
        :return: The field names
        """

        peeler_manifest_required_field: Set[str] = set(
            self.peeler_jsonschema["properties"]["manifest"]["required"]
        )

        return peeler_manifest_required_field & self._fields_to_fill

    def _get_default_value(self, property_name: str) -> Any | None:
        """Get the default value of the property as specified in the blender manifest jsonschema.

        :param property_name: the name of the properties as specified
        :raises RuntimeError: if no default value
        :return: the default value
        """
        properties: Dict[str, Dict[str, Any]] = self.blender_manifest_jsonschema[
            "properties"
        ]

        property_: Dict[str, Any] = properties[property_name]
        default_value = property_.get("default", None)

        if default_value is None:
            raise RuntimeError(
                f"The property: {property_name} has no default value provided in the json_schema"
            )

        return default_value

    @property
    def _infer_callables(self) -> Dict[str, Callable[[], Any]]:
        return {
            "name": lambda: self.pyproject.project_table.get("name"),
            "version": lambda: self.pyproject.project_table.get("version"),
        }

    def _infer_fields(self) -> Dict[str, Any]:
        return {
            field: self._infer_callables.get(
                field, partial(self._get_default_value, field)
            )()
            for field in self._fields_to_fill
        }

    def to_blender_manifest(self) -> TOMLDocument:
        """Generate a blender manifest TOML document.

        :raises ValueError: if required values cannot be inferred from the pyproject.
        :return: A blender manifest TOML document.
        """

        # raise an error if some fields are missing
        # and cannot be filled automatically
        if self._strictly_required_fields:
            header = "Missing field in [peeler.manifest] table:"
            missing_properties = {
                f'{field}:\n\t{self.blender_manifest_jsonschema["properties"]["description"]}'
                for field in self._strictly_required_fields
            }
            msg = header + r"\n".join(missing_properties)
            raise ValueError(msg)

        document = TOMLDocument()

        # update the doc with fields inferred by peeler
        document.update(self._infer_fields())

        # update the doc with fields given in the pyproject manifest peeler table
        document.update(self.pyproject.manifest_table)

        return document
