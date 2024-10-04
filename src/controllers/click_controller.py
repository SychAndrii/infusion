import os
import sys
import click
import getpass
from src import __version__
from .helpers import CustomCommand
from langchain_openai import ChatOpenAI
from src.models import InfusedSourceCode
from src.errors import NotSourceCodeError, InvalidModelError, OutputDirWithStreamingError
from src.services.logging import logging_service
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

class ClickController:
    """
    The `ClickController` class manages the command-line interface (CLI) commands using the Click library.
    It handles the infusion of source code files by adding documentation using a language model.
    """
        
    CONFIG_PATH = os.path.expanduser("~/.infuse-config.toml")

    @click.command(cls=CustomCommand)
    @click.argument("file_paths", nargs=-1, type=click.Path())
    @click.option(
        "-v",
        "--version",
        is_flag=True,
        help="Show the version.",
    )
    @click.option(
        "-s",
        "--stream",
        is_flag=True,
        help="See how LLM generated documentation for your file in real time. You cannot provide streaming and output_dir at the same time.",
    )
    @click.option(
        "-m",
        "--model",
        type=click.STRING,
        default="gpt-4o",
        help="Select the Open AI model to use when generating documentation. Possible values: gpt-4o, gpt-4o-mini, cohere. Default value: gpt-4o",
    )
    @click.option(
        "-o",
        "--output",
        "output_dir",
        type=click.Path(),
        help="Specify an output folder for files with generated documentation. If not provided, the output will be shown in stdout, and won't be saved to any file. You cannot provide streaming and output_dir at the same time.",
    )
    @click.option(
        "-u",
        "--token-usage",
        is_flag=True,
        help="Show the number of tokens used in the prompt and response.",
    )
    @click.pass_context
    async def infuse_files(ctx, file_paths, version, output_dir, token_usage, model, stream):
        """
        Infusion is a command-line tool designed to help you generate documentation for your source code using advanced language models.
        You provide file paths in your current directory, LLM modifies them to include documentation, and inserts them into the output folder.

        You provide multiple FILE_PATHS by separating them with spaces. Relative paths will be relative to the directory, from which you are calling this tool.
        Absolute paths are also supported.
        """

        config = ClickController.__load_config()
        model = model or config.get("model", "gpt-4o")
        output_dir = output_dir or config.get("output")
        stream = stream or config.get("stream")

        try:
            await ClickController.__execute(
                file_paths, version, output_dir, token_usage, model, stream
            )
        except Exception as e:
            logging_service.log_error(
                f"Error: {str(e)}. Error type: {type(e).__name__}"
            )
            sys.exit(3)

    @staticmethod
    def __load_config():
        """
        Loads configuration from a TOML file in the user's home directory.
        If the file is missing or can't be parsed, it handles the error appropriately.

        Returns:
            dict: The configuration dictionary, or an empty dict if no valid config is found.
        """
        if os.path.exists(ClickController.CONFIG_PATH):
            try:
                with open(ClickController.CONFIG_PATH, 'rb') as file:
                    return tomllib.load(file)
            except tomllib.TOMLDecodeError:
                logging_service.log_error(f"Error: Unable to parse the config file at {ClickController.CONFIG_PATH}. Exiting.")
                sys.exit(1)
        return {}

    @staticmethod
    async def __execute(file_paths, version, output_dir, token_usage, model, streaming):
        if version:
            ClickController.__print_version()

        try:
            ClickController.__validate(file_paths, output_dir, model, streaming)
        except FileNotFoundError as e:
            logging_service.log_error(str(e))
            sys.exit(1)
        except InvalidModelError:
            logging_service.log_error(
                "Error: Provided model is not supported. Supported models: gpt-4o, gpt-4o-mini."
            )
            sys.exit(1)
        except OutputDirWithStreamingError:
            logging_service.log_error(
                "Error: You cannot provide streaming and output_dir at the same time."
            )
            sys.exit(1)

        for file_path in file_paths:
            if streaming:
                chain = ClickController.__get_streaming_infuse_files_chain(model)
                with open(file_path, "r", encoding="utf-8") as file:
                    source_code = file.read()

                    buffer = ""

                    async for text in chain.astream(
                        {
                            "initial_code": source_code,
                            "file_name": os.path.basename(file_path),
                        }
                    ):
                        new_content = text[len(buffer):]

                        if new_content.strip():
                            logging_service.log_info(
                                new_content,
                                nl=False
                            )
                            buffer += new_content
            else:
                chain = ClickController.__get_infuse_files_chain(token_usage, model)
                ClickController.__process_file_path(file_path, chain, output_dir)

    @staticmethod
    def __check_files_exist(file_paths):
        """
        Checks if all specified files exist.

        Args:
            file_paths (list): A list of file paths to check.

        Raises:
            FileNotFoundError: If any of the specified files do not exist.
        """
        missing_files = [file_path for file_path in file_paths if not os.path.isfile(file_path)]
        if missing_files:
            missing_files_str = ', '.join(missing_files)
            raise FileNotFoundError(f"The following files do not exist: {missing_files_str}")

    @staticmethod
    def __process_file_path(file_path, chain, output_dir):
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
            sys.exit(2)
        except (NotSourceCodeError, OutputParserException):
            logging_service.log_error(
                f"Error: '{file_path}' was not detected as a file that contains valid source code."
            )
            sys.exit(2)

    @staticmethod 
    def __validate(file_paths, output_dir, model, streaming):
        # Check if no files are provided
        if len(file_paths) == 0:
            ClickController.__handle_zero_files()

        if output_dir and streaming:
            raise OutputDirWithStreamingError()

        ClickController.__ensure_model_is_valid(model)
        ClickController.__check_files_exist(file_paths)
        ClickController.__ensure_environment_is_set(model)

        if output_dir:
            ClickController.__ensure_output_folder_exists(output_dir)

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
    def __ensure_model_is_valid(model):
        """
        Checks if provided model is supported by the CLI tool.

        Returns:
            None
        """
        if model not in ["gpt-4o", "gpt-4o-mini", "cohere"]:
            raise InvalidModelError()

    @staticmethod
    def __ensure_environment_is_set(model):
        """
        Checks if the required environment variables are set and prompts the user if they are missing.

        Returns:
            None
        """

        config = ClickController.__load_config()

        if "openai_api_key" in config:
            os.environ["OPENAI_API_KEY"] = config.get("openai_api_key")
        elif "cohere_api_key" in config:
            os.environ["COHERE_API_KEY"] = config.get("cohere_api_key")
 
        if model != "cohere":
            if "OPENAI_API_KEY" not in os.environ and "openai_api_key" not in config:
                os.environ["OPENAI_API_KEY"] = getpass.getpass("Open AI API key:")
            else:
                logging_service.log_info("Using Open AI API key from the environment")
        else:
            if "COHERE_API_KEY" not in os.environ and "cohere_api_key" not in config:
                os.environ["COHERE_API_KEY"] = getpass.getpass("Open Cohere API key:")
            else:
                logging_service.log_info("Using Cohere API key from the environment")

    @staticmethod
    def __print_version():
        """
        Prints the version of the tool and exits the program.

        Args:
            ctx (Context): Click context object.

        Returns:
            None
        """
        click.echo(__version__)
        sys.exit()

    @staticmethod
    def __handle_zero_files():
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
        sys.exit(1)

    @staticmethod
    async def __extract_infused_code_streaming(input_stream):
        """An async generator that operates on input streams."""
        async for input in input_stream:
            if not isinstance(input, dict):
                continue
            if "error" in input:
                error = input["error"]
                if error:
                    raise Exception('Error occurred during streaming.')
            if "source_code_with_docs" in input:
                source_code = input["source_code_with_docs"]
                yield source_code

    @staticmethod
    def __get_streaming_infuse_files_chain(model):
        model = ChatOpenAI(model=model, streaming=True)
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
            prompt | model | parser | ClickController.__extract_infused_code_streaming
        )
        return chain

    @staticmethod
    def __get_infuse_files_chain(token_usage, model):
        """
        Creates and configures the chain for processing files with documentation infusion.

        Args:
            token_usage (bool): If True, the token usage statistics will be displayed.

        Returns:
            Runnable: The configured chain for file processing.
        """

        model = ChatOpenAI(model=model)
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
