"""
Data Models for Blog System

This module defines the data structures used throughout the blog API.
We use simple dataclasses to represent our database entities.

Why dataclasses?
- Built-in to Python (no external dependencies)
- Automatic __init__, __repr__, and __eq__ methods
- Type hints for better code clarity
- Easy to convert to JSON for API responses
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List


@dataclass
class User:
    """
    User model representing a blog author.

    Attributes:
        id: Unique identifier for the user
        name: User's full name
        email: User's email address
    """
    id: int
    name: str
    email: str

    def to_dict(self) -> dict:
        """
        Convert user object to dictionary for JSON serialization.

        Returns:
            dict: Dictionary representation of the user
        """
        return asdict(self)


@dataclass
class Post:
    """
    Post model representing a blog post.

    Attributes:
        id: Unique identifier for the post
        title: Post title
        content: Post content/body
        author_id: ID of the user who created the post
        created_at: Timestamp when the post was created
        author: User object (optional, populated when joining with users table)
    """
    id: int
    title: str
    content: str
    author_id: int
    created_at: str  # Stored as ISO format string (e.g., "2025-10-03T10:30:00")
    author: Optional[User] = None  # Populated when we join with users table

    def to_dict(self) -> dict:
        """
        Convert post object to dictionary for JSON serialization.

        If the post has author information, it will be included.
        Otherwise, only author_id is included.

        Returns:
            dict: Dictionary representation of the post
        """
        post_dict = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'created_at': self.created_at
        }

        # Include author information if available
        if self.author:
            post_dict['author'] = self.author.to_dict()

        return post_dict


@dataclass
class PaginatedResponse:
    """
    Wrapper for paginated API responses.

    This provides consistent structure for paginated data across all endpoints.

    Attributes:
        data: List of items (posts or users)
        page: Current page number
        limit: Number of items per page
        total: Total number of items available
        total_pages: Total number of pages
    """
    data: List
    page: int
    limit: int
    total: int
    total_pages: int

    def to_dict(self) -> dict:
        """
        Convert paginated response to dictionary.

        Returns:
            dict: Dictionary with pagination metadata and data
        """
        return {
            'data': [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.data],
            'pagination': {
                'page': self.page,
                'limit': self.limit,
                'total': self.total,
                'total_pages': self.total_pages
            }
        }
