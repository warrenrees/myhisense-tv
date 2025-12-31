# Contributing to myhisense-tv

Thank you for your interest in contributing to this project! This document provides guidelines for contributions.

## Getting Started

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/warrenrees/myhisense-tv.git
   cd hisense-tv
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or: venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in editable mode
   ```

### Running Tests

Currently, this project does not have automated tests. Contributions adding tests are welcome!

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use type hints for function parameters and return values
- Include docstrings for all public functions and classes
- Use `logging` instead of `print()` statements in library code

### Type Hints

Use type hints compatible with Python 3.8+:

```python
from typing import Dict, List, Optional

def my_function(param: str, items: List[str]) -> Optional[Dict[str, Any]]:
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def my_function(param: str) -> bool:
    """Brief description of function.

    Args:
        param: Description of parameter.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param is invalid.
    """
```

## Submitting Changes

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Commit with descriptive messages
5. Push to your fork
6. Open a Pull Request

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update")
- Reference issues when applicable (e.g., "Fix #123")

Example:
```
Add support for new TV model authentication

- Implement protocol version 3300 detection
- Add fallback for legacy authentication
- Update documentation
```

## Reporting Issues

When reporting bugs, please include:

- Python version (`python --version`)
- Operating system
- TV model (if known)
- Steps to reproduce the issue
- Error messages or logs
- Expected vs actual behavior

## Feature Requests

Feature requests are welcome! Please describe:

- The use case for the feature
- How it should work
- Any implementation suggestions

## Protocol Documentation

If you discover new protocol details through packet analysis or APK decompilation, please document them in `VIDAA_PROTOCOL_ANALYSIS.md`.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
