#!/bin/bash
# Run the MCP Server using FastMCP CLI

# Activate virtual environment
source .venv/bin/activate

# Run the server using fastmcp
fastmcp run src/mcp_server/main.py:mcp 