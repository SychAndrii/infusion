import os
import click
import getpass
from src import __version__
from .helpers import CustomCommand
from langchain_openai import ChatOpenAI
from src.models import InfusedSourceCode
from src.errors import NotSourceCodeError
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException


class ClickController:

    @click.command(cls=CustomCommand)
    @click.argument(
        "file_paths", nargs=-1, type=click.Path()
    )  # Accept multiple file paths
    @click.option("-v", "--version", is_flag=True, help="Show the version and exit.")
    @click.option(
        "-o",
        "--output",
        "output_dir",
        default="fusion_output",
        type=click.Path(),
        help="Specify an output folder. If not provided, the output folder will be `fusion_output` in current directory.",
    )
    @click.pass_context
    def infuse_files(ctx, file_paths, version, output_dir):
        if version:
            click.echo(__version__)
            ctx.exit()

        # Check if no files are provided
        if len(file_paths) == 0:
            click.echo(
                "Error: No files provided. Please specify at least one file.", err=True
            )
            ctx.exit(1)

        os.environ["OPENAI_API_KEY"] = getpass.getpass("Open AI API key:")

        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        model = ChatOpenAI(model="gpt-4")
        parser = JsonOutputParser(pydantic_object=InfusedSourceCode)

        prompt = PromptTemplate(
            template="""Your task is to add documentation to the provided code. Follow these rules:
            - If the code uses structured comment formats (like JSDoc for JavaScript/TypeScript or JavaDoc for Java), use that style.
            - If structured comments are not supported, add simple comments that describe parameters, return values, and any important details.
            - Add comments only above functions and classes, not within the function bodies.
            
            You'll also be provided with the file name and its extension. Use the file extension to identify the programming language (e.g., 'index.ts' means TypeScript).
            If you can't determine the programming language from the extension or the source code content return the word 'error'.

            {format_instructions}
            
            File name:
            {file_name}
            
            Code:
            {initial_code}
            """,
            input_variables=["initial_code", "file_name"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | model | parser

        for file_path in file_paths:
            try:
                # Attempt to read the file and check if it's a text file
                with open(file_path, "r", encoding="utf-8") as file:
                    source_code = file.read()

                    # Generate the documented code
                    infused_code = chain.invoke(
                        {
                            "initial_code": source_code,
                            "file_name": os.path.basename(file_path),
                        }
                    )

                    if (
                        infused_code["source_code_with_docs"] == "error"
                        or infused_code == "error"
                    ):
                        raise NotSourceCodeError()

                    # Get the base file name
                    base_name = os.path.basename(file_path)
                    # Create the destination file path in the output directory
                    dest_file_path = os.path.join(output_dir, f"{base_name}")

                    # Write the documented code to the new file
                    with open(dest_file_path, "w", encoding="utf-8") as dest_file:
                        dest_file.write(infused_code["source_code_with_docs"])

                    click.echo(
                        f"File '{file_path}' has been processed and saved as '{dest_file_path}'."
                    )

            except UnicodeDecodeError:
                click.echo(f"Error: '{file_path}' is not a text file.", err=True)
            except (NotSourceCodeError, OutputParserException):
                click.echo(
                    f"Error: '{file_path}' was not detected as a file that contains source code.",
                    err=True,
                )
            except Exception as e:
                # Handle other potential errors (e.g., permissions, IO issues)
                click.echo(f"Error: Could not read '{file_path}'. {str(e)}. Error type: {type(e).__name__}", err=True)
