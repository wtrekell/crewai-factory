# CrewAI Factory Crew 🚀

A powerful meta-CrewAI project that generates custom CrewAI implementations from simple YAML configurations. Transform
your ideas into fully functional CrewAI projects with minimal effort!

> **Note**: This project is in early development stage. Currently, the Design Crew produces fairly usable results, but
> the Coding Crew's output requires significant improvements before production usage.

## 🎯 Purpose

CrewAI Factory Crew automates the creation of CrewAI projects by taking a high-level YAML description of your desired
crew and generating all necessary implementation files, including:

- Crew logic and structure
- Agent configurations
- Task definitions
- Support files and tools

## 🌟 Key Features

- **YAML-Driven Development**: Define your crew's purpose, output format, and requirements in a simple YAML file
- **Two-Stage Generation Process**:
    - Design Crew: Architects your crew's structure and configurations
    - Coding Crew: Implements the actual code and supporting files
- **Intelligent Tool Selection**: Automatically selects and configures appropriate CrewAI tools for your use case

## 📁 Project Structure

```
├── config/                # Configuration files for different crews
│   ├── coding_crew/       # Coding crew configurations
│   └── design_crew/       # Design crew configurations
├── tools/                 # Custom tools implementations
├── helpers/               # Helper functions and utilities
├── crew.py                # Core crew implementations
├── main.py                # Main execution script
└── models.py              # Pydantic models
```

## 🚀 Getting Started

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create `.env` file in the root directory and add the following environment variables with your API keys:
```
SERPER_API_KEY=YOUR_SERPER_API_KEY
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY
```

3. Run the crew factory:

```bash
python main.py
```

4. The output crew will be located in `output_*crew_name*` directory. Note that many tasks doesn't limit output to particular file, so the agents could hallucinate sometimes and write some unrequired files

## 📝 Input Format

The `crew_input.yaml` file defines your desired CrewAI project.

Example:
```yaml
crew_name: brainstorm_crew
crew_purpose: brainstorm ideas of innovative projects utilising CrewAI framework
crew_output: >
  table of ideas in `.md` file.
  The list should contain at least 10 ideas. Each idea should be described in a few sentences.
  Each idea should have:
  1. technical complexity level
  2. target market niche
  3. innovation index
```

## 🎯 Model Selection

For optimal results, the project uses a combination of models:

- `gpt1o_mini`: Initial planning and structural decisions
- `gemini2`: Code generation and technical implementations
- `claude3.5-sonnet`: Review and quality assurance tasks

This combination provides the best cost/value ratio while maintaining high-quality output.

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Improve the tasks and agents definitions or submit the alternatives, if properly tested
- Propose improvements to the overall generation process
- Improve tools selection process
- Implement custom tools development crew
- Expand on choosing the resulting crew's `process` type
