# ScraperCreators MCP Server

A FastMCP server for the ScraperCreators platform that provides MCP tools and resources for content scraping operations.

## Project Structure

- `src/mcp_server/` - Core server implementation

  - `main.py` - FastMCP server with tools
  - `cli.py` - CLI utility for version information

- `src/scrapecreator_api/` - ScraperCreators API integration
  - `reddit_search.py` - Reddit Search API client
  - `response_models.py` - Response data models
- `test_server.py` - Direct integration tests
- `run_server.sh` - Script to start the server

## Installation

```bash
# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package and dependencies
pip install -e .
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Usage

### Running the server

The project provides a FastMCP server that can be run using:

```bash
./run_server.sh
```

This uses the FastMCP CLI to run the server with the `stdio` transport.

Alternatively, you can run it directly with:

```bash
# Using Python
python -m src.mcp_server.main

# Using FastMCP CLI
fastmcp run src/mcp_server/main.py:mcp
```

### Reddit Search API

The `RedditSearch` class provides a Python client for the ScrapeCreators Reddit Search API.

#### Basic Usage

```python
from scrapecreator_api.reddit_search import RedditSearch

# Initialize with API key (or set REDDIT_API_KEY in .env.local)
client = RedditSearch(api_key="your_api_key")

# Basic search
results = client.search(query="python programming")

# Search with modifiers
results = client.search(
    query="fastapi tutorial",
    sort="new",
    timeframe="week",
    subreddit="learnpython",
    self=True
)

# Search with pagination and limit
results = client.search_with_pagination(
    query="data science",
    limit=50
)
```

#### Search Parameters

- `query`: Search keywords or phrases
- `sort`: Sort method (`relevance`, `new`, `top`, `comment_count`)
- `timeframe`: Time period (`all`, `day`, `week`, `month`, `year`)
- `after`: Pagination token from previous response
- Modifiers:
  - `author`: Filter by author
  - `subreddit`: Filter by subreddit
  - `title`: Search in titles
  - `selftext`: Search in post content
  - `flair`: Filter by post flair
  - `url`: Search in URLs
  - `self`: Filter self posts (boolean)

#### Search Response Options

The API supports two response modes:

##### Inline Mode

Returns JSON response directly with optional result limiting:

```python
response = client.search(
    query="your query",
    return_mode="inline",
    max_results=10  # Optional limit
)
```

##### File Mode

Saves results to file and returns metadata:

```python
response = client.search(
    query="your query",
    return_mode="file",
    output_dir="/custom/path"  # Optional custom directory
)
```

Both modes return a `SearchResponse` object containing:

- `success`: Boolean indicating success
- `count`: Number of posts found
- `posts`: List of RedditPost objects (inline mode only)
- `file_path`: Path to saved JSON file (file mode only)

#### Error Handling

The client provides custom exceptions for different error scenarios:

- `RedditSearchError`: Base exception class
- `RedditSearchConnectionError`: Connection issues
- `RedditSearchAuthenticationError`: Invalid API key
- `RedditSearchAPIError`: API response errors

### Testing

The recommended way to test the server is through direct integration:

```bash
./test_client.sh
```

This runs a test that imports the MCP instance directly and tests the tools without requiring a separate server process. Based on the FastMCP quickstart guide, this is the most reliable approach for testing.

## Available Tools

- `hello`: Returns a greeting message with the given name

## Notes

- The server instance is named `mcp` in `main.py` to make it easily discoverable by the FastMCP CLI
- For production use, consider using HTTP or other transports instead of stdio
- API keys should be stored in `.env.local` file or provided as environment variables
