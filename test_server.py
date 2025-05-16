"""Test the MCP Server with a direct integration test."""

import asyncio
from fastmcp import Client, FastMCP
from src.mcp_server.main import mcp


async def test_hello_tool():
    """Test the hello tool by calling it directly."""
    client = Client(mcp)
    
    async with client:
        result = await client.call_tool("hello", {"name": "Test User"})
        print(f"Tool result: {result}")
        
        # The result is a list with a TextContent object
        # Extract the text from the first item
        text_content = str(result[0])
        print(f"Extracted text: {text_content}")
        
        assert "Test User" in text_content, "Name should be included in the response"
        print("Test passed!")


def main():
    """Run the test."""
    asyncio.run(test_hello_tool())


if __name__ == "__main__":
    main() 