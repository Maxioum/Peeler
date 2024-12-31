from importlib import metadata

import typer


def version_command() -> None:
    """Print the package name and version to the console."""

    import peeler

    version = metadata.version(peeler.__name__)
    typer.echo(f"{peeler.__name__} {version}")
