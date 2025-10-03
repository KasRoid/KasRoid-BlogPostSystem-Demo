"""
Database Helper Functions

This module provides functions to interact with the SQLite database.
All database queries are centralized here for easy maintenance.

Design principles:
- Each function has a single, clear purpose
- Functions return Python objects (User, Post) instead of raw database rows
- SQL queries are readable and well-commented
- Proper error handling for database operations
"""

import sqlite3
from typing import List, Optional, Tuple
from models import User, Post, PaginatedResponse
import math


# Database file name
DATABASE_NAME = 'blog.db'


def get_db_connection():
    """
    Create and return a database connection.

    The connection is configured to return rows as sqlite3.Row objects,
    which allows us to access columns by name (like row['id']).

    Returns:
        sqlite3.Connection: Database connection object
    """
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row  # Enable column access by name
    return connection


def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Retrieve a user by their ID.

    Args:
        user_id: The ID of the user to retrieve

    Returns:
        User object if found, None otherwise
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        'SELECT id, name, email FROM users WHERE id = ?',
        (user_id,)
    )

    row = cursor.fetchone()
    connection.close()

    if row:
        return User(
            id=row['id'],
            name=row['name'],
            email=row['email']
        )

    return None


def get_all_users() -> List[User]:
    """
    Retrieve all users from the database.

    Returns:
        List of User objects
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT id, name, email FROM users ORDER BY id')

    rows = cursor.fetchall()
    connection.close()

    users = [
        User(id=row['id'], name=row['name'], email=row['email'])
        for row in rows
    ]

    return users


def get_posts(
    page: int = 1,
    limit: int = 10,
    sort_by: str = 'created_at',
    order: str = 'desc',
    search: Optional[str] = None
) -> PaginatedResponse:
    """
    Retrieve posts with pagination, sorting, and search capabilities.

    This is the main function for fetching posts. It supports:
    - Pagination: Split results into pages
    - Sorting: Order by any column (usually created_at)
    - Search: Filter by keyword in title or content

    Args:
        page: Page number (1-indexed)
        limit: Number of posts per page
        sort_by: Column to sort by ('created_at' or 'title')
        order: Sort order ('asc' or 'desc')
        search: Optional search keyword

    Returns:
        PaginatedResponse containing posts and pagination metadata
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    # Build the WHERE clause for search
    where_clause = ""
    params = []

    if search:
        where_clause = "WHERE posts.title LIKE ? OR posts.content LIKE ?"
        search_pattern = f'%{search}%'
        params = [search_pattern, search_pattern]

    # Validate sort column to prevent SQL injection
    allowed_sort_columns = ['created_at', 'title', 'id']
    if sort_by not in allowed_sort_columns:
        sort_by = 'created_at'

    # Validate sort order
    order = 'DESC' if order.lower() == 'desc' else 'ASC'

    # Count total posts (for pagination metadata)
    count_query = f'SELECT COUNT(*) FROM posts {where_clause}'
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    # Calculate pagination values
    total_pages = math.ceil(total / limit) if total > 0 else 0
    offset = (page - 1) * limit

    # Build the main query with JOIN to include author information
    query = f'''
        SELECT
            posts.id,
            posts.title,
            posts.content,
            posts.author_id,
            posts.created_at,
            users.id as user_id,
            users.name as user_name,
            users.email as user_email
        FROM posts
        JOIN users ON posts.author_id = users.id
        {where_clause}
        ORDER BY posts.{sort_by} {order}
        LIMIT ? OFFSET ?
    '''

    # Add limit and offset to params
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    connection.close()

    # Convert database rows to Post objects with author information
    posts = []
    for row in rows:
        author = User(
            id=row['user_id'],
            name=row['user_name'],
            email=row['user_email']
        )

        post = Post(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            author_id=row['author_id'],
            created_at=row['created_at'],
            author=author
        )

        posts.append(post)

    return PaginatedResponse(
        data=posts,
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages
    )


def get_user_posts(user_id: int, limit: int = 3) -> List[Post]:
    """
    Retrieve posts by a specific user.

    This function is used to get a user's recent posts.
    It includes author information in the response.

    Args:
        user_id: ID of the user whose posts to retrieve
        limit: Maximum number of posts to return (default: 3)

    Returns:
        List of Post objects
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    query = '''
        SELECT
            posts.id,
            posts.title,
            posts.content,
            posts.author_id,
            posts.created_at,
            users.id as user_id,
            users.name as user_name,
            users.email as user_email
        FROM posts
        JOIN users ON posts.author_id = users.id
        WHERE posts.author_id = ?
        ORDER BY posts.created_at DESC
        LIMIT ?
    '''

    cursor.execute(query, (user_id, limit))
    rows = cursor.fetchall()
    connection.close()

    # Convert rows to Post objects
    posts = []
    for row in rows:
        author = User(
            id=row['user_id'],
            name=row['user_name'],
            email=row['user_email']
        )

        post = Post(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            author_id=row['author_id'],
            created_at=row['created_at'],
            author=author
        )

        posts.append(post)

    return posts


def get_post_by_id(post_id: int) -> Optional[Post]:
    """
    Retrieve a single post by its ID.

    Args:
        post_id: ID of the post to retrieve

    Returns:
        Post object if found, None otherwise
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    query = '''
        SELECT
            posts.id,
            posts.title,
            posts.content,
            posts.author_id,
            posts.created_at,
            users.id as user_id,
            users.name as user_name,
            users.email as user_email
        FROM posts
        JOIN users ON posts.author_id = users.id
        WHERE posts.id = ?
    '''

    cursor.execute(query, (post_id,))
    row = cursor.fetchone()
    connection.close()

    if row:
        author = User(
            id=row['user_id'],
            name=row['user_name'],
            email=row['user_email']
        )

        return Post(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            author_id=row['author_id'],
            created_at=row['created_at'],
            author=author
        )

    return None
