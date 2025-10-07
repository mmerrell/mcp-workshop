"""Simple MCP server with basic greeting functionality."""

from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Simple Workshop Server")


@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name.
    
    Args:
        name: The name of the person to greet
        
    Returns:
        A friendly greeting message
    """
    return f"Hello, {name}! Welcome to the MCP workshop!"


if __name__ == "__main__":
    mcp.run()
