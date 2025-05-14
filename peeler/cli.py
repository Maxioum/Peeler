# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

from clypi import Command, Positional, arg


class Version(Command):
    """Display the current installed version."""

    async def run(self) -> None:
        """Call the version command."""

        from .command.version import version_command

        version_command()


class Manifest(Command):
    """Create or update a blender_manifest.toml file from a pyproject.toml file."""

    pyproject: Positional[Path] = arg(
        help="the path to the `pyproject.toml` file or directory"
    )
    blender_manifest: Positional[Path] = arg(
        default_factory=Path.cwd,
        help="optional path to the `blender_manifest.toml` file to be updated or created",
    )

    async def run(self) -> None:
        """Call a command to create or update a blender_manifest.toml from a pyproject.toml."""
        from .command.manifest import manifest_command

        manifest_command(self.pyproject, self.blender_manifest)


class Wheels(Command):
    """Call a command to download wheels."""

    pyproject: Positional[Path] = arg(help="The pyproject file")
    blender_manifest: Positional[Path] = arg(help="the blender manifest file")
    wheels_directory: Positional[Path] = arg(
        default=None, help="the directory to download wheels into."
    )

    async def run(self) -> None:
        """Call the command to download wheels and write paths to the blender manifest."""

        from .command.wheels import wheels_command

        await wheels_command(
            self.pyproject, self.blender_manifest, self.wheels_directory
        )


class Peeler(Command):
    """A verry simple cli."""

    subcommand: Version | Manifest | Wheels


def main() -> None:
    """Peeler app Entry point."""
    cmd = Peeler.parse()
    cmd.start()


if __name__ == "__main__":
    main()
