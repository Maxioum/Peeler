from pathlib import Path
from typing import Annotated, Optional

from typer import Typer, Argument

app = Typer()


@app.command(help=f"Display the current installed version.", hidden=True)
def version() -> None:
    """Call the version command."""

    from .command.version import version_command

    version_command()


@app.command(
    help=f"Create or update a blender_manifest.toml file from a pyproject.toml file.",
)
def manifest(
    pyproject: Annotated[Path, Argument()],
    blender_manifest: Annotated[Path, Argument(default_factory=Path.cwd)],
) -> None:
    """Call a command to create or update a blender_manifest.toml from a pyproject.toml.

    :param pyproject: the path to the `pyproject.toml` file or directory
    :param blender_manifest: optional path to the `blender_manifest.toml` file to be updated or created
    """

    from .command.manifest import manifest_command

    manifest_command(pyproject, blender_manifest)


if __name__ == "__main__":
    app()
