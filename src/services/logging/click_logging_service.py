import click


class ClickLoggingService:
    """
    The `ClickLoggingService` class provides logging functionality for command-line applications using the Click library.
    It allows logging informational, error, and debug messages with styled output.
    """

    def log_info(self, message):
        """
        Logs an informational message to the console with blue text. This message is printed to stdout.

        Args:
            message (str): The informational message to log.

        Returns:
            None
        """
        click.echo(click.style(message, fg="blue", bold=True))

    def log_error(self, message):
        """
        Logs an error message to the console with red text. This message is printed to stderr.

        Args:
            message (str): The error message to log.

        Returns:
            None
        """
        click.echo(click.style(message, fg="red", bold=True), err=True)

    def log_debug(self, message):
        """
        Logs a debug message to the console with red text, similar to error messages. This message is printed to stderr.

        Args:
            message (str): The debug message to log.

        Returns:
            None
        """
        click.echo(click.style(message, fg="orange", bold=True), err=True)
