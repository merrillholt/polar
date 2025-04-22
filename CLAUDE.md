# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup
- Create conda environment: `conda env create -f environment.yml`
- Activate environment: `conda activate polarapp`

## Commands
- Run application: `python polar.py`
- Lint code: `flake8 polar.py`
- Format code: `black polar.py`
- Type check: `mypy polar.py`

## Code Style
- Imports: Group standard library, third-party packages, then local modules
- Formatting: 4-space indentation, 88-character line length (Black style)
- Types: Use type hints for function parameters and return values
- Docstrings: Use NumPy docstring format for all functions and classes
- Naming: snake_case for variables/functions, PascalCase for classes
- Error handling: Use try-except blocks with specific exceptions
- Comments: Descriptive, explain why not what
- Prefer clear, descriptive variable names over abbreviations