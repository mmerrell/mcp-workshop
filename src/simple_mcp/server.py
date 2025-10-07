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

@mcp.tool()
def get_image_tags(
    image_name: str, 
    page: int = 1, 
    page_size: int = 25,
    ordering: str = "-last_updated"
) -> dict[str, Any]:
    """List all tags for a Docker image.
    
    Args:
        image_name: Name of the image (e.g., "nginx", "library/python")
                   For official images, use "library/imagename"
        page: Page number for pagination (default: 1)
        page_size: Number of results per page (default: 25, max: 100)
        ordering: Sort order - options include:
                 "-last_updated" (newest first, default)
                 "last_updated" (oldest first)
                 "-name" (Z-A)
                 "name" (A-Z)
        
    Returns:
        Dictionary containing tag information
    """
    # For official images, prepend "library/" if not present
    if "/" not in image_name and image_name in ["nginx", "python", "redis", "ubuntu", "postgres", "mysql", "node", "alpine"]:
        image_name = f"library/{image_name}"
    
    base_url = f"https://hub.docker.com/v2/repositories/{image_name}/tags"
    
    params = {
        "page": page,
        "page_size": min(page_size, 100),
        "ordering": ordering
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        tags = []
        for tag in data.get("results", []):
            tag_info = {
                "name": tag.get("name", ""),
                "full_size": tag.get("full_size", 0),
                "last_updated": tag.get("last_updated", ""),
                "last_updater_username": tag.get("last_updater_username", ""),
                "images_count": len(tag.get("images", [])),
                "digest": tag.get("digest", "")
            }
            tags.append(tag_info)
        
        return {
            "image": image_name,
            "count": data.get("count", 0),
            "page": page,
            "page_size": page_size,
            "ordering": ordering,
            "num_results": len(tags),
            "tags": tags
        }
        
    except urllib.error.HTTPError as e:
        return {
            "error": f"HTTP Error {e.code}: {e.reason}",
            "image": image_name,
            "hint": "For official images, try 'library/imagename' (e.g., 'library/nginx')"
        }
    except Exception as e:
        return {
            "error": f"Error fetching tags: {str(e)}",
            "image": image_name
        }


@mcp.tool()
def get_tag_details(image_name: str, tag: str = "latest") -> dict[str, Any]:
    """Get detailed manifest and metadata for a specific image tag.
    
    Args:
        image_name: Name of the image (e.g., "nginx", "library/python")
        tag: Specific tag to inspect (default: "latest")
        
    Returns:
        Dictionary containing detailed tag information including:
        - Digest
        - Size
        - Layers
        - Architecture variants
        - OS information
    """
    # For official images, prepend "library/" if not present
    if "/" not in image_name and image_name in ["nginx", "python", "redis", "ubuntu", "postgres", "mysql", "node", "alpine"]:
        image_name = f"library/{image_name}"
    
    url = f"https://hub.docker.com/v2/repositories/{image_name}/tags/{tag}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        # Extract image variants (different architectures)
        images = []
        for img in data.get("images", []):
            image_info = {
                "architecture": img.get("architecture", ""),
                "os": img.get("os", ""),
                "size": img.get("size", 0),
                "digest": img.get("digest", ""),
                "status": img.get("status", ""),
                "last_pushed": img.get("last_pushed", "")
            }
            
            # Add variant info if available
            if img.get("variant"):
                image_info["variant"] = img.get("variant")
            
            images.append(image_info)
        
        # Calculate total size across all variants
        total_size = sum(img.get("size", 0) for img in data.get("images", []))
        
        return {
            "image": image_name,
            "tag": tag,
            "name": data.get("name", ""),
            "full_size": data.get("full_size", 0),
            "total_size_all_variants": total_size,
            "digest": data.get("digest", ""),
            "last_updated": data.get("last_updated", ""),
            "last_updater": data.get("last_updater_username", ""),
            "num_variants": len(images),
            "images": images,
            "tag_status": data.get("tag_status", ""),
            "tag_last_pushed": data.get("tag_last_pushed", "")
        }
        
    except urllib.error.HTTPError as e:
        return {
            "error": f"HTTP Error {e.code}: {e.reason}",
            "image": image_name,
            "tag": tag,
            "hint": "For official images, try 'library/imagename' (e.g., 'library/nginx')"
        }
    except Exception as e:
        return {
            "error": f"Error fetching tag details: {str(e)}",
            "image": image_name,
            "tag": tag
        }


if __name__ == "__main__":
    mcp.run()
