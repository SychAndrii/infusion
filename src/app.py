import asyncio
import click
from src.controllers import ClickController

controller = ClickController()


# Async wrapper for click command
async def run_command():
    await controller.infuse_files(
        standalone_mode=False
    )  # Use standalone_mode to handle errors cleanly.


if __name__ == "__main__":
    # Run the async click command with asyncio.run
    asyncio.run(run_command())
