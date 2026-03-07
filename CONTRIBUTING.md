# Contributing to Wave-Haven

Thank you for your interest in contributing to Wave-Haven! We welcome contributions from the community.

## 🌊 Haven Principles

Before contributing, please understand our core philosophy:

> **"Wave flows, Haven shelters"**
> 
> We believe in the balance between dynamic execution (Wave) and stable knowledge (Haven).
> Every contribution should respect this duality.

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/wave-haven.git
cd wave-haven
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Run tests to ensure everything works
pytest tests/
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

## 📋 Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small

### Commit Messages

Use conventional commits:

```
feat: add new wave orchestration feature
fix: resolve event bus connection issue
docs: update API documentation
refactor: optimize memory storage
test: add tests for haven system
```

### Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=wave_haven --cov-report=html
```

## 🎯 Areas for Contribution

### High Priority

- [ ] Improve semantic search accuracy
- [ ] Add more agent templates
- [ ] Optimize memory storage
- [ ] Better error handling

### Medium Priority

- [ ] Web UI for monitoring
- [ ] More integrations (Slack, Discord)
- [ ] Performance benchmarks
- [ ] Additional language support

### Documentation

- [ ] Translation to other languages
- [ ] More examples and tutorials
- [ ] Video demonstrations
- [ ] Best practices guide

## 📝 Pull Request Process

1. **Update Documentation**: If you change APIs, update the documentation
2. **Add Tests**: Ensure your changes have test coverage
3. **Update CHANGELOG**: Add your changes to CHANGELOG.md
4. **Submit PR**: Create a pull request with clear description
5. **Code Review**: Wait for maintainers to review
6. **Merge**: Once approved, your PR will be merged

## 🐛 Reporting Bugs

When reporting bugs, please include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: How to trigger the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, OpenClaw version
- **Logs**: Relevant log output

## 💡 Feature Requests

We love new ideas! When suggesting features:

- Describe the use case
- Explain why it fits Wave-Haven's philosophy
- Consider implementation complexity
- Be open to discussion

## 🌐 Community

- **GitHub Discussions**: For questions and ideas
- **Issues**: For bugs and features
- **Pull Requests**: For code contributions

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect different viewpoints

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Acknowledged in documentation

Thank you for making Wave-Haven better!

---

**Questions?** Open an issue or start a discussion on GitHub.
