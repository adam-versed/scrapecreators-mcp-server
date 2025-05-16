"""Unit tests for the RedditSearch class."""

import os
import json
import pytest
import httpx
from unittest.mock import patch, MagicMock
from datetime import datetime
from pathlib import Path

from scrapecreator_api.reddit_search import (
    RedditSearch,
    RedditSearchError,
    RedditSearchConnectionError,
    RedditSearchAuthenticationError,
    RedditSearchAPIError
)

# Sample API response for testing
SAMPLE_POST_DATA = {
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
    "is_video": False
}

SAMPLE_RESPONSE = {
    "data": {
        "children": [
            {"data": SAMPLE_POST_DATA}
        ]
    }
}

class TestRedditSearch:
    """Test cases for the RedditSearch class."""
    
    def test_init_with_explicit_api_key(self):
        """Test initialization with explicit API key."""
        client = RedditSearch(api_key="test_key")
        assert client.api_key == "test_key"
    
    def test_init_with_env_var(self):
        """Test initialization with API key from environment variable."""
        with patch.dict(os.environ, {"REDDIT_API_KEY": "env_key"}):
            client = RedditSearch()
            assert client.api_key == "env_key"
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with patch.dict(os.environ, clear=True):
            with pytest.raises(ValueError):
                RedditSearch()
    
    def test_validate_parameters_valid(self):
        """Test parameter validation with valid parameters."""
        client = RedditSearch(api_key="test_key")
        # Should not raise an exception
        client._validate_parameters(sort="relevance", timeframe="all", return_mode="inline")
    
    def test_validate_parameters_invalid_sort(self):
        """Test parameter validation with invalid sort."""
        client = RedditSearch(api_key="test_key")
        with pytest.raises(ValueError):
            client._validate_parameters(sort="invalid", timeframe="all", return_mode="inline")
    
    def test_validate_parameters_invalid_timeframe(self):
        """Test parameter validation with invalid timeframe."""
        client = RedditSearch(api_key="test_key")
        with pytest.raises(ValueError):
            client._validate_parameters(sort="relevance", timeframe="invalid", return_mode="inline")
            
    def test_validate_parameters_invalid_return_mode(self):
        """Test parameter validation with invalid return mode."""
        client = RedditSearch(api_key="test_key")
        with pytest.raises(ValueError):
            client._validate_parameters(sort="relevance", timeframe="all", return_mode="invalid")
    
    def test_build_query_string_no_modifiers(self):
        """Test query string building without modifiers."""
        client = RedditSearch(api_key="test_key")
        query = client._build_query_string("test query", {})
        assert query == "test query"
    
    def test_build_query_string_with_modifiers(self):
        """Test query string building with modifiers."""
        client = RedditSearch(api_key="test_key")
        query = client._build_query_string(
            "test query",
            {
                "subreddit": "python",
                "title": "help me",
                "self": True
            }
        )
        assert "test query" in query
        assert "subreddit:python" in query
        assert 'title:"help me"' in query
        assert "self:true" in query
        assert " AND " in query
    
    def test_search_success(self):
        """Test search with a successful response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_RESPONSE
    
        with patch("httpx.Client.get", return_value=mock_response):
            client = RedditSearch(api_key="test_key")
            result = client.search(query="test")
            assert result.success is True
            assert result.count == 1
            assert result.posts[0].id == "abc123"
            assert result.posts[0].title == "Test Post"
    
    def test_search_authentication_error(self):
        """Test search with authentication error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Invalid API key"
    
        with patch("httpx.Client.get", return_value=mock_response):
            client = RedditSearch(api_key="test_key")
            with pytest.raises(RedditSearchAuthenticationError):
                client.search(query="test")
    
    def test_search_api_error(self):
        """Test search with API error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
    
        with patch("httpx.Client.get", return_value=mock_response):
            client = RedditSearch(api_key="test_key")
            with pytest.raises(RedditSearchAPIError):
                client.search(query="test")
    
    def test_search_connection_error(self):
        """Test search with connection error."""
        with patch("httpx.Client.get", side_effect=httpx.ConnectError("Failed to connect")):
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
                "children": [
                    {"data": {**SAMPLE_POST_DATA, "id": "1"}},
                    {"data": {**SAMPLE_POST_DATA, "id": "2"}}
                ],
                "after": "t3_next"
            }
        }
    
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "data": {
                "children": [
                    {"data": {**SAMPLE_POST_DATA, "id": "3"}},
                    {"data": {**SAMPLE_POST_DATA, "id": "4"}}
                ],
                "after": None
            }
        }
    
        with patch("httpx.Client.get", side_effect=[mock_response1, mock_response2]):
            client = RedditSearch(api_key="test_key")
            response = client.search(query="test")
            assert response.success is True
            assert response.count == 4
            assert len(response.posts) == 4
            assert response.posts[0].id == "1"
            assert response.posts[3].id == "4"
    
    def test_search_with_pagination_limit(self):
        """Test search with pagination and limit."""
        # Mock responses for pagination
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            "data": {
                "children": [
                    {"data": {**SAMPLE_POST_DATA, "id": "1"}},
                    {"data": {**SAMPLE_POST_DATA, "id": "2"}}
                ],
                "after": "t3_next"
            }
        }
    
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "data": {
                "children": [
                    {"data": {**SAMPLE_POST_DATA, "id": "3"}},
                    {"data": {**SAMPLE_POST_DATA, "id": "4"}}
                ],
                "after": "t3_next2"
            }
        }
    
        with patch("httpx.Client.get", side_effect=[mock_response1, mock_response2]):
            client = RedditSearch(api_key="test_key")
            response = client.search(query="test", max_results=3)
            assert response.success is True
            assert response.count == 3
            assert len(response.posts) == 3
            assert response.posts[0].id == "1"
            assert response.posts[2].id == "3"

@pytest.fixture
def reddit_search():
    """Fixture for RedditSearch instance."""
    return RedditSearch(api_key="test_key")

@pytest.fixture
def mock_response():
    """Fixture for mock response."""
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
        "data": {
            "children": [
                {"data": SAMPLE_POST_DATA},
                {"data": SAMPLE_POST_DATA},
                {"data": SAMPLE_POST_DATA}
            ]
        }
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