import re
from typing import List

from pydantic import BaseModel, Field, field_validator


def to_snake_case(s: str) -> str:
    s = re.sub(r'[^\w\s]', ' ', s)

    s = re.sub(r'(?<=[a-z0-9])([A-Z])', r'_\1', s)
    s = re.sub(r'(?<=[A-Z])([A-Z][a-z])', r'_\1', s)
    s = re.sub(r'[\s\-]+', '_', s)
    return s.lower()


class AgentModel(BaseModel):
    name: str = Field(...,
                      description="Name of the agent. Must describe his role in concise manner. format: `agent_name`")
    role: str = Field(..., description="Human-like role of the agent within team")
    goal: str = Field(..., description="Agent's goal")
    backstory: str = Field(..., description="Agent's backstory")

    @field_validator('name')
    def validate_name_format(cls, v):
        return to_snake_case(v)


class AgentsModel(BaseModel):
    list: List[AgentModel]


class TaskModel(BaseModel):
    name: str = Field(..., description="Name of the task. format: `task_name`")
    description: str = Field(..., description="Description of the task")
    expected_output: str = Field(..., description="Expected output of the task")
    agent: str = Field(..., description="Agent responsible for the task, format: `agent_name`")

    @field_validator('name')
    def validate_name_format(cls, v):
        return to_snake_case(v)

    @field_validator('agent')
    def validate_agent_format(cls, v):
        return to_snake_case(v)


class TasksModel(BaseModel):
    list: List[TaskModel]

# TaskModel.model_rebuild()
# TaskModel.model_rebuild()
