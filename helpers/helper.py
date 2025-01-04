import logging
import os
import re
from typing import Any
import yaml
from dotenv import load_dotenv, find_dotenv

logging.basicConfig(level=logging.ERROR)


# these expect to find a .env file at the directory above the lesson.                                                                                                                     # the format for that file is (without the comment)                                                                                                                                       #API_KEYNAME=AStringThatIsTheLongAPIKeyFromSomeService
def load_env():
    _ = load_dotenv(find_dotenv())


def to_snake_case(name: str) -> str:
    name = name.strip('"\'')
    name = name.replace(' ', '_')
    # Then handle camelCase and PascalCase
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)

    # Convert to lowercase and clean up any double underscores
    name = name.lower()
    name = re.sub('_+', '_', name)

    # Remove any non-alphanumeric characters except underscores
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name


def folded_str_presenter(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='>')
    elif len(data) > 80:  # Threshold for using folded style
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='>')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


yaml.add_representer(str, folded_str_presenter)


def format_task_data(data: dict) -> tuple:
    task_name = data.pop("name", None)
    if not task_name:
        raise ValueError("Each task must have a 'name' field.")
    return task_name, data


def pydantic_list_to_dict(obj: Any) -> dict:
    formatted_data = {}
    models = obj.list
    for task in models:
        data = task.dict()
        name, task_data = format_task_data(data)
        formatted_data[name] = task_data
    return formatted_data


def validate_and_save_yaml_from_pydantic_list(output, output_file=None):
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        # Register the custom string presenter
        # Convert all pydantic models to dict form
        yaml_data = pydantic_list_to_dict(output.pydantic)

        with open(output_file, 'w', encoding='utf-8') as file:
            for key, value in yaml_data.items():
                task_dict = {key: value}
                yaml.dump(
                    task_dict,
                    file,
                    sort_keys=False,
                    default_flow_style=False,
                    allow_unicode=True
                )
                file.write('\n')  # Add an empty line between tasks

        print(f"Output successfully written to {output_file}")

    except Exception as e:
        print(f"Error validating or formatting output: {e}")
        raise


def flatten_structure(
        data: Any,
        fields: list,
        container: dict,
        current_key: str = None,
) -> None:
    if isinstance(data, dict):
        if isinstance(data, dict):
            if 'name' in data:
                current_key = data['name']

            intersection = set(data.keys()).intersection(fields)
            if intersection:
                if current_key is None:
                    current_key = f"item_{len(container) + 1}"

                extracted = {f: data.get(f, "") for f in fields}
                container[current_key] = extracted
            else:
                for k, v in data.items():
                    flatten_structure(v, fields, container, current_key=k)

        elif isinstance(data, list):
            for item in data:
                flatten_structure(item, fields, container)


def format_yaml_content(content: str, is_tasks: bool = False) -> str:
    try:
        data = yaml.safe_load(content)
        if not data or not isinstance(data, dict):
            return content

        # Extract tasks data if present
        content_data = data.get('tasks', data)
        if not content_data:
            return content

        # Define fields based on content type
        fields = ['description', 'expected_output', 'agent'] if is_tasks else ['role', 'goal', 'backstory']

        # Process and format entries
        formatted_entries = {}
        for key, value in content_data.items():
            if not isinstance(value, dict):
                continue

            snake_case_key = to_snake_case(key)
            entry = {
                field: to_snake_case(value.get(field)) if field == 'agent' and is_tasks
                else value.get(field, '')
                for field in fields
            }
            formatted_entries[snake_case_key] = entry

        output = ''
        for i, (key, value) in enumerate(formatted_entries.items()):
            section = yaml.dump(
                {key: value},
                default_flow_style=False,
                allow_unicode=True,
                width=80
            )
            output += section
            if i < len(formatted_entries) - 1:
                output += '\n'

        return output

    except Exception as e:
        logging.error(f"Error formatting YAML: {str(e)}")
        return content


def write_review_changes_callback(base_dir: str) -> str:
    try:
        if not base_dir:
            base_dir = "output_default/src/config"

        tasks_path = os.path.join(base_dir, "tasks.yaml")
        agents_path = os.path.join(base_dir, "agents.yaml")

        if not (os.path.exists(tasks_path) and os.path.exists(agents_path)):
            return f"Missing tasks.yaml or agents.yaml in {base_dir}"

        with open(tasks_path, 'r') as f:
            tasks_content = f.read()
        formatted_tasks = format_yaml_content(tasks_content, is_tasks=True)
        with open(tasks_path, 'w') as f:
            f.write(formatted_tasks)

        with open(agents_path, 'r') as f:
            agents_content = f.read()
        formatted_agents = format_yaml_content(agents_content, is_tasks=False)
        with open(agents_path, 'w') as f:
            f.write(formatted_agents)

        return f"Successfully reformatted files in {base_dir}"

    except Exception as e:
        logging.error("Error in callback: %s", str(e))
        return f"Error in callback: {str(e)}"
