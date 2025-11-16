# Contributing Guide

Thank you for your interest in contributing to the Multi-Tenant Diary Assistant!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Multi-Tenant-Digital-Diary-Platform.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes: `make test`
6. Format code: `make format`
7. Commit: `git commit -m "Add: your feature description"`
8. Push: `git push origin feature/your-feature-name`
9. Open a Pull Request

## Development Setup

```bash
# Install dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Lint code
make lint
```

## Code Style

- Follow PEP 8
- Use Black for formatting (line length: 120)
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions focused and small

## Testing

- Write tests for new features
- Ensure all tests pass: `make test`
- Aim for >80% code coverage

## Commit Messages

Use clear, descriptive commit messages:
- `Add: feature description`
- `Fix: bug description`
- `Update: change description`
- `Refactor: improvement description`

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review

## Questions?

Open an issue or contact the maintainers.

