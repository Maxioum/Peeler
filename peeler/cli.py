import typer

app = typer.Typer()


@app.command(help=f"Display the current installed version.", hidden=True)
def version() -> None:
    """Call the version command."""

    from .command.version import version_command

    version_command()


# temp callback to force use version command as specified in:
# https://typer.tiangolo.com/tutorial/commands/one-or-multiple/#one-command-and-one-callback
@app.callback()
def callback() -> None:  # noqa: D103
    pass


if __name__ == "__main__":
    app()
