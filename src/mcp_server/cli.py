"""Command-line interface for the MCP Server."""

import sys

import fastmcp


def version() -> None:
    """Print version information and exit."""
    print("MCP Server v0.1.0")
    print(f"FastMCP v{fastmcp.__version__}")
    sys.exit(0)


def main() -> None:
    """Run the CLI application."""
    version()


if __name__ == "__main__":
    main()
