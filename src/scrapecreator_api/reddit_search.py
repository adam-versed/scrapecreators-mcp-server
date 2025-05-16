"""
ScrapeCreators Reddit Search API Client

This module provides a Python client for the ScrapeCreators Reddit Search API.
"""

import os
import httpx
from typing import Dict, Any, Optional, List, Union
from urllib.parse import quote
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env.local
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env.local')
load_dotenv(dotenv_path=dotenv_path)


class RedditSearchError(Exception):
    """Base exception for all Reddit Search errors."""
    pass


class RedditSearchConnectionError(RedditSearchError):
    """Raised when there is a connection error with the API."""
    pass


class RedditSearchAuthenticationError(RedditSearchError):
    """Raised when there is an authentication error with the API."""
    pass


class RedditSearchAPIError(RedditSearchError):
    """Raised when the API returns an error response."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error (Status {status_code}): {message}")


class RedditSearch:
    """Client for the ScrapeCreators Reddit Search API."""
    
    BASE_URL = "https://api.scrapecreators.com/v1/reddit/search"
    VALID_SORT_OPTIONS = ["relevance", "new", "top", "comment_count"]
    VALID_TIMEFRAME_OPTIONS = ["all", "day", "week", "month", "year"]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise the RedditSearch client.

        Args:
            api_key: The API key for the ScrapeCreators Reddit Search API.
                    If not provided, it will be loaded from the environment
                    variable REDDIT_API_KEY or the .env.local file.
        """
        self.api_key = api_key or os.environ.get("REDDIT_API_KEY")
        
        if not self.api_key:
            raise ValueError("Reddit API key not found. Please set REDDIT_API_KEY environment variable or create a .env.local file.")
        
        self.client = httpx.Client(timeout=30.0)  # 30 second timeout
    
    def __del__(self):
        """Close the HTTP client when the object is destroyed."""
        if hasattr(self, 'client'):
            self.client.close()
    
    def _validate_parameters(self, sort: str, timeframe: str) -> None:
        """
        Validate search parameters.
        
        Args:
            sort: Sort method for results.
            timeframe: Time period for results.
            
        Raises:
            ValueError: If any parameters are invalid.
        """
        if sort not in self.VALID_SORT_OPTIONS:
            raise ValueError(f"Invalid sort option: {sort}. Valid options are: {', '.join(self.VALID_SORT_OPTIONS)}")
        
        if timeframe not in self.VALID_TIMEFRAME_OPTIONS:
            raise ValueError(f"Invalid timeframe option: {timeframe}. Valid options are: {', '.join(self.VALID_TIMEFRAME_OPTIONS)}")
    
    def _build_query_string(self, base_query: str, modifiers: Dict[str, Any]) -> str:
        """
        Build the query string with modifiers.
        
        Args:
            base_query: The base search query.
            modifiers: Dict of modifiers to apply.
            
        Returns:
            The formatted query string.
        """
        # Start with the base query
        if not base_query:
            # If no base query, default to a wildcard search
            query_parts = ["*"]
        else:
            query_parts = [base_query]
        
        # Format modifiers
        for key, value in modifiers.items():
            if key == "title" or key == "selftext":
                # Quotes around text for title and selftext
                formatted = f'{key}:"{value}"'
            elif key == "self":
                # Boolean values as lowercase strings
                formatted = f'{key}:{str(value).lower()}'
            else:
                formatted = f'{key}:{value}'
            
            query_parts.append(formatted)
        
        # Join with AND according to documentation best practices
        return " AND ".join(query_parts)
    
    def search(self, 
               query: str = "", 
               sort: str = "relevance", 
               timeframe: str = "all", 
               after: Optional[str] = None, 
               **modifiers) -> Dict[str, Any]:
        """
        Perform a search on the ScrapeCreators Reddit Search API.
        
        Args:
            query: The search keywords or phrases.
            sort: Sort method for results (relevance, new, top, comment_count).
            timeframe: Time period for results (all, day, week, month, year).
            after: Token for pagination, retrieved from a previous response.
            **modifiers: Supported search modifiers (e.g., author, subreddit, title, selftext, flair, url, self).
        
        Returns:
            A dictionary containing the search results.
            
        Raises:
            RedditSearchConnectionError: If there is a connection error.
            RedditSearchAuthenticationError: If the API key is invalid.
            RedditSearchAPIError: If the API returns an error response.
            ValueError: If any parameters are invalid.
        """
        self._validate_parameters(sort, timeframe)
        
        # Build the query string
        formatted_query = self._build_query_string(query, modifiers)
        
        # Set up request parameters
        params = {
            "query": formatted_query,
            "sort": sort,
            "timeframe": timeframe
        }
        
        # Add after parameter for pagination if provided
        if after:
            params["after"] = after
        
        # Ensure headers contain only string values to avoid type errors
        headers: Dict[str, str] = {"x-api-key": str(self.api_key)}
        
        logger.debug(f"Performing Reddit search with params: {params}")
        
        try:
            response = self.client.get(self.BASE_URL, params=params, headers=headers)
            
            # Handle HTTP errors
            if response.status_code == 401:
                raise RedditSearchAuthenticationError("Invalid API key")
            
            if response.status_code != 200:
                raise RedditSearchAPIError(
                    status_code=response.status_code,
                    message=response.text
                )
            
            return response.json()
            
        except httpx.ConnectError as e:
            raise RedditSearchConnectionError(f"Failed to connect to the API: {str(e)}")
        except httpx.RequestError as e:
            raise RedditSearchConnectionError(f"Request error: {str(e)}")
        except (RedditSearchAuthenticationError, RedditSearchAPIError):
            # Re-raise these specific exceptions without wrapping them
            raise
        except Exception as e:
            # Re-raise any other exceptions
            raise RedditSearchError(f"An unexpected error occurred: {str(e)}")
    
    def search_with_pagination(self, 
                              query: str = "", 
                              sort: str = "relevance", 
                              timeframe: str = "all", 
                              limit: Optional[int] = None, 
                              **modifiers) -> List[Dict[str, Any]]:
        """
        Perform a search with automatic pagination.
        
        Args:
            query: The search keywords or phrases.
            sort: Sort method for results.
            timeframe: Time period for results.
            limit: Maximum number of results to return. If None, returns all available results.
            **modifiers: Search modifiers.
            
        Returns:
            A list of Reddit post results.
        """
        all_results = []
        after = None
        total_fetched = 0
        
        while True:
            # Perform the search
            response = self.search(
                query=query, 
                sort=sort, 
                timeframe=timeframe, 
                after=after, 
                **modifiers
            )
            
            # Extract the posts from the response
            # Adjust this based on the actual API response structure
            data = response.get("data", {})
            posts = data.get("children", [])
            
            # Add the posts to our results
            all_results.extend(posts)
            total_fetched += len(posts)
            
            # Check if we've reached the limit
            if limit and total_fetched >= limit:
                all_results = all_results[:limit]  # Trim to the exact limit
                break
            
            # Get the 'after' token for the next page
            after = data.get("after")
            
            # If there's no after token or no posts were returned, we've reached the end
            if not after or not posts:
                break
        
        return all_results 