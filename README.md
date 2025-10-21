# Simple MCP Workshop - Docker Hub Edition

A hands-on workshop for learning how to build MCP (Model Context Protocol) servers using FastMCP and Python. This workshop progressively builds a Docker Hub query tool that can be used by AI assistants like Claude.

[Link to Slide Deck](https://docs.google.com/presentation/d/e/2PACX-1vSuoHZiHVuxL77tlP5_q9EkEnDnuQHx6DE3ta7R_PepD2bTDZlq5d_a1zoupYxomR5_6SK4hCIN82gA/pub?start=false&loop=false&delayms=3000)

## What You'll Build

An MCP server that allows AI assistants to:
- Search for Docker images on Docker Hub
- Get detailed information about images
- Compare image statistics (pulls, stars)
- Filter by official vs. community images

## Workshop Stages

This workshop is organized into progressive stages, represented as tags/branches in this repo. It is recommended 
to work through the branches in order, ensuring that the MCP server compiles and can be successfully be used before 
moving to the next stage:

### Stage 1: Basic MCP Server (`stage-1` tag/branch)
**Concepts:** MCP basics, tool definition, simple responses

- Set up Python project with uv
- Create basic MCP server with FastMCP
- Implement a simple `greet` tool
- Connect to Claude Desktop

**What you'll learn:**
- MCP server structure
- Tool decorators
- Basic parameter handling

### Stage 2: Docker Hub Search (`stage-2` tag/branch)
**Concepts:** HTTP requests, API integration, pagination

- Add `search_images` tool
- Query Docker Hub API
- Handle pagination
- Distinguish official vs. community images

**What you'll learn:**
- Making HTTP GET requests
- Parsing JSON responses
- Query parameter handling
- Data transformation

### Stage 3: Image Details (Coming Soon - `stage-3` tag/branch)
**Concepts:** Detailed queries, nested data

- Add `get_image_details` tool
- Fetch image tags and metadata
- Handle image namespaces

### Stage 4: Comparison Tools (Coming Soon - `stage-4` tag/branch)
**Concepts:** Multi-source queries, data analysis

- Add `compare_images` tool
- Aggregate statistics
- Provide recommendations

## Prerequisites

- **Python 3.10+**
- **uv** package manager - [Install uv](https://docs.astral.sh/uv/)
- **Claude Desktop** (or another MCP-compatible client)

## Quick Start

### 1. Clone and Install
```bash
git clone <your-repo-url>
cd simple-mcp-workshop
uv sync
```

### 2. Choose Your Starting Point

Start from scratch:
```bash
git checkout stage-1
```

Or jump to a specific stage:
```bash
git checkout stage-2  # Docker Hub search
```

### 3. Configure Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
```json
{
  "mcpServers": {
    "simple-workshop": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/simple-mcp-workshop",
        "run",
        "simple-mcp"
      ]
    }
  }
}
```

Replace `/ABSOLUTE/PATH/TO/simple-mcp-workshop` with your actual path.

### 4. Restart Claude Desktop

Quit and reopen Claude Desktop to load the MCP server.

### 5. Test It!

In Claude Desktop, try:
- **Stage 1:** "Can you greet me?"
- **Stage 2:** "Search Docker Hub for nginx images"
- **Stage 3:** "Get details about specific container images"
- **Stage 4:** "Compare image x with image y to recommend which one I should use in this context"

## Project Structure
```
simple-mcp-workshop/
├── .gitignore
├── README.md              # This file
├── pyproject.toml         # Python project configuration
├── uv.lock               # Dependency lock file
└── src/
    └── simple_mcp/
        ├── __init__.py
        └── server.py      # MCP server implementation
```

## Available Tools

### Stage 1
- **greet(name: str)** - Simple greeting tool for testing

### Stage 2+
- **search_images(query: str, page: int, page_size: int)** - Search Docker Hub
  - Returns image name, description, stars, pulls
  - Handles pagination
  - Marks official images

### Stage 3+
- **get_image_details(image_name: str)** - Get detailed image info
- **list_image_tags(image_name: str)** - List available tags

### Stage 4+
- **compare_images(image_names: list[str])** - Compare multiple images

## Navigating Between Stages
```bash
# See all stages
git tag

# Switch to a stage
git checkout stage-1
git checkout stage-2

# Create a new branch from a stage
git checkout stage-2
git checkout -b my-experiments
```

## Workshop Flow

1. **Start at Stage 1** - Understand MCP basics
2. **Progress through stages** - Each adds new concepts
3. **Experiment** - Create your own branch and try modifications
4. **Reference previous stages** - Checkout tags if you get stuck

## Testing Your Server

### Method 1: Through Claude Desktop
The easiest way - just ask Claude to use your tools!

### Method 2: Direct Python Testing
```bash
uv run python -c "from simple_mcp.server import search_images; print(search_images('nginx', 1, 10))"
```

### Method 3: MCP Inspector
Use the official MCP Inspector tool to debug your server.

## Common Issues

### "Command not found: simple-mcp"
Make sure you've run `uv sync` to install dependencies.

### Claude Desktop not seeing the server
1. Check the config path is absolute (not relative)
2. Restart Claude Desktop completely
3. Check Claude Desktop logs for errors

### Import errors
Make sure you're in the project root and have run `uv sync`.

## Learning Objectives

By completing this workshop, you'll understand:
- ✅ How MCP servers work
- ✅ Tool definition and parameter handling
- ✅ Making HTTP requests from MCP tools
- ✅ Parsing and transforming API responses
- ✅ Handling pagination and filtering
- ✅ Connecting MCP servers to AI assistants

## Next Steps After the Workshop

- **Add authentication** - Use Docker Hub personal access tokens
- **Add more APIs** - GitHub, npm, PyPI
- **Add resources** - Expose configuration or data
- **Add prompts** - Pre-built conversation starters
- **Deploy** - Package and share your server

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Docker Hub API Docs](https://docs.docker.com/docker-hub/api/latest/)
- [Anthropic MCP Documentation](https://docs.claude.com/en/docs/mcp)

## Contributing

Found an issue or want to improve the workshop?
- Open an issue
- Submit a pull request
- Suggest new stages or features

## License

MIT License - Feel free to use for learning and teaching!

---

**Happy Building! 🚀**

Questions? Check the git tags, each stage is fully working and documented.