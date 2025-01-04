from crewai.tools import BaseTool
from langchain_community.tools import ShellTool
from pydantic import Field

shell_tool = ShellTool()

import logging

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def custom_error_handler(exception):
    error_message = f"An error occurred during shell execution: {str(exception)}"
    logger.error(error_message)
    return error_message

class ShellCommandTool(BaseTool):
    name: str = "Shell Command Executor"
    description: str = "Executes shell commands and returns the output."
    shell_tool: ShellTool = Field(default_factory=ShellTool)
    # def __init__(self):
    #     self.shell_tool = ShellTool()

    def _run(self, command: str) -> str:
        """Execute the shell command and return the output."""
        try:
            return self.shell_tool.run({"commands": [command]}, verbose=True)
        except Exception as e:
            return f"Error executing command: {str(e)}"