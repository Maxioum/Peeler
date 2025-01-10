from tomlkit import TOMLDocument
from tomlkit.items import Table


class Pyproject:
    """A class to fetch values from a `pyproject.toml` with a peeler tool table.

    :param document: The TOML document representing the `pyproject.toml` file.
    """

    def __init__(self, document: TOMLDocument) -> None:
        self._document = document

    @property
    def project_table(self) -> Table:
        """Retrieve the `[project]` table from the `pyproject.toml`.

        :return: The `[project]` table.
        """
        if not hasattr(self, "_project_table"):
            self._project_table = self._document.get("project")
        return self._project_table

    @property
    def peeler_table(self) -> Table:
        """Retrieve the `[tool.peeler]` table from the `pyproject.toml`.

        :return: The `[tool.peeler]` table.
        """
        if not hasattr(self, "_peeler_table"):
            self._peeler_table = self._document.get("tool", {}).get("peeler")
        return self._peeler_table

    @property
    def settings_table(self) -> Table:
        """Retrieve the `settings` table from the `[tool.peeler]` section, excluding `manifest`.

        :return: The `settings` table.
        """
        if not hasattr(self, "_settings_table"):
            _ = self.manifest_table
            self._settings_table = self.peeler_table.remove("manifest")
        return self._settings_table

    @property
    def manifest_table(self) -> Table:
        """Retrieve the `manifest` table from the `[tool.peeler]` section.

        :return: The `manifest` table.
        """
        if not hasattr(self, "_manifest_table"):
            self._manifest_table = self.peeler_table.get("manifest")
        return self._manifest_table
