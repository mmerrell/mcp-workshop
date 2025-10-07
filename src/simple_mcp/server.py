"""Simple MCP server with Docker Hub search functionality."""

import urllib.request
import urllib.parse
import json
from typing import Any
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


@mcp.tool()
def search_images(query: str, page: int = 1, page_size: int = 25) -> dict[str, Any]:
    """Search for Docker images on Docker Hub.
    
    Args:
        query: Search term (e.g., "nginx", "python", "ubuntu")
        page: Page number for pagination (default: 1)
        page_size: Number of results per page (default: 25, max: 100)
        
    Returns:
        Dictionary containing search results with image information
    """
    # Docker Hub API endpoint
    base_url = "https://hub.docker.com/v2/search/repositories/"
    
    # Build query parameters
    params = {
        "query": query,
        "page": page,
        "page_size": min(page_size, 100)  # Docker Hub max is 100
    }
    
    # Construct full URL
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        # Make the request
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        # Parse and format results
        results = []
        for item in data.get("results", []):
            # Determine if it's an official image
            is_official = item.get("is_official", False)
            
            result = {
                "name": item.get("repo_name", ""),
                "description": item.get("short_description", ""),
                "star_count": item.get("star_count", 0),
                "pull_count": item.get("pull_count", 0),
                "is_official": is_official,
                "is_automated": item.get("is_automated", False),
                "type": "official" if is_official else "community"
            }
            results.append(result)
        
        return {
            "query": query,
            "count": data.get("count", 0),
            "page": page,
            "page_size": page_size,
            "num_results": len(results),
            "results": results
        }
        
    except urllib.error.HTTPError as e:
        return {
            "error": f"HTTP Error {e.code}: {e.reason}",
            "query": query
        }
    except Exception as e:
        return {
            "error": f"Error searching Docker Hub: {str(e)}",
            "query": query
        }


if __name__ == "__main__":
    mcp.run()
