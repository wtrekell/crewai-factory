import os
from datetime import datetime

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# might need global `magic` installed: brew install magic
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai import LLM

# Temporary replacement for missing crewai_tools
from crewai.tools import BaseTool
from typing import Any
from pydantic import Field
import os
import json

class FileReadTool(BaseTool):
    name: str = "File Reader"
    description: str = "Reads content from a file"
    
    def _run(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

class FileWriterTool(BaseTool):
    name: str = "File Writer"
    description: str = "Writes content to a file"
    
    def _run(self, file_path: str, content: str) -> str:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

class DirectorySearchTool(BaseTool):
    name: str = "Directory Search"
    description: str = "Searches for files in a directory"
    directory: str = Field(default=".", description="Directory to search in")
    
    def _run(self, query: str = "") -> str:
        try:
            files = []
            for root, dirs, filenames in os.walk(self.directory):
                for filename in filenames:
                    if query.lower() in filename.lower():
                        files.append(os.path.join(root, filename))
            return "\n".join(files) if files else "No files found"
        except Exception as e:
            return f"Error searching directory: {str(e)}"

class SerperDevTool(BaseTool):
    name: str = "Search Tool"
    description: str = "Simple search tool placeholder"
    
    def _run(self, query: str) -> str:
        return f"Search results for: {query} (placeholder - configure with real search API)"

class WebsiteSearchTool(BaseTool):
    name: str = "Website Search"
    description: str = "Website search tool placeholder"
    
    def _run(self, url: str) -> str:
        return f"Website search for: {url} (placeholder - configure with real web scraping)"

class ScrapeWebsiteTool(BaseTool):
    name: str = "Website Scraper"
    description: str = "Website scraping tool placeholder"
    
    def _run(self, url: str) -> str:
        return f"Scraped content from: {url} (placeholder - configure with real web scraping)"

class CodeInterpreterTool(BaseTool):
    name: str = "Code Interpreter"
    description: str = "Code execution tool placeholder"
    
    def _run(self, code: str) -> str:
        return f"Code execution result: (placeholder - configure with real code execution)"

class CodeDocsSearchTool(BaseTool):
    name: str = "Code Docs Search"
    description: str = "Searches code documentation"
    docs_url: str = Field(default="", description="Documentation URL to search")
    
    def _run(self, query: str) -> str:
        return f"Code docs search for: {query} at {self.docs_url} (placeholder - configure with real docs search)"

from helpers.get_docs_string import LocalTxTFileKnowledgeSource
from helpers.helper import validate_and_save_yaml_from_pydantic_list, write_review_changes_callback
from models import TasksModel, AgentsModel
from tools.files_langchain import FileManagementTool
from tools.shell_tool import ShellCommandTool
# Placeholder for PlaywrightTool - install playwright if needed
class PlaywrightTool(BaseTool):
    name: str = "Playwright Browser"
    description: str = "Browser automation tool placeholder"
    
    def _run(self, command: str) -> str:
        return f"Browser automation: {command} (placeholder - install playwright to use)"

shell_tool = ShellCommandTool()
file_read_tool = FileReadTool()
file_write_tool = FileWriterTool()
search_tool = SerperDevTool()
web_rag_tool = WebsiteSearchTool()
code_interpreter_tool = CodeInterpreterTool()
playwright_tool = PlaywrightTool()
scrape_website_tool = ScrapeWebsiteTool()
docsSearchTool = DirectorySearchTool(directory='./docs_crewai')
docsSearchRagTool = CodeDocsSearchTool(docs_url='https://docs.crewai.com')

docs_singlefile = TextFileKnowledgeSource(
    file_paths=["singlefile.txt"]
)

gpt4o_mini = LLM(
    model="gpt-4.1-mini-2025-04-14",
)
gpt4o = LLM(
    model="gpt-4.1-mini-2025-04-14",
)
gpt1o_mini = LLM(
    model="gpt-4.1-mini-2025-04-14",
)
gpt1o = LLM(
    model="gpt-4.1-mini-2025-04-14",
)
gemini2 = LLM(
    model="gemini/gemini-2.5-pro",
    # temperature=0.7,
)
gemini2think = LLM(
    model="gemini/gemini-2.5-pro",
    # temperature=0.7,
)
claude = LLM(
    model="anthropic/claude-sonnet-4-20250514",
)


@CrewBase
class DesignCrew:
    agents_config = 'config/design_crew/agents.yaml'
    tasks_config = 'config/design_crew/tasks.yaml'

    def __init__(self, crew_name=None):
        self.crew_name = 'default_name' if crew_name is None else crew_name
        
        # Create timestamped crew store directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"crew_store/{self.crew_name}_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/config", exist_ok=True)
        os.makedirs(f"{self.output_dir}/src", exist_ok=True)

        self.file_toolkit = FileManagementTool(
            root_dir=f"./{self.output_dir}",
            selected_tools=["read_file", "write_file", "list_directory"]
        )

    @agent
    def content_designer(self):
        content_designer = Agent(
            config=self.agents_config['content_designer'],
            tools=[search_tool, scrape_website_tool, file_read_tool, file_write_tool],
            allow_delegation=False,
            verbose=True,
            llm=gpt4o_mini,
            max_iter=1,
        )
        return content_designer

    @agent
    def content_designer_gemini2(self):
        content_designer = Agent(
            config=self.agents_config['content_designer'],
            tools=[search_tool, scrape_website_tool, file_read_tool, file_write_tool],
            allow_delegation=False,
            verbose=True,
            llm=gpt4o_mini,
            max_iter=1,
        )
        return content_designer

    @agent
    def qa_expert(self):
        return Agent(
            config=self.agents_config['qa_expert'],
            tools=[search_tool, web_rag_tool, file_write_tool],
            verbose=True,
            llm=gpt4o_mini,
            max_iter=1
        )

    @task
    def design_crew_input(self) -> Task:
        return Task(
            config=self.tasks_config['design_crew_input'],
            tools=[search_tool, scrape_website_tool],
            output_file=f"{self.output_dir}/src/input.json",
        )

    @task
    def design_tasks(self) -> Task:
        return Task(
            config=self.tasks_config['design_tasks'],
            context=[self.design_crew_input()],
            tools=[search_tool, scrape_website_tool],
            output_pydantic=TasksModel,
            callback=lambda output: validate_and_save_yaml_from_pydantic_list(output,
                                                                              f"{self.output_dir}/config/tasks.yaml"),
        )

    @task
    def design_agents(self) -> Task:
        return Task(
            config=self.tasks_config['design_agents'],
            context=[self.design_crew_input(), self.design_tasks()],
            tools=[search_tool, scrape_website_tool],
            output_pydantic=AgentsModel,
            callback=lambda output: validate_and_save_yaml_from_pydantic_list(output,
                                                                              f"{self.output_dir}/config/agents.yaml"),

        )

    @task
    def review_tasks_and_agents(self) -> Task:
        return Task(
            config=self.tasks_config['review_tasks_and_agents'],
            context=[self.design_crew_input(), self.design_tasks(), self.design_agents()],
            output_file=f"{self.output_dir}/config/review.md",
        )

    @task
    def prepare_review_changes(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_review_changes'],
            context=[self.design_tasks(), self.design_agents(), self.review_tasks_and_agents()],
            tools=[file_read_tool, file_write_tool]
        )

    @task
    def write_review_changes(self) -> Task:
        return Task(
            config=self.tasks_config['write_review_changes'],
            context=[self.prepare_review_changes()],
            tools=[file_write_tool],
            callback=lambda output: write_review_changes_callback(f"{self.output_dir}/config"),
            output_file=f"{self.output_dir}/config/design_result.yaml",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=[
                self.design_crew_input(),
                self.design_tasks(),
                self.design_agents(),
                self.review_tasks_and_agents(),
                self.prepare_review_changes(),
                self.write_review_changes(),
            ],
            process=Process.sequential,
            # memory=True,
            verbose=True,
            knowledge_sources=[docs_singlefile],
        )


@CrewBase
class CodingCrew:
    agents_config = 'config/coding_crew/agents.yaml'
    tasks_config = 'config/coding_crew/tasks.yaml'

    def __init__(self, crew_name=None, design_output_dir=None):
        self.crew_name = crew_name or 'default_name'
        
        # Use the same timestamped directory as DesignCrew if provided
        if design_output_dir:
            self.output_dir = design_output_dir
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = f"crew_store/{self.crew_name}_{timestamp}"
            os.makedirs(self.output_dir, exist_ok=True)
            
        # Ensure additional directories exist
        os.makedirs(f"{self.output_dir}/src", exist_ok=True)
        os.makedirs(f"{self.output_dir}/tests", exist_ok=True)
        
        self.directorySearchTool = DirectorySearchTool(directory=self.output_dir)

        self.review_iteration = 0
        self.max_iterations = 2

    @agent
    def architect(self) -> Agent:
        return Agent(
            config=self.agents_config['architect'],
            tools=[search_tool, file_read_tool, web_rag_tool],
            llm=gpt4o_mini,
            max_iter=3
        )

    @agent
    def developer(self) -> Agent:
        return Agent(
            config=self.agents_config['developer'],
            tools=[
                file_read_tool,
                file_write_tool,
                code_interpreter_tool,
                self.directorySearchTool,
                search_tool
            ],
            llm=gemini2,
            max_iter=2
        )

    @agent
    def technical_lead(self) -> Agent:
        return Agent(
            config=self.agents_config['technical_lead'],
            tools=[
                file_read_tool,
                docsSearchRagTool,
                search_tool
            ],
            llm=claude,
            max_iter=3
        )

    @agent
    def qa_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['qa_engineer'],
            tools=[
                file_read_tool,
                self.directorySearchTool,
                code_interpreter_tool,
                shell_tool
            ],
            llm=gpt4o_mini,
            max_iter=3
        )

    @task
    def select_tools(self) -> Task:
        return Task(
            config=self.tasks_config['select_tools'],
            tools=[file_read_tool, DirectorySearchTool(directory=self.output_dir)]
        )

    @task
    def implement_crew_logic(self) -> Task:
        return Task(
            config=self.tasks_config['implement_crew_logic'],
            context=[self.select_tools()],
            tools=[file_write_tool, code_interpreter_tool],
            output_file=f"{self.output_dir}/crew.py"
        )

    @task
    def implement_support_files(self) -> Task:
        return Task(
            config=self.tasks_config['implement_support_files'],
            context=[self.implement_crew_logic()],
            tools=[file_write_tool, code_interpreter_tool]
        )

    @task
    def review_implementation(self) -> Task:
        return Task(
            config=self.tasks_config['review_implementation'],
            context=[self.select_tools(), self.implement_crew_logic(), self.implement_support_files()],
            tools=[file_read_tool, docsSearchRagTool, self.directorySearchTool],
            # callback=self.implement_review_changes
        )

    @task
    def implement_review_changes(self) -> Task:
        return Task(
            config=self.tasks_config['implement_review_changes'],
            context=[self.review_implementation()],
            tools=[file_write_tool, code_interpreter_tool],
            # callback=self._track_review_iteration
        )

    # def _track_review_iteration(self, output):
    #     self.review_iteration = getattr(self, 'review_iteration', 0) + 1
    #     if self.review_iteration < 2 and 'ISSUES FOUND:' in output.raw:
    #         return self.review_implementation()
    #     return output

    # @task
    # def verify_changes(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['verify_changes'],
    #         context=[self.implement_review_changes()],
    #         tools=[FileReadTool(), DirectoryReadTool(), CodeInterpreterTool()]
    #     )
    #
    # @task
    # def implement_tests(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['implement_tests'],
    #         context=[self.implement_crew_logic(), self.implement_support_files()],
    #         tools=[FileWriterTool(), CodeInterpreterTool()],
    #         output_file=f"{self.output_dir}/tests/test_crew.py"
    #     )
    #
    # @task
    # def execute_tests(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['execute_tests'],
    #         context=[self.implement_tests()],
    #         tools=[ShellCommandTool(), CodeInterpreterTool()],
    #         output_file=f"{self.output_dir}/tests/test_results.md"
    #     )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=[
                self.select_tools(),
                self.implement_crew_logic(),
                self.implement_support_files(),
                self.review_implementation(),
                self.implement_review_changes(),
                # self.verify_changes(),
                # self.implement_tests(),
                # self.execute_tests()
            ],
            process=Process.sequential,
            # memory=True,
            verbose=True,
            knowledge_sources=[docs_singlefile],
            embedder={
                "provider": "google",
                "config": {
                    "model": "models/text-embedding-004",
                    "api_key": os.environ.get("GEMINI_API_KEY"),
                }
            }
        )
