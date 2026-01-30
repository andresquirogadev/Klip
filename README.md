# Klip Clipboard Helper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/andresquirogadev/Klip/actions/workflows/ci.yml/badge.svg)](https://github.com/andresquirogadev/Klip/actions/workflows/ci.yml)

A lightweight Windows background tool that provides instant access
to frequently-used SQL snippets and clipboard content.

**Repository:** https://github.com/andresquirogadev/Klip.git

## Why
Developers and operators often need to copy the same SQL queries,
identifiers, commands or snippets multiple times a day. This tool reduces friction
by keeping critical information one shortcut away.

## Features
- Runs silently in the background
- Global hotkey access
- Instant clipboard injection
- Minimal resource usage
- Portable executable support

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10 or later

### From Source
1. Clone the repository:
   ```bash
   git clone https://github.com/andresquirogadev/Klip.git
   cd Klip
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

### Portable Executable
Download the latest portable executable from the [Releases](https://github.com/andresquirogadev/Klip/releases) page.

## Usage
1. Launch the application
2. Configure your SQL snippets in `sql_snippets.json`
3. Use the global hotkey (configurable) to access the snippet selector
4. Select and copy snippets to clipboard

## Configuration
Edit `config.json` to customize:
- Hotkeys
- Snippet categories
- UI preferences

## Use cases
- Copying SQL queries, contract IDs, IPs, commands
- Repetitive operational tasks
- Support and admin workflows
- Database administration

## Tech
- Windows
- Python
- Background process

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Status
Used daily in production environments.