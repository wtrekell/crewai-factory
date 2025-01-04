import json
import time

from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from langchain_community.agent_toolkits.playwright.toolkit import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_sync_playwright_browser, create_async_playwright_browser
from pydantic import Field
import logging

# additional requirements: pip install lxml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def custom_error_handler(exception):
    error_message = f"An error occurred during browser interaction: {str(exception)}"
    logger.error(error_message)
    return error_message


class PlaywrightTool(BaseTool):
    name: str = "Web Browser Playwright"
    # description: str = "A Web Browser allowing dynamic interaction with web pages, including navigation, text extraction, and browser interactions."
    description: str = (
        f"A Web Browser allowing dynamic interaction with web pages, including navigation, text extraction, and browser interactions."
        f"Supported actions: click_element, navigate_browser, previous_webpage, extract_text, extract_hyperlinks, get_elements, current_webpage. "
        f"Note: Before using any action, the browser must first navigate to a page "
        f"using the 'navigate_browser' action. "
        f"Expected tool input format: {{'tool_input': {{'action': 'navigate_browser', 'parameters': {{'url': 'https://example.com'}}}}}}.")
    toolkit: PlayWrightBrowserToolkit = Field(default=None)
    sync_browser: object = Field(default=None)

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            # Set up an asynchronous browser
            # async_browser = create_sync_playwright_browser(headless=True)
            sync_browser = create_sync_playwright_browser(headless=True)
            self.toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
            # self.async_browser = async_browser
            self.sync_browser = sync_browser

            # Dynamically set the description
            supported_actions = ", ".join([tool.name for tool in self.toolkit.get_tools()])
            # self.description = (
            #     f"Allows dynamic interaction with web pages. "
            #     f"Supported actions: {supported_actions} "
            #     f"Note: Before using any action, the browser must first navigate to a page "
            #     f"using the 'navigate_browser' action. Example input: {{'action': 'navigate_browser', "
            #     f"'parameters': {{'url': 'https://example.com'}}}}"
            # )
            # self.description_updated = True

        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {str(e)}")
            self.toolkit = None

    def _run(self, tool_input: dict) -> str:
        if not self.toolkit:
            return "Playwright toolkit is not initialized. Cannot execute actions."

        # Ensure tool_input is a dictionary. If it's a string, try to parse JSON.
        if isinstance(tool_input, str):
            try:
                tool_input = json.loads(tool_input)
            except json.JSONDecodeError:
                return "Invalid input: tool_input must be a dictionary or valid JSON string."

        # Validate that we have the necessary keys
        if not isinstance(tool_input, dict):
            return "Invalid tool_input: must be a dictionary."
        if "action" not in tool_input:
            return "Invalid tool_input: 'action' key is missing."
        if "parameters" not in tool_input:
            return "Invalid tool_input: 'parameters' key is missing."

        try:
            action = str(tool_input.get("action", "")).lower()
            parameters = tool_input.get("parameters", {})
            tool = next((t for t in self.toolkit.get_tools() if t.name.lower() == action), None)

            if not tool:
                return f"No matching tool found for action '{action}'. Supported actions: {', '.join([t.name for t in self.toolkit.get_tools()])}"

            if action == "extract_text":
                time.sleep(10)
            result = tool.run(parameters)
            if action == "extract_text":
                result += self.extract_code_blocks(result)

            if "status code 200" in result:
                result += ".Page loaded. You must now proceed with the page actions."
            return result
        except Exception as e:
            return custom_error_handler(e)

    def close_browser(self):
        """Shut down the Playwright browser instance."""
        try:
            # if self.async_browser:
            #     asyncio.run(self.async_browser.close())
            #     return "Browser instance(async) closed successfully."
            if self.sync_browser:
                self.sync_browser.close()
                return "Browser instance(sync_browser) closed successfully."
            return "Browser instance is not initialized or already closed."
        except Exception as e:
            return custom_error_handler(e)

    def extract_code_blocks(self, page_content):
        soup = BeautifulSoup(page_content, "html.parser")
        code_blocks = soup.find_all(["pre", "code"])  # Extract both <pre> and <code> elements
        return "\n".join(block.get_text() for block in code_blocks)


PlaywrightTool.model_rebuild()
