"""
Pydantic models for the Reddit Search API response.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class RedditPost(BaseModel):
    """Model representing a single Reddit post."""
    id: str
    subreddit: str
    title: str
    selftext: Optional[str] = None
    author: str
    score: int
    upvote_ratio: float
    num_comments: int
    created_utc: int
    url: str
    permalink: str
    is_self: bool
    is_video: bool
    created_at_iso: str
    
    # Include all other fields as a dict to maintain complete data
    raw_data: Dict[str, Any] = Field(default_factory=dict, exclude=True)
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "RedditPost":
        """Create a RedditPost instance from API response data."""
        # Store complete raw data
        raw_data = data.copy()
        
        # Create instance with required fields
        return cls(
            id=data.get("id", ""),
            subreddit=data.get("subreddit", ""),
            title=data.get("title", ""),
            selftext=data.get("selftext"),
            author=data.get("author", ""),
            score=data.get("score", 0),
            upvote_ratio=data.get("upvote_ratio", 0.0),
            num_comments=data.get("num_comments", 0),
            created_utc=data.get("created_utc", 0),
            url=data.get("url", ""),
            permalink=data.get("permalink", ""),
            is_self=data.get("is_self", False),
            is_video=data.get("is_video", False),
            created_at_iso=datetime.fromtimestamp(data.get("created_utc", 0)).isoformat(),
            raw_data=raw_data
        )


class RedditSearchRawResponse(BaseModel):
    """Model representing the raw API response."""
    data: Dict[str, Any]
    
    model_config = {
        "extra": "allow"  # Allow extra fields in the response
    }


class SearchResponse(BaseModel):
    """Model representing the final search response."""
    success: bool = True
    count: int
    posts: Optional[List[RedditPost]] = None
    file_path: Optional[str] = None 