from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# might need global `magic` installed: brew install magic
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai import LLM

from crewai_tools import (SerperDevTool, WebsiteSearchTool, FileReadTool,
                          CodeInterpreterTool, FileWriterTool, ScrapeWebsiteTool,
                          DirectorySearchTool)

from crewai_tools import DirectoryReadTool, FileReadTool
from crewai_tools.tools.code_docs_search_tool.code_docs_search_tool import CodeDocsSearchTool

from helpers.get_docs_string import LocalTxTFileKnowledgeSource
from helpers.helper import validate_and_save_yaml_from_pydantic_list, write_review_changes_callback
from models import TasksModel, AgentsModel
from tools.files_langchain import FileManagementTool
from tools.shell_tool import ShellCommandTool
from tools.playwright_tool import PlaywrightTool

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

gpt4o_mini = LLM(
    model="gpt-4o-mini",
)
gpt4o = LLM(
    model="gpt-4o",
)
gpt1o_mini = LLM(
    model="o1-mini-2024-09-12",
)
gpt1o = LLM(
    model="o1-preview",
)
gemini2 = LLM(
    model="gemini/gemini-2.0-flash-exp",
    # temperature=0.7,
)
gemini2think = LLM(
    model="gemini/gemini-2.0-flash-thinking-exp-1219",
    # temperature=0.7,
)
claude = LLM(
    model="anthropic/claude-3-5-sonnet-20241022",
)


@CrewBase
class DesignCrew:
    agents_config = 'config/design_crew/agents.yaml'
    tasks_config = 'config/design_crew/tasks.yaml'

    def __init__(self, crew_name=None):
        self.crew_name = 'default_name' if crew_name is None else crew_name

        self.file_toolkit = FileManagementTool(
            root_dir=f"./{self.crew_name}",
            selected_tools=["read_file", "write_file", "list_directory"]
        )

    @agent
    def content_designer(self):
        content_designer = Agent(
            config=self.agents_config['content_designer'],
            tools=[search_tool, scrape_website_tool, file_read_tool, file_write_tool],
            allow_delegation=False,
            verbose=True,
            llm=gpt1o_mini,
            max_iter=3,
        )
        return content_designer

    @agent
    def content_designer_gemini2(self):
        content_designer = Agent(
            config=self.agents_config['content_designer'],
            tools=[search_tool, scrape_website_tool, file_read_tool, file_write_tool],
            allow_delegation=False,
            verbose=True,
            llm=gemini2,
            max_iter=3,
        )
        return content_designer

    @agent
    def qa_expert(self):
        return Agent(
            config=self.agents_config['qa_expert'],
            tools=[search_tool, web_rag_tool, file_write_tool],
            verbose=True,
            llm=claude,
            max_iter=3
        )

    @task
    def design_crew_input(self) -> Task:
        return Task(
            config=self.tasks_config['design_crew_input'],
            tools=[search_tool, scrape_website_tool],
            output_file=f"output_{self.crew_name}/src/input.json",
        )

    @task
    def design_tasks(self) -> Task:
        return Task(
            config=self.tasks_config['design_tasks'],
            context=[self.design_crew_input()],
            tools=[search_tool, scrape_website_tool],
            output_pydantic=TasksModel,
            callback=lambda output: validate_and_save_yaml_from_pydantic_list(output,
                                                                              f"output_{self.crew_name}/config/tasks.yaml"),
        )

    @task
    def design_agents(self) -> Task:
        return Task(
            config=self.tasks_config['design_agents'],
            context=[self.design_crew_input(), self.design_tasks()],
            tools=[search_tool, scrape_website_tool],
            output_pydantic=AgentsModel,
            callback=lambda output: validate_and_save_yaml_from_pydantic_list(output,
                                                                              f"output_{self.crew_name}/config/agents.yaml"),

        )

    @task
    def review_tasks_and_agents(self) -> Task:
        return Task(
            config=self.tasks_config['review_tasks_and_agents'],
            context=[self.design_crew_input(), self.design_tasks(), self.design_agents()],
            output_file=f"output_{self.crew_name}/config/review.md",
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
            callback=lambda output: write_review_changes_callback(f"output_{self.crew_name}/config"),
            output_file=f"output_{self.crew_name}/config/design_result.yaml",
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
            knowledge_sources=[
                LocalTxTFileKnowledgeSource(
                    file_path="docs_crewai/singlefile.txt",
                ),
            ]
        )


@CrewBase
class CodingCrew:
    agents_config = 'config/coding_crew/agents.yaml'
    tasks_config = 'config/coding_crew/tasks.yaml'

    def __init__(self, crew_name=None):
        self.crew_name = crew_name or 'default_name'
        self.output_dir = f"output_{self.crew_name}"
        self.directorySearchTool = DirectorySearchTool(directory=self.output_dir)

        self.review_iteration = 0
        self.max_iterations = 2

    @agent
    def architect(self) -> Agent:
        return Agent(
            config=self.agents_config['architect'],
            tools=[search_tool, file_read_tool, web_rag_tool],
            llm=gpt1o_mini,
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
            llm=gpt1o_mini,
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
            knowledge_sources=[
                LocalTxTFileKnowledgeSource(
                    file_path="docs_crewai/singlefile.txt",
                )
            ]
        )
