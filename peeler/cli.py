# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Annotated

from typer import Argument, Typer

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


@app.command(
    help=f"Call a command to download wheels.",
)
def wheels(
    pyproject: Annotated[Path, Argument()],
    blender_manifest: Annotated[Path, Argument()],
    wheels_directory: Annotated[Path | None, Argument()] = None,
) -> None:
    """Call the command to download wheels and write paths to the blender manifest.

    :param pyproject_file: The pyproject file.
    :param blender_manifest_file: the blender manifest file
    :param wheels_directory: the directory to download wheels into.
    """

    from .command.wheels import wheels_command

    wheels_command(pyproject, blender_manifest, wheels_directory)


if __name__ == "__main__":
    app()
