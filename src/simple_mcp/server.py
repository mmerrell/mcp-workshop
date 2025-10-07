"""Simple MCP server with Docker Hub search functionality."""

import urllib.request
import urllib.parse
import json
from typing import Any
from datetime import datetime
from functools import lru_cache
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
    base_url = "https://hub.docker.com/v2/search/repositories/"

    params = {
        "query": query,
        "page": page,
        "page_size": min(page_size, 100)
    }

    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        results = []
        for item in data.get("results", []):
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


# Cache tag details for 5 minutes (images don't change often)
@lru_cache(maxsize=100)
def _fetch_tag_details_cached(image_name: str, tag: str) -> str:
    """Internal cached function to fetch tag details.

    Returns JSON string to be cache-friendly.
    """
    # For official images, prepend "library/" if not present
    if "/" not in image_name and image_name in ["nginx", "python", "redis", "ubuntu", "postgres", "mysql", "node", "alpine"]:
        image_name = f"library/{image_name}"

    url = f"https://hub.docker.com/v2/repositories/{image_name}/tags/{tag}"

    with urllib.request.urlopen(url) as response:
        return response.read().decode()


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
    # Normalize image name for caching
    if "/" not in image_name and image_name in ["nginx", "python", "redis", "ubuntu", "postgres", "mysql", "node", "alpine"]:
        normalized_name = f"library/{image_name}"
    else:
        normalized_name = image_name

    try:
        # Use cached function
        json_data = _fetch_tag_details_cached(normalized_name, tag)
        data = json.loads(json_data)

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
            "image": normalized_name,
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
        if e.code == 404:
            return {
                "error": f"Tag '{tag}' not found for image '{image_name}'",
                "image": image_name,
                "tag": tag,
                "hint": "Use get_image_tags to see available tags. For official images, the image name should not include 'library/' prefix when calling this tool.",
                "suggestion": f"Try: get_image_tags('{image_name}') to see all available tags"
            }
        return {
            "error": f"HTTP Error {e.code}: {e.reason}",
            "image": image_name,
            "tag": tag,
            "hint": "For official images, try without the 'library/' prefix (e.g., 'nginx' not 'library/nginx')"
        }
    except Exception as e:
        return {
            "error": f"Error fetching tag details: {str(e)}",
            "image": image_name,
            "tag": tag
        }


@mcp.tool()
def compare_tags(image_name: str, tag1: str, tag2: str) -> dict[str, Any]:
    """Compare two tags of the same image side-by-side.

    This tool fetches details for both tags and provides a comprehensive comparison
    including size differences, architecture changes, and update timeline.

    Args:
        image_name: Name of the image (e.g., "nginx", "python")
        tag1: First tag to compare (e.g., "latest")
        tag2: Second tag to compare (e.g., "alpine")

    Returns:
        Dictionary containing detailed comparison including:
        - Size differences (total and per-architecture)
        - Architecture availability changes
        - Update timeline
        - Digest differences
    """
    # Fetch both tags
    details1 = get_tag_details(image_name, tag1)
    details2 = get_tag_details(image_name, tag2)

    # Check for errors
    if "error" in details1:
        return {
            "error": f"Failed to fetch tag '{tag1}': {details1['error']}",
            "hint": details1.get("hint", ""),
            "suggestion": details1.get("suggestion", "")
        }

    if "error" in details2:
        return {
            "error": f"Failed to fetch tag '{tag2}': {details2['error']}",
            "hint": details2.get("hint", ""),
            "suggestion": details2.get("suggestion", "")
        }

    # Compare sizes
    size1 = details1.get("full_size", 0)
    size2 = details2.get("full_size", 0)
    size_diff = size2 - size1
    size_diff_percent = (size_diff / size1 * 100) if size1 > 0 else 0

    # Compare architectures
    archs1 = {img["architecture"] for img in details1.get("images", []) if img["architecture"] != "unknown"}
    archs2 = {img["architecture"] for img in details2.get("images", []) if img["architecture"] != "unknown"}

    common_archs = archs1 & archs2
    only_in_tag1 = archs1 - archs2
    only_in_tag2 = archs2 - archs1

    # Compare sizes per architecture
    arch_size_comparison = []
    for arch in common_archs:
        img1 = next((img for img in details1["images"] if img["architecture"] == arch), None)
        img2 = next((img for img in details2["images"] if img["architecture"] == arch), None)

        if img1 and img2:
            size_diff_arch = img2["size"] - img1["size"]
            size_diff_percent_arch = (size_diff_arch / img1["size"] * 100) if img1["size"] > 0 else 0

            arch_size_comparison.append({
                "architecture": arch,
                f"{tag1}_size": img1["size"],
                f"{tag2}_size": img2["size"],
                "size_difference": size_diff_arch,
                "size_difference_percent": round(size_diff_percent_arch, 2),
                "size_change": "increased" if size_diff_arch > 0 else "decreased" if size_diff_arch < 0 else "no change"
            })

    # Parse update times
    def parse_time(time_str):
        try:
            # Handle both formats: with and without microseconds
            if '.' in time_str:
                return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            else:
                return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except:
            return None

    time1 = parse_time(details1.get("last_updated", ""))
    time2 = parse_time(details2.get("last_updated", ""))

    time_comparison = {}
    if time1 and time2:
        time_diff = abs((time2 - time1).total_seconds())
        days_diff = time_diff / 86400

        time_comparison = {
            f"{tag1}_updated": details1.get("last_updated", ""),
            f"{tag2}_updated": details2.get("last_updated", ""),
            "days_between_updates": round(days_diff, 2),
            "newer_tag": tag2 if time2 > time1 else tag1
        }

    return {
        "image": details1.get("image", image_name),
        "comparison": {
            "tag1": tag1,
            "tag2": tag2
        },
        "size_comparison": {
            f"{tag1}_size": size1,
            f"{tag2}_size": size2,
            "size_difference": size_diff,
            "size_difference_percent": round(size_diff_percent, 2),
            "size_change": "increased" if size_diff > 0 else "decreased" if size_diff < 0 else "no change",
            f"{tag1}_total_all_variants": details1.get("total_size_all_variants", 0),
            f"{tag2}_total_all_variants": details2.get("total_size_all_variants", 0)
        },
        "architecture_comparison": {
            "common_architectures": sorted(list(common_archs)),
            f"only_in_{tag1}": sorted(list(only_in_tag1)),
            f"only_in_{tag2}": sorted(list(only_in_tag2)),
            "per_architecture_sizes": arch_size_comparison
        },
        "time_comparison": time_comparison,
        "digest_comparison": {
            f"{tag1}_digest": details1.get("digest", ""),
            f"{tag2}_digest": details2.get("digest", ""),
            "digests_match": details1.get("digest") == details2.get("digest")
        },
        "variant_count": {
            f"{tag1}_variants": details1.get("num_variants", 0),
            f"{tag2}_variants": details2.get("num_variants", 0)
        }
    }


@mcp.tool()
def analyze_image_layers(image_name: str, tag: str = "latest") -> dict[str, Any]:
    """Analyze the layers and composition of a Docker image.

    This tool provides insights into what makes up an image, including
    layer sizes, architecture-specific details, and patterns that might
    indicate the base image or build process.

    Args:
        image_name: Name of the image (e.g., "nginx", "python")
        tag: Tag to analyze (default: "latest")

    Returns:
        Dictionary containing layer analysis including:
        - Layer count and size distribution
        - Architecture breakdown
        - Size efficiency metrics
        - Base image detection hints
    """
    # Get tag details
    details = get_tag_details(image_name, tag)

    # Check for errors
    if "error" in details:
        return {
            "error": f"Failed to fetch tag details: {details['error']}",
            "hint": details.get("hint", ""),
            "suggestion": details.get("suggestion", "")
        }

    images = details.get("images", [])

    # Filter out unknown architectures
    real_images = [img for img in images if img["architecture"] != "unknown"]
    manifest_images = [img for img in images if img["architecture"] == "unknown"]

    # Analyze architecture distribution
    arch_analysis = []
    for img in real_images:
        arch_info = {
            "architecture": img["architecture"],
            "os": img["os"],
            "size_bytes": img["size"],
            "size_mb": round(img["size"] / (1024 * 1024), 2),
            "digest": img["digest"],
            "last_pushed": img["last_pushed"]
        }

        if img.get("variant"):
            arch_info["variant"] = img["variant"]
            arch_info["full_platform"] = f"{img['os']}/{img['architecture']}/{img['variant']}"
        else:
            arch_info["full_platform"] = f"{img['os']}/{img['architecture']}"

        arch_analysis.append(arch_info)

    # Sort by size
    arch_analysis.sort(key=lambda x: x["size_bytes"], reverse=True)

    # Calculate statistics
    sizes = [img["size_bytes"] for img in real_images]
    avg_size = sum(sizes) / len(sizes) if sizes else 0
    min_size = min(sizes) if sizes else 0
    max_size = max(sizes) if sizes else 0

    # Identify the smallest image (often alpine-based or distroless)
    smallest_arch = min(real_images, key=lambda x: x["size"], default=None)
    largest_arch = max(real_images, key=lambda x: x["size"], default=None)

    # Detect base image hints
    base_image_hints = []

    # Alpine detection (usually smallest)
    if smallest_arch and smallest_arch["size"] < avg_size * 0.7:
        base_image_hints.append({
            "hint": "possibly_alpine_based",
            "reason": f"Smallest variant ({smallest_arch['architecture']}) is significantly smaller than average",
            "architecture": smallest_arch["architecture"],
            "size_mb": round(smallest_arch["size"] / (1024 * 1024), 2)
        })

    # Check if tag name suggests base image
    tag_lower = tag.lower()
    if "alpine" in tag_lower:
        base_image_hints.append({
            "hint": "alpine_base_confirmed",
            "reason": "Tag name contains 'alpine'",
            "tag": tag
        })
    elif "slim" in tag_lower:
        base_image_hints.append({
            "hint": "debian_slim_likely",
            "reason": "Tag name contains 'slim' (usually Debian slim variant)",
            "tag": tag
        })
    elif "bookworm" in tag_lower or "bullseye" in tag_lower or "buster" in tag_lower:
        base_image_hints.append({
            "hint": "debian_based",
            "reason": f"Tag name contains Debian version codename",
            "tag": tag
        })

    # Size efficiency analysis
    size_range = max_size - min_size
    size_variance_percent = (size_range / avg_size * 100) if avg_size > 0 else 0

    efficiency = {
        "smallest_variant_mb": round(min_size / (1024 * 1024), 2),
        "largest_variant_mb": round(max_size / (1024 * 1024), 2),
        "average_variant_mb": round(avg_size / (1024 * 1024), 2),
        "size_variance_percent": round(size_variance_percent, 2),
        "size_consistency": "high" if size_variance_percent < 20 else "medium" if size_variance_percent < 50 else "variable"
    }

    return {
        "image": details.get("image", image_name),
        "tag": tag,
        "summary": {
            "total_variants": len(real_images),
            "manifest_entries": len(manifest_images),
            "architectures_supported": len(set(img["architecture"] for img in real_images)),
            "total_size_all_variants_mb": round(details.get("total_size_all_variants", 0) / (1024 * 1024), 2),
            "primary_size_mb": round(details.get("full_size", 0) / (1024 * 1024), 2)
        },
        "architecture_breakdown": arch_analysis,
        "size_efficiency": efficiency,
        "base_image_hints": base_image_hints,
        "smallest_variant": {
            "architecture": smallest_arch["architecture"] if smallest_arch else None,
            "size_mb": round(smallest_arch["size"] / (1024 * 1024), 2) if smallest_arch else None
        },
        "largest_variant": {
            "architecture": largest_arch["architecture"] if largest_arch else None,
            "size_mb": round(largest_arch["size"] / (1024 * 1024), 2) if largest_arch else None
        },
        "last_updated": details.get("last_updated", ""),
        "digest": details.get("digest", "")
    }


if __name__ == "__main__":
    mcp.run()