"""Main entry point for the ScraperCreators MCP Server."""

from fastmcp import FastMCP


# Name the FastMCP instance 'mcp' to make it discoverable by the CLI
mcp = FastMCP(
    title="ScraperCreators MCP Server",
    description="A FastMCP server for the ScraperCreators platform",
)


@mcp.tool()
def hello(name: str) -> str:
    """Return a greeting message.
    
    Args:
        name: The name to greet
        
    Returns:
        A greeting message
    """
    return f"Hello, {name}! Welcome to the ScraperCreators MCP Server."


def main() -> None:
    """Run the FastMCP application."""
    mcp.run()


if __name__ == "__main__":
    main()
