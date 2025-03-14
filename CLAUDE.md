# CLAUDE.md - Coding Guidelines for CUA Sample App

## Setup & Installation
- `python3 -m venv .venv` - Create virtual environment
- `source .venv/bin/activate` - Activate virtual environment
- `pip install -r requirements.txt` - Install dependencies

## Environment Configuration
- Create `.env` file with `ANTHROPIC_API_KEY=your_key_here` for Claude
- For OpenAI, use `OPENAI_API_KEY=your_key_here`

## Run Commands
- `python cli.py --computer local-playwright` - Run with local Playwright
- `python cli.py --computer local-playwright --model claude-3-sonnet-20240229` - Specify model
- `python -m examples.claude_example` - Run Claude example
- `python simple_cua_loop.py` - Run simple CUA loop

## Docker Usage
- `docker build -t cua-sample-app .` - Build Docker image
- `docker run --rm -it --name cua-sample-app -p 5900:5900 --dns=1.1.1.3 -e DISPLAY=:99 cua-sample-app` - Run container

## Code Style Guidelines
- Follow PEP 8 (4-space indentation, 79-char line limit)
- Use descriptive snake_case for variables/functions, CamelCase for classes
- Add type hints (use Protocol for interfaces where appropriate)
- Include docstrings with triple quotes for all classes and functions
- Import order: stdlib → third-party → local (grouped with blank lines)
- Use explicit exception handling with try/except blocks
- Prefer composition over inheritance for extensibility
- Avoid global variables and mutable default arguments
- For safety-related code, use explicit validation and error handling