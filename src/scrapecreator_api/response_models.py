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
    raw_data: Dict[str, Any] = Field(exclude=True)
    
    def __init__(self, **data):
        # Store complete raw data before processing
        raw_data = data.copy()
        super().__init__(**data, raw_data=raw_data)


class RedditSearchListingData(BaseModel):
    """Model representing the data field in the response."""
    children: List[RedditPost]
    after: Optional[str] = None


class RedditSearchRawResponse(BaseModel):
    """Model representing the complete API response."""
    success: bool
    posts: List[RedditPost]


class SearchResponse(BaseModel):
    """Model representing our standardized search response."""
    count: int
    posts: Optional[List[RedditPost]] = None
    file_path: Optional[str] = None
    success: bool = True
    error: Optional[str] = None 