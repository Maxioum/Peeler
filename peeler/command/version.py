# # SPDX-FileCopyrightText: 2025 Maxime Letellier <maxime.eliot.letellier@gmail.com>
#
# # SPDX-License-Identifier: GPL-3.0-or-later

from importlib import metadata

import typer


def version_command() -> None:
    """Print the package name and version to the console."""

    import peeler

    version = metadata.version(peeler.__name__)
    typer.echo(f"{peeler.__name__} {version}")
