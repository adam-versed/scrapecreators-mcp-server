"""Type stubs for fastmcp."""

from typing import Any, Callable, TypeVar, Dict, overload, Optional

__version__: str

T = TypeVar('T')

class FastMCP:
    """FastMCP application class."""
    
    def __init__(
        self,
        title: str,
        description: str = "",
        **kwargs
    ) -> None:
        """Initialize a FastMCP application."""
        ...
    
    def run(self) -> None:
        """Run the FastMCP application."""
        ...
    
    @overload
    def tool(self) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Register a function as a tool."""
        ...
    
    @overload
    def tool(self, func: Callable[..., T]) -> Callable[..., T]:
        """Register a function as a tool."""
        ...


class Client:
    """FastMCP client class."""
    
    def __init__(self, server: Any, **kwargs) -> None:
        """Initialize a FastMCP client."""
        ...
    
    async def __aenter__(self) -> "Client":
        """Enter the client context."""
        ...
    
    async def __aexit__(self, *args: Any) -> None:
        """Exit the client context."""
        ...
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Call a tool on the server."""
        ... 