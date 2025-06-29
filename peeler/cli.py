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
    help="Download wheels and update the Blender manifest.",
)
def wheels(
    path: Annotated[
        Path,
        Argument(
            help="Path to a file or directory containing uv.lock, pylock.*.toml, or pyproject.toml (defaults to current working directory).",
        ),
    ] = Path.cwd(),
    manifest: Annotated[
        Path,
        Argument(
            help="Path to a file or directory containing blender_manifest.toml (defaults to current working directory)."
        ),
    ] = Path.cwd(),
    wheels_dir: Annotated[
        Path | None,
        Argument(
            show_default=False,
            help="Directory where wheels will be downloaded (defaults to a sibling directory of the given manifest).",
        ),
    ] = None,
) -> None:
    """Download wheels and write their paths to the Blender manifest."""

    from .command.wheels import wheels_command

    wheels_command(path, manifest, wheels_dir)


if __name__ == "__main__":
    app()
