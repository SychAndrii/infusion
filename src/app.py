import os
import getpass
from src.controllers import ClickController

controller = ClickController()

if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = getpass.getpass('Open AI API key:')
    controller.copy_files()
