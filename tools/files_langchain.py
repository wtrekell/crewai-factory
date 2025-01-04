from typing import List, Optional, Dict
from crewai.tools import BaseTool
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_community.tools import BaseTool as LangchainBaseTool
from pydantic import Field, PrivateAttr


class FileManagementTool(BaseTool):
    name: str = "File Management"
    description: str = "Toolkit for performing file operations"
    root_dir: Optional[str] = Field(default=None)
    selected_tools: List[str] = Field(default_factory=list)
    _toolkit: FileManagementToolkit = PrivateAttr()
    _tools: Dict = PrivateAttr(default_factory=dict)

    def __init__(self, root_dir: Optional[str] = None, selected_tools: Optional[List[str]] = None, **kwargs):
        selected_tools = selected_tools or []
        super().__init__(root_dir=root_dir, selected_tools=selected_tools, **kwargs)
        self._toolkit = FileManagementToolkit(root_dir=root_dir, selected_tools=selected_tools)
        self._initialize_tools()

    def _initialize_tools(self):
        tools = self._toolkit.get_tools()
        self._tools = {t.name: t for t in tools}
        tool_descriptions = []
        for name, tool in self._tools.items():
            args = tool.args if hasattr(tool, 'args') else {}
            arg_desc = f" Arguments: {args}" if args else ""
            tool_descriptions.append(f"{name}: {tool.description}{arg_desc}")

        self.description = "Available operations:\n" + "\n".join(tool_descriptions)

    def _run(self, **kwargs) -> str:
        if 'tool_name' not in kwargs:
            raise ValueError(f"Must specify 'tool_name'. Available tools: {list(self._tools.keys())}")

        tool_name = kwargs.pop('tool_name')
        if tool_name not in self._tools:
            raise ValueError(f"Tool {tool_name} not found. Available: {list(self._tools.keys())}")

        return self._tools[tool_name].run(**kwargs)
