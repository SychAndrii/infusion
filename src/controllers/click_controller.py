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
    def output_files(ctx, file_paths, version):
        if version:
            click.echo(__version__)
            ctx.exit()

        # Process each file path
        for file_path in file_paths:
            if not os.path.exists(file_path):
                click.echo(f"Error: Path '{file_path}' does not exist.", err=True)
                ctx.exit(1)

        for file_path in file_paths:
            try:
                # Attempt to read the file and check if it's a text file
                with open(file_path, "r", encoding="utf-8") as f:
                    contents = f.read()

                    # Apply color and style to the header
                    header = click.style(
                        f"*** Contents of {file_path} ***", fg="blue", bold=True
                    )
                    click.echo(f"{header}:\n{contents}")
            except UnicodeDecodeError:
                # This happens if the file is not a valid text file
                click.echo(f"Error: '{file_path}' is not a valid text file.", err=True)
            except Exception as e:
                # Handle other potential errors (e.g., permissions, IO issues)
                click.echo(f"Error: Could not read '{file_path}'. {str(e)}", err=True)
