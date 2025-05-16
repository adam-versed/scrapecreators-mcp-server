"""
Tests for the RedditSearch class.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from src.scrapecreator_api.reddit_search import (
    RedditSearch,
    RedditSearchError,
    RedditSearchAPIError,
    RedditSearchAuthenticationError,
    RedditSearchConnectionError
)
from datetime import datetime
from pathlib import Path

# Sample API response for testing
SAMPLE_RESPONSE = {
    "success": True,
    "posts": [
        {
            "id": "abc123",
            "subreddit": "test",
            "title": "Test Post",
            "selftext": "Test Content",
            "author": "testuser",
            "score": 42,
            "upvote_ratio": 0.95,
            "num_comments": 10,
            "created_utc": 1234567890,
            "url": "https://reddit.com/r/test/comments/abc123",
            "permalink": "/r/test/comments/abc123",
            "is_self": True,
            "is_video": False,
            "created_at_iso": "2024-03-20T12:34:56.000Z"
        }
    ]
}

class TestRedditSearch:
    """Tests for the RedditSearch class."""

    def test_init_with_explicit_api_key(self):
        """Test initialisation with an explicit API key."""
        client = RedditSearch(api_key="test_key")
        assert client.api_key == "test_key"

    def test_init_with_env_var(self):
        """Test initialisation with an API key from environment variable."""
        with patch.dict(os.environ, {"REDDIT_API_KEY": "env_key"}):
            client = RedditSearch()
            assert client.api_key == "env_key"

    def test_init_without_api_key(self):
        """Test initialisation without an API key."""
        with patch.dict(os.environ, {"REDDIT_API_KEY": ""}, clear=True):
            with pytest.raises(ValueError):
                RedditSearch()

    def test_validate_parameters_valid(self):
        """Test parameter validation with valid parameters."""
        client = RedditSearch(api_key="test_key")
        # Should not raise an exception
        client._validate_parameters(sort="relevance", timeframe="all")

    def test_validate_parameters_invalid_sort(self):
        """Test parameter validation with invalid sort."""
        client = RedditSearch(api_key="test_key")
        with pytest.raises(ValueError):
            client._validate_parameters(sort="invalid", timeframe="all")

    def test_validate_parameters_invalid_timeframe(self):
        """Test parameter validation with invalid timeframe."""
        client = RedditSearch(api_key="test_key")
        with pytest.raises(ValueError):
            client._validate_parameters(sort="relevance", timeframe="invalid")

    def test_build_query_string_no_modifiers(self):
        """Test query string building with no modifiers."""
        client = RedditSearch(api_key="test_key")
        query = client._build_query_string("test query", {})
        assert query == "test query"

    def test_build_query_string_with_modifiers(self):
        """Test query string building with modifiers."""
        client = RedditSearch(api_key="test_key")
        query = client._build_query_string(
            "test query",
            {
                "author": "test_author",
                "subreddit": "test_subreddit",
                "title": "test title",
                "selftext": "test selftext",
                "self": True
            }
        )
        # The order might vary, so we check that each part is present
        assert "test query" in query
        assert "author:test_author" in query
        assert "subreddit:test_subreddit" in query
        assert 'title:"test title"' in query
        assert 'selftext:"test selftext"' in query
        assert "self:true" in query
        assert " AND " in query  # Parts are joined with AND

    def test_search_success(self):
        """Test search with a successful response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"children": []}}

        with patch("httpx.Client.get", return_value=mock_response):
            client = RedditSearch(api_key="test_key")
            result = client.search(query="test")
            assert result == {"data": {"children": []}}

    def test_search_authentication_error(self):
        """Test search with an authentication error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Invalid API key"

        with patch("httpx.Client.get", return_value=mock_response):
            client = RedditSearch(api_key="test_key")
            with pytest.raises(RedditSearchAuthenticationError):
                client.search(query="test")

    def test_search_api_error(self):
        """Test search with an API error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("httpx.Client.get", return_value=mock_response):
            client = RedditSearch(api_key="test_key")
            with pytest.raises(RedditSearchAPIError) as excinfo:
                client.search(query="test")
            assert excinfo.value.status_code == 500
            assert "Internal Server Error" in str(excinfo.value)

    def test_search_connection_error(self):
        """Test search with a connection error."""
        import httpx

        with patch("httpx.Client.get", side_effect=httpx.ConnectError("Connection refused")):
            client = RedditSearch(api_key="test_key")
            with pytest.raises(RedditSearchConnectionError):
                client.search(query="test")

    def test_search_with_pagination(self):
        """Test search with pagination."""
        # Mock responses for pagination
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            "data": {
                "children": [{"id": "1"}, {"id": "2"}],
                "after": "t3_next"
            }
        }

        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "data": {
                "children": [{"id": "3"}, {"id": "4"}],
                "after": None
            }
        }

        with patch("httpx.Client.get", side_effect=[mock_response1, mock_response2]):
            client = RedditSearch(api_key="test_key")
            results = client.search_with_pagination(query="test")
            assert len(results) == 4
            assert results[0]["id"] == "1"
            assert results[3]["id"] == "4"

    def test_search_with_pagination_limit(self):
        """Test search with pagination and limit."""
        # Mock responses for pagination
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            "data": {
                "children": [{"id": "1"}, {"id": "2"}],
                "after": "t3_next"
            }
        }

        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "data": {
                "children": [{"id": "3"}, {"id": "4"}],
                "after": "t3_next2"
            }
        }

        with patch("httpx.Client.get", side_effect=[mock_response1, mock_response2]):
            client = RedditSearch(api_key="test_key")
            results = client.search_with_pagination(query="test", limit=3)
            assert len(results) == 3
            assert results[0]["id"] == "1"
            assert results[2]["id"] == "3"

@pytest.fixture
def reddit_search():
    """Create a RedditSearch instance with a mock API key."""
    with patch.dict(os.environ, {"REDDIT_API_KEY": "test_key"}):
        return RedditSearch()

@pytest.fixture
def mock_response():
    """Create a mock response object."""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = SAMPLE_RESPONSE
    return mock

def test_search_inline_mode(reddit_search, mock_response):
    """Test search with inline response mode."""
    with patch("httpx.Client.get", return_value=mock_response):
        response = reddit_search.search(
            query="test",
            return_mode="inline",
            max_results=1
        )
        
        assert response.success is True
        assert response.count == 1
        assert response.file_path is None
        assert len(response.posts) == 1
        assert response.posts[0].id == "abc123"

def test_search_file_mode(reddit_search, mock_response, tmp_path):
    """Test search with file response mode."""
    with patch("httpx.Client.get", return_value=mock_response):
        response = reddit_search.search(
            query="test",
            return_mode="file",
            output_dir=str(tmp_path)
        )
        
        assert response.success is True
        assert response.count == 1
        assert response.posts is None
        assert response.file_path is not None
        assert os.path.exists(response.file_path)
        
        # Verify file contents
        with open(response.file_path, 'r') as f:
            saved_data = json.load(f)
            assert len(saved_data) == 1
            assert saved_data[0]["id"] == "abc123"

def test_search_with_max_results(reddit_search, mock_response):
    """Test search with max_results limit."""
    # Create response with multiple posts
    multi_response = {
        "success": True,
        "posts": SAMPLE_RESPONSE["posts"] * 3  # 3 copies of the sample post
    }
    mock_response.json.return_value = multi_response
    
    with patch("httpx.Client.get", return_value=mock_response):
        response = reddit_search.search(
            query="test",
            return_mode="inline",
            max_results=2
        )
        
        assert response.success is True
        assert response.count == 2
        assert len(response.posts) == 2

def test_search_invalid_return_mode(reddit_search):
    """Test search with invalid return mode."""
    with pytest.raises(ValueError) as exc_info:
        reddit_search.search(query="test", return_mode="invalid")
    assert "Invalid return mode" in str(exc_info.value)

def test_search_custom_output_dir(reddit_search, mock_response, tmp_path):
    """Test search with custom output directory."""
    custom_dir = tmp_path / "custom_output"
    
    with patch("httpx.Client.get", return_value=mock_response):
        response = reddit_search.search(
            query="test",
            return_mode="file",
            output_dir=str(custom_dir)
        )
        
        assert response.success is True
        assert str(custom_dir) in response.file_path
        assert os.path.exists(response.file_path)

def test_search_file_name_format(reddit_search, mock_response, tmp_path):
    """Test the format of generated result files."""
    with patch("httpx.Client.get", return_value=mock_response):
        response = reddit_search.search(
            query="test query with spaces!",
            return_mode="file",
            output_dir=str(tmp_path)
        )
        
        # Verify filename format
        filename = os.path.basename(response.file_path)
        assert filename.startswith("reddit_search_test_query_with_spaces")
        assert filename.endswith(".json")
        assert "_202" in filename  # Should contain year
        assert len(filename.split("_")) >= 4  # Should have multiple parts 