import click

class ClickLoggingService:
    def log_info(self, message):
        click.echo(click.style(message, fg="blue", bold=True))

    def log_error(self, message):
        click.echo(click.style(message, fg="red", bold=True), err=True)
