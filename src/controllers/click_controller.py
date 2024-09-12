import os
import click
import shutil
from src import __version__
from .helpers import CustomCommand
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

class ClickController:

    @click.command(cls=CustomCommand)
    @click.argument(
        "file_paths", nargs=-1, type=click.Path()
    )  # Accept multiple file paths
    @click.option("-v", "--version", is_flag=True, help="Show the version and exit.")
    @click.pass_context
    def copy_files(ctx, file_paths, version):
        if version:
            click.echo(__version__)
            ctx.exit()

        # Process each file path
        for file_path in file_paths:
            if not os.path.exists(file_path):
                click.echo(f"Error: Path '{file_path}' does not exist.", err=True)
                ctx.exit(1)

        output_dir = "fusion_output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        model = ChatOpenAI(model="gpt-4")
        messages = [
            SystemMessage(content="Translate the following from English into Italian"),
            HumanMessage(content="hi!"),
        ]
        result = model.invoke(messages)

        parser = StrOutputParser()
        translation = parser.invoke(result)
        print('TRANSLATION:', translation)

        for file_path in file_paths:
            try:
                # Attempt to read the file and check if it's a text file
                with open(file_path, "r", encoding="utf-8"):
                    base_name = os.path.basename(file_path)
                    dest_file_path = os.path.join(output_dir, f"{base_name}")
            except UnicodeDecodeError:
                # This happens if the file is not a valid text file
                click.echo(f"Error: '{file_path}' is not a valid text file.", err=True)
            except Exception as e:
                # Handle other potential errors (e.g., permissions, IO issues)
                click.echo(f"Error: Could not read '{file_path}'. {str(e)}", err=True)
