# MCP Server

A FastMCP server for exploring scraper content.

## Project Structure

- `src/mcp_server/` - Core server implementation

  - `main.py` - FastMCP server with tools
  - `cli.py` - CLI utility for version information

- `test_server.py` - Direct integration tests
- `run_server.sh` - Script to start the server

## Installation

```bash
# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package and dependencies
pip install -e .
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Usage

### Running the server

The project provides a FastMCP server that can be run using:

```bash
./run_server.sh
```

This uses the FastMCP CLI to run the server with the `stdio` transport.

Alternatively, you can run it directly with:

```bash
# Using Python
python -m src.mcp_server.main

# Using FastMCP CLI
fastmcp run src/mcp_server/main.py:mcp
```

### Testing

The recommended way to test the server is through direct integration:

```bash
./test_client.sh
```

This runs a test that imports the MCP instance directly and tests the tools without requiring a separate server process. Based on the FastMCP quickstart guide, this is the most reliable approach for testing.

## Available Tools

- `hello`: Returns a greeting message with the given name

## Notes

- The server instance is named `mcp` in `main.py` to make it easily discoverable by the FastMCP CLI
- For production use, consider using HTTP or other transports instead of stdio
