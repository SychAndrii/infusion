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

        This method modifies the argument list to replace `-h` with `--help`, 
        ensuring that the user gets the help message when using `-h` instead 
        of `--help`.
        """

        if "-h" in args:
            args = ["--help" if arg == "-h" else arg for arg in args]
        return super().parse_args(ctx, args)

    def get_help_option(self, ctx):
        """
        Overrides the default help option behavior to add `-h` as an alias for `--help`.

        This method retrieves the help option from the base `click.Command` class,
        and then appends `-h` to the list of help flag options, making it a valid
        flag for displaying the help message.
        """
        # Override to add `-h` as an alias for `--help` in the help message
        help_option = super().get_help_option(ctx)
        help_option.opts.append("-h")  # Add `-h` to the help flag options
        return help_option
