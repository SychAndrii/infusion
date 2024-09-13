import click


class CustomCommand(click.Command):
    """
    A custom command class that extends `click.Command` to modify the behavior of
    the `--help` option in Click commands.

    This class introduces the following changes:
    - The `-h` flag is treated as an alias for `--help`.
    - Updates the help message to reflect this alias (`-h`).
    """

    def parse_args(self, ctx, args):
        """
        Parses the command-line arguments and ensures that the `-h` flag is
        interpreted as `--help`.
        """
        if "-h" in args:
            args = ["--help" if arg == "-h" else arg for arg in args]
        return super().parse_args(ctx, args)

    def get_help_option(self, ctx):
        """
        Overrides the default help option behavior to customize the text
        displayed for the `-h` and `--help` options.
        """
        help_option = super().get_help_option(ctx)
        if help_option:
            # Override the help text for the `-h` and `--help` options
            help_option.help = "Show the help message."
        return help_option
