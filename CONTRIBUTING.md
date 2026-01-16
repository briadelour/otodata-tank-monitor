# Contributing to Otodata Propane Tank Monitor

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Home Assistant version
- Integration version
- Relevant logs from Home Assistant

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:
- A clear, descriptive title
- Detailed description of the proposed feature
- Why this feature would be useful
- Example use cases

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and concise

### Testing

Before submitting a PR:
1. Test your changes with Home Assistant
2. Ensure the integration loads without errors
3. Verify all sensors work correctly
4. Check Home Assistant logs for any warnings or errors

## Development Setup

1. Clone the repository
2. Create a symbolic link from your HA `custom_components` folder to the integration:
   ```bash
   ln -s /path/to/otodata-tank-monitor/custom_components/neevo /path/to/homeassistant/custom_components/neevo
   ```
3. Restart Home Assistant
4. Configure the integration through the UI

## Questions?

Feel free to open an issue for questions or discussion!

## Code of Conduct

- Be respectful and considerate
- Welcome newcomers
- Be patient with questions
- Focus on constructive feedback
