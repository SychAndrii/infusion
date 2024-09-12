import click

class CustomCommand(click.Command):
    def parse_args(self, ctx, args):
        if "-h" in args:
            args = ["--help" if arg == "-h" else arg for arg in args]
        return super().parse_args(ctx, args)

    def get_help_option(self, ctx):
        # Override to add `-h` as an alias for `--help` in the help message
        help_option = super().get_help_option(ctx)
        help_option.opts.append("-h")  # Add `-h` to the help flag options
        return help_option
