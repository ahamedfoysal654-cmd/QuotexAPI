# Contributing to QuotexAPI

First off, thank you for considering contributing to QuotexAPI! It's people like you that make QuotexAPI such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include logs if applicable**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and explain which behavior you expected to see instead**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the Python style guide (PEP 8, Black formatting)
* Include appropriate test cases
* Update documentation as needed
* End all files with a newline

## Development Setup

1. Fork the repo and create your branch from `main`
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Make your changes
4. Run tests:
   ```bash
   pytest
   ```
5. Format your code:
   ```bash
   black QuotexAPI/
   isort QuotexAPI/
   ```
6. Commit your changes using a descriptive commit message

## Style Guide

### Python Style

* Follow PEP 8
* Use Black for formatting (line length: 100)
* Use isort for import sorting
* Use type hints where appropriate
* Write docstrings for all public methods (Google style)

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Documentation

* Use clear and concise language
* Include code examples where appropriate
* Keep the README up to date
* Document all public APIs

## Testing

* Write unit tests for new features
* Ensure all tests pass before submitting PR
* Aim for high code coverage
* Use pytest for testing

## Project Structure

```
QuotexAPI/
├── QuotexAPI/           # Main package
│   ├── services/        # Service layer
│   ├── utils/           # Utilities
│   ├── client.py        # Main client
│   ├── models.py        # Data models
│   └── ...
├── examples/            # Example scripts
├── tests/              # Test files
└── docs/               # Documentation
```

## Questions?

Feel free to open an issue with the "question" label.

Thank you for contributing! 🎉
