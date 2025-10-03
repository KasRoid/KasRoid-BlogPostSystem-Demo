"""
REST API Blueprint

This module defines all REST API endpoints for the blog system.
Uses Flask Blueprint for modular organization.

Endpoints:
- GET /posts - List all posts (with pagination, sorting, search)
- GET /posts/<id> - Get a single post
- GET /users - List all users
- GET /users/<id> - Get a single user
- GET /users/<id>/posts - Get posts by a specific user

Design principles:
- Consistent JSON response format
- Proper HTTP status codes (200, 404, 400)
- Query parameters for filtering and pagination
- Include helpful error messages
"""

from flask import Blueprint, request, jsonify
from database import get_posts, get_user_by_id, get_user_posts, get_all_users, get_post_by_id


# Create a Blueprint for REST API routes
# This allows us to organize routes separately from the main app
rest_api_bp = Blueprint('rest_api', __name__)


@rest_api_bp.route('/posts', methods=['GET'])
def list_posts():
    """
    GET /posts - Retrieve a list of posts

    Query parameters:
        page (int): Page number (default: 1)
        limit (int): Number of posts per page (default: 10)
        sort (str): Sort field - 'created_at' or 'title' (default: 'created_at')
        order (str): Sort order - 'asc' or 'desc' (default: 'desc')
        search (str): Search keyword for title or content (optional)

    Returns:
        JSON response with posts and pagination metadata

    Example:
        GET /posts?page=1&limit=10&sort=created_at&order=desc
        GET /posts?search=python
    """
    # Extract query parameters with default values
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    sort_by = request.args.get('sort', 'created_at', type=str)
    order = request.args.get('order', 'desc', type=str)
    search = request.args.get('search', None, type=str)

    # Validate pagination parameters
    if page < 1:
        return jsonify({
            'error': 'Page number must be greater than 0'
        }), 400

    if limit < 1 or limit > 100:
        return jsonify({
            'error': 'Limit must be between 1 and 100'
        }), 400

    # Get posts from database
    paginated_response = get_posts(
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order,
        search=search
    )

    # Return JSON response
    return jsonify(paginated_response.to_dict()), 200


@rest_api_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """
    GET /posts/<id> - Retrieve a single post by ID

    Path parameters:
        post_id (int): ID of the post to retrieve

    Returns:
        JSON response with post data

    Example:
        GET /posts/1
    """
    post = get_post_by_id(post_id)

    if not post:
        return jsonify({
            'error': f'Post with ID {post_id} not found'
        }), 404

    return jsonify(post.to_dict()), 200


@rest_api_bp.route('/users', methods=['GET'])
def list_users():
    """
    GET /users - Retrieve a list of all users

    Returns:
        JSON response with array of users

    Example:
        GET /users
    """
    users = get_all_users()

    # Convert User objects to dictionaries
    users_data = [user.to_dict() for user in users]

    return jsonify({
        'data': users_data,
        'total': len(users_data)
    }), 200


@rest_api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    GET /users/<id> - Retrieve a single user by ID

    Path parameters:
        user_id (int): ID of the user to retrieve

    Returns:
        JSON response with user data

    Example:
        GET /users/1
    """
    user = get_user_by_id(user_id)

    if not user:
        return jsonify({
            'error': f'User with ID {user_id} not found'
        }), 404

    return jsonify(user.to_dict()), 200


@rest_api_bp.route('/users/<int:user_id>/posts', methods=['GET'])
def get_user_posts_endpoint(user_id):
    """
    GET /users/<id>/posts - Retrieve posts by a specific user

    Path parameters:
        user_id (int): ID of the user whose posts to retrieve

    Query parameters:
        limit (int): Maximum number of posts to return (default: 3)

    Returns:
        JSON response with array of posts

    Example:
        GET /users/1/posts?limit=3
    """
    # First, verify the user exists
    user = get_user_by_id(user_id)

    if not user:
        return jsonify({
            'error': f'User with ID {user_id} not found'
        }), 404

    # Get limit from query parameters
    limit = request.args.get('limit', 3, type=int)

    # Validate limit
    if limit < 1 or limit > 100:
        return jsonify({
            'error': 'Limit must be between 1 and 100'
        }), 400

    # Get user's posts
    posts = get_user_posts(user_id, limit)

    # Convert Post objects to dictionaries
    posts_data = [post.to_dict() for post in posts]

    return jsonify({
        'user': user.to_dict(),
        'posts': posts_data,
        'total': len(posts_data)
    }), 200


# Health check endpoint
@rest_api_bp.route('/health', methods=['GET'])
def health_check():
    """
    GET /health - Check if the API is running

    This is useful for monitoring and debugging.

    Returns:
        JSON response with status message
    """
    return jsonify({
        'status': 'healthy',
        'message': 'REST API is running'
    }), 200
