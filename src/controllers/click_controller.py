import os
import click
from src import __version__
from .helpers import CustomCommand

class ClickController:

    @click.command(cls=CustomCommand)
    @click.argument(
        "file_paths", nargs=-1, type=click.Path()
    )  # Accept multiple file paths
    @click.option("-v", "--version", is_flag=True, help="Show the version and exit.")
    @click.pass_context
    def hello(ctx, file_paths, version):
        if version:
            click.echo(__version__)
            ctx.exit()

        # Process each file path
        for file_path in file_paths:
            if not os.path.exists(file_path):
                click.echo(f"Error: Path '{file_path}' does not exist.", err=True)
                ctx.exit(1)
                
        for file_path in file_paths:
            click.echo(f"Processing file: {file_path}")
