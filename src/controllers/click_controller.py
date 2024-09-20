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


class ClickController:
    """
    The `ClickController` class manages the command-line interface (CLI) commands using the Click library.
    It handles the infusion of source code files by adding documentation using a language model.
    """

    @click.command(cls=CustomCommand)
    @click.argument("file_paths", nargs=-1, type=click.Path())
    @click.option("-v", "--version", is_flag=True, help="Show the version.")
    @click.option(
        "-o",
        "--output",
        "output_dir",
        type=click.Path(),
        help="Specify an output folder. If not provided, the output folder will be `fusion_output` in the current directory.",
    )
    @click.option(
        "-u",
        "--token-usage",
        is_flag=True,
        help="Show the number of tokens used in the prompt and response.",
    )
    @click.pass_context
    def infuse_files(ctx, file_paths, version, output_dir, token_usage):
        """
        Infusion is a command-line tool designed to help you generate documentation for your source code using advanced language models.
        You provide file paths in your current directory, LLM modifies them to include documentation, and inserts them into the output folder.

        You provide multiple FILE_PATHS by separating them with spaces. Relative paths will be relative to the directory, from which you are calling this tool.
        Absolute paths are also supported.
        """

        if version:
            ClickController.__print_version(ctx)

        # Check if no files are provided
        if len(file_paths) == 0:
            ClickController.__handle_zero_files(ctx)

        ClickController.__ensure_environment_is_set()

        if output_dir:
            ClickController.__ensure_output_folder_exists(output_dir)

        chain = ClickController.__get_infuse_files_chain(token_usage)

        for file_path in file_paths:
            try:
                logging_service.log_info(f"Processing {file_path}")

                infused_code = ClickController.__process_file_with_chain(
                    file_path, chain
                )

                if output_dir:
                    dest_file_path = ClickController.__get_output_file_path(
                        file_path, output_dir
                    )
                    ClickController.__save_contents_into_file(infused_code, dest_file_path)
                    logging_service.log_info(
                        f"File '{file_path}' has been processed and saved as '{dest_file_path}'."
                    )
                else:
                    logging_service.log_info("Processing ended")
                    logging_service.log_info(f"\n{file_path}:\n", color="white")
                    logging_service.log_info(f"{infused_code}\n\n")
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

    @staticmethod
    def __print_token_usage(llm_response):
        """
        Logs the token usage details from the language model response.

        Args:
            llm_response: The response object containing token usage metadata.

        Returns:
            The original response object.
        """
        logging_service.log_debug(
            f"Prompt Tokens: {llm_response.response_metadata['token_usage']['prompt_tokens']}"
        )
        logging_service.log_debug(
            f"Completion Tokens: {llm_response.response_metadata['token_usage']['completion_tokens']}"
        )
        return llm_response

    @staticmethod
    def __process_file_with_chain(file_path, chain):
        """
        Processes a single file by adding documentation using a specified processing chain.

        Args:
            file_path (str): The path to the file to process.
            chain: The chain of commands to process the file.

        Returns:
            str: The source code with added documentation.

        Raises:
            NotSourceCodeError: If the file is not detected as source code.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            source_code = file.read()

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
        """
        Generates the output file path within the specified output directory.

        Args:
            initial_file_path (str): The original file path.
            output_folder (str): The directory where the infused file will be saved.

        Returns:
            str: The full path to the output file.
        """
        base_name = os.path.basename(initial_file_path)
        dest_file_path = os.path.join(output_folder, f"{base_name}")
        return dest_file_path

    @staticmethod
    def __save_contents_into_file(contents, output_path):
        """
        Saves the provided contents into a file at the specified path.

        Args:
            contents (str): The content to write into the file.
            output_path (str): The path to save the file.

        Returns:
            None
        """
        with open(output_path, "w", encoding="utf-8") as dest_file:
            dest_file.write(contents)

    @staticmethod
    def __ensure_output_folder_exists(output_dir):
        """
        Ensures that the output directory exists, creating it if necessary.

        Args:
            output_dir (str): The directory to check or create.

        Returns:
            None
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    @staticmethod
    def __ensure_environment_is_set():
        """
        Checks if the required environment variables are set and prompts the user if they are missing.

        Returns:
            None
        """
        if "OPENAI_API_KEY" not in os.environ:
            os.environ["OPENAI_API_KEY"] = getpass.getpass("Open AI API key:")
        else:
            logging_service.log_info("Using API key from the environment")

    @staticmethod
    def __print_version(ctx):
        """
        Prints the version of the tool and exits the program.

        Args:
            ctx (Context): Click context object.

        Returns:
            None
        """
        click.echo(__version__)
        ctx.exit()

    @staticmethod
    def __handle_zero_files(ctx):
        """
        Handles the scenario where no files are provided to the command.

        Args:
            ctx (Context): Click context object.

        Returns:
            None
        """
        logging_service.log_error(
            "Error: No files provided. Please specify at least one file."
        )
        ctx.exit(1)

    @staticmethod
    def __get_infuse_files_chain(token_usage):
        """
        Creates and configures the chain for processing files with documentation infusion.

        Args:
            token_usage (bool): If True, the token usage statistics will be displayed.

        Returns:
            Runnable: The configured chain for file processing.
        """
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
                RunnableLambda(ClickController.__print_token_usage)
                if token_usage
                else RunnablePassthrough()
            )
            | parser
        )
        return chain
