import os
import click
import getpass
from src import __version__
from .helpers import CustomCommand
from langchain_openai import ChatOpenAI
from src.models import InfusedSourceCode
from src.errors import NotSourceCodeError
from src.services.logging import logging_service
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.runnables import RunnableLambda, RunnablePassthrough


def output_token_usage(response):
    click.echo(
        click.style(
            f"Prompt Tokens: {response.response_metadata['token_usage']['prompt_tokens']}",
            fg="red",
            bold=True,
        ),
        err=True,
    )
    click.echo(
        click.style(
            f"Completion Tokens: {response.response_metadata['token_usage']['completion_tokens']}",
            fg="red",
            bold=True,
        ),
        err=True,
    )
    return response


class ClickController:
    """
    The `ClickController` class manages the command-line interface (CLI) commands using
    Click library.
    """

    @click.command(cls=CustomCommand)
    @click.argument(
        "file_paths", nargs=-1, type=click.Path()
    )  # Accept multiple file paths
    @click.option("-v", "--version", is_flag=True, help="Show the version.")
    @click.option(
        "-o",
        "--output",
        "output_dir",
        default="fusion_output",
        type=click.Path(),
        help="Specify an output folder. If not provided, the output folder will be `fusion_output` in the current directory. Relative path will be relative to the directory from which you are calling this tool. Absolute path is also supported.",
    )
    @click.option(
        "-u",
        "--token-usage",
        is_flag=True,
        help="Show the number of tokens that were sent in the prompt and returned in the response.",
    )
    @click.pass_context
    def infuse_files(ctx, file_paths, version, output_dir, token_usage):
        """
        Infusion is a command-line tool designed to help you generate documentation for your source code using advanced language models.
        You provide file paths in your current directory, LLM modifies them to include documentation, and inserts them into the output folder.

        You provide multiple FILE_PATHS by separating them with spaces. Relative paths will be relative to the directory from which you are calling this tool.
        Absolute paths are also supported.
        """
        if version:
            ClickController.__print_version(ctx)

        # Check if no files are provided
        if len(file_paths) == 0:
            ClickController.__handle_zero_files(ctx)

        ClickController.__ensure_environment_is_set()
        ClickController.__ensure_output_folder_exists(output_dir)

        chain = ClickController.__get_infuse_files_chain(token_usage)

        for file_path in file_paths:
            try:
                logging_service.log_info(f"Processing {file_path}")
                
                infused_code = ClickController.__process_file_with_chain(file_path, chain)
                dest_file_path = ClickController.__get_output_file_path(file_path, output_dir)
                ClickController.__save_contents_into_file(infused_code, dest_file_path)
                
                logging_service.log_info(
                    f"File '{file_path}' has been processed and saved as '{dest_file_path}'."
                )
            except UnicodeDecodeError:
                logging_service.log_error(f"Error: '{file_path}' is not a text file.")
            except (NotSourceCodeError, OutputParserException):
                logging_service.log_error(
                    f"Error: '{file_path}' was not detected as a file that contains source code."
                )
            except Exception as e:
                # Handle other potential errors (e.g., permissions, IO issues)
                logging_service.log_error(
                    f"Error: Could not read '{file_path}'. {str(e)}. Error type: {type(e).__name__}"
                )

        logging_service.log_info("Processing ended")

    @staticmethod
    def __process_file_with_chain(file_path, chain):
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

            if infused_code["error"] or infused_code["source_code_with_docs"] == "":
                raise NotSourceCodeError()

            return infused_code["source_code_with_docs"]

    @staticmethod
    def __get_output_file_path(initial_file_path, output_folder):
        # Get the base file name
        base_name = os.path.basename(initial_file_path)
        # Create the destination file path in the output directory
        dest_file_path = os.path.join(output_folder, f"{base_name}")
        return dest_file_path

    @staticmethod
    def __save_contents_into_file(contents, output_path):
        # Write the documented code to the new file
        with open(output_path, "w", encoding="utf-8") as dest_file:
            dest_file.write(contents)

    @staticmethod
    def __ensure_output_folder_exists(output_dir):
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    @staticmethod
    def __ensure_environment_is_set():
        # Check if OPENAI_API_KEY is defined in the environment, if not, ask for it
        if "OPENAI_API_KEY" not in os.environ:
            os.environ["OPENAI_API_KEY"] = getpass.getpass("Open AI API key:")
        else:
            logging_service.log_info("Using API key from the environment")

    @staticmethod
    def __print_version(ctx):
        click.echo(__version__)
        ctx.exit()

    @staticmethod
    def __handle_zero_files(ctx):
        logging_service.log_error(
            "Error: No files provided. Please specify at least one file."
        )
        ctx.exit(1)

    @staticmethod
    def __get_infuse_files_chain(token_usage):
        model = ChatOpenAI(model="gpt-4")
        parser = JsonOutputParser(pydantic_object=InfusedSourceCode)

        prompt = PromptTemplate(
            template="""Your task is to add documentation to the provided code. Follow these rules:
            - If the code uses structured comment formats (like JSDoc for JavaScript/TypeScript or JavaDoc for Java), use that style.
            - If structured comments are not supported, add simple comments that describe parameters, return values, and any important details.
            - Add comments only above functions and classes, not within the function bodies.

            You'll also be provided with the file name and its extension. Use the file extension to identify the programming language (e.g., 'index.ts' means TypeScript).

            {format_instructions}

            File name:
            {file_name}

            Code:
            {initial_code}
            """,
            input_variables=["initial_code", "file_name"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = (
            prompt
            | model
            | (
                RunnableLambda(output_token_usage)
                if token_usage
                else RunnablePassthrough()
            )
            | parser
        )
        return chain
