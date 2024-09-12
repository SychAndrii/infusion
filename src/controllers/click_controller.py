import click
from src import __version__


class ClickController:

    @click.command()
    @click.option("-v", "--version", is_flag=True, help="Show the version and exit.")
    @click.pass_context
    def hello(ctx, version):
        if version:
            click.echo(__version__)
            ctx.exit()
