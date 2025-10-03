"""
GraphQL API Implementation with Strawberry

This module implements a GraphQL API for the blog system.
It provides the same functionality as the REST API but with GraphQL's advantages:
- Single endpoint for all queries
- Client can request exactly the fields they need
- Nested data in a single request (no N+1 requests)

Technology: Strawberry GraphQL
- Uses Python type hints to define the schema
- Clean, Pythonic syntax
- Automatic schema generation
"""

import strawberry
from typing import List, Optional
from database import (
    get_all_users,
    get_user_by_id,
    get_posts,
    get_user_posts,
    get_post_by_id
)


# GraphQL Types
# These are the data structures that GraphQL clients can query

@strawberry.type
class User:
    """
    GraphQL User type.

    This represents a blog author. Clients can query user information
    and optionally include their posts in a single request.

    Fields:
        id: Unique user identifier
        name: User's full name
        email: User's email address

    Nested queries:
        posts: Get this user's posts (optional, with limit parameter)
    """
    id: int
    name: str
    email: str

    @strawberry.field
    def posts(self, limit: int = 3) -> List['Post']:
        """
        Get posts written by this user.

        This is a resolver function that allows nested queries.
        Example: query { user(id: 1) { name, posts { title } } }

        Args:
            limit: Maximum number of posts to return (default: 3)

        Returns:
            List of Post objects
        """
        # Input validation for nested posts query
        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")

        # Reuse the database function from REST API
        db_posts = get_user_posts(self.id, limit)

        # Convert database Post objects to GraphQL Post types
        return [
            Post(
                id=post.id,
                title=post.title,
                content=post.content,
                author_id=post.author_id,
                created_at=post.created_at
            )
            for post in db_posts
        ]


@strawberry.type
class Post:
    """
    GraphQL Post type.

    This represents a blog post. Clients can query post information
    and optionally include the author details in a single request.

    Fields:
        id: Unique post identifier
        title: Post title
        content: Post content/body
        author_id: ID of the user who wrote this post
        created_at: Timestamp when post was created (ISO format string)

    Nested queries:
        author: Get the author's information (User object)
    """
    id: int
    title: str
    content: str
    author_id: int
    created_at: str

    @strawberry.field
    def author(self) -> Optional[User]:
        """
        Get the author of this post.

        This allows nested queries like:
        query { posts { title, author { name } } }

        Returns:
            User object or None if user not found
        """
        # Fetch user information from database
        db_user = get_user_by_id(self.author_id)

        if db_user:
            return User(
                id=db_user.id,
                name=db_user.name,
                email=db_user.email
            )

        return None


@strawberry.type
class PaginationInfo:
    """
    Pagination metadata for paginated queries.

    This provides information about the current page and total available data.
    It follows the same structure as the REST API for consistency.

    Fields:
        page: Current page number
        limit: Items per page
        total: Total number of items available
        total_pages: Total number of pages
    """
    page: int
    limit: int
    total: int
    total_pages: int


@strawberry.type
class PostsResponse:
    """
    Response type for paginated posts query.

    This wraps the posts data with pagination information.
    Clients can choose to query just the data or include pagination metadata.

    Fields:
        data: List of Post objects
        pagination: Pagination metadata (optional to query)
    """
    data: List[Post]
    pagination: PaginationInfo


# Query Type
# This defines all the read operations available in the GraphQL API

@strawberry.type
class Query:
    """
    Root Query type - defines all available GraphQL queries.

    Available queries:
    - posts: Get paginated list of posts with sorting and search
    - user: Get a single user by ID
    - users: Get all users
    """

    @strawberry.field
    def posts(
        self,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "created_at",
        order: str = "desc",
        search: Optional[str] = None
    ) -> PostsResponse:
        """
        Get a paginated list of blog posts.

        This query supports the same features as the REST API:
        - Pagination: Split results into pages
        - Sorting: Order by created_at or title
        - Search: Filter by keyword in title or content

        Example queries:

        1. Simple query (first page, 10 posts):
           query {
             posts {
               data { id, title }
             }
           }

        2. With pagination:
           query {
             posts(page: 2, limit: 5) {
               data { id, title }
               pagination { total, total_pages }
             }
           }

        3. With search:
           query {
             posts(search: "python") {
               data { title, content }
             }
           }

        4. With nested author:
           query {
             posts {
               data {
                 title
                 author { name, email }
               }
             }
           }

        Args:
            page: Page number (default: 1)
            limit: Posts per page (default: 10)
            sort_by: Column to sort by - "created_at" or "title" (default: "created_at")
            order: Sort order - "asc" or "desc" (default: "desc")
            search: Search keyword for title/content (optional)

        Returns:
            PostsResponse with data and pagination info
        """
        # Input validation
        if page < 1:
            raise ValueError("Page number must be greater than 0")

        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")

        # Validate sort_by field
        allowed_sort_fields = ["created_at", "title", "id"]
        if sort_by not in allowed_sort_fields:
            raise ValueError(f"sortBy must be one of: {', '.join(allowed_sort_fields)}")

        # Validate order field
        if order.lower() not in ["asc", "desc"]:
            raise ValueError("order must be 'asc' or 'desc'")

        # Reuse the database function from REST API
        paginated_response = get_posts(
            page=page,
            limit=limit,
            sort_by=sort_by,
            order=order,
            search=search
        )

        # Convert database Post objects to GraphQL Post types
        posts = [
            Post(
                id=post.id,
                title=post.title,
                content=post.content,
                author_id=post.author_id,
                created_at=post.created_at
            )
            for post in paginated_response.data
        ]

        # Create pagination info
        pagination = PaginationInfo(
            page=paginated_response.page,
            limit=paginated_response.limit,
            total=paginated_response.total,
            total_pages=paginated_response.total_pages
        )

        return PostsResponse(data=posts, pagination=pagination)

    @strawberry.field
    def user(self, id: int) -> Optional[User]:
        """
        Get a single user by ID.

        This supports nested queries to get the user's posts:

        Example queries:

        1. User info only:
           query {
             user(id: 1) {
               name
               email
             }
           }

        2. User with posts (single request, no N+1 problem):
           query {
             user(id: 1) {
               name
               email
               posts(limit: 5) {
                 title
                 created_at
               }
             }
           }

        Args:
            id: User ID to fetch

        Returns:
            User object or None if not found
        """
        db_user = get_user_by_id(id)

        if db_user:
            return User(
                id=db_user.id,
                name=db_user.name,
                email=db_user.email
            )

        return None

    @strawberry.field
    def users(self) -> List[User]:
        """
        Get all users.

        This supports nested queries to get each user's posts.

        Example queries:

        1. All users:
           query {
             users {
               id
               name
             }
           }

        2. All users with their posts (single request, solves N+1 problem):
           query {
             users {
               name
               posts(limit: 3) {
                 title
               }
             }
           }

        Returns:
            List of all User objects
        """
        db_users = get_all_users()

        # Convert database User objects to GraphQL User types
        return [
            User(
                id=user.id,
                name=user.name,
                email=user.email
            )
            for user in db_users
        ]


# Create the GraphQL schema
# This is the main schema object that will be used by Strawberry
schema = strawberry.Schema(query=Query)
