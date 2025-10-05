"""
Flask Application Entry Point

This is the main file that starts the Flask server.
It initializes the Flask app, configures CORS, and registers blueprints.

To run the server:
    python app.py

The server will start at http://localhost:5000

Available endpoints:
    - REST API: http://localhost:5000/posts
    - Health check: http://localhost:5000/health
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from rest_api import rest_api_bp
from strawberry.flask.views import GraphQLView
from graphql_api import schema


def create_app():
    """
    Create and configure the Flask application.

    This function:
    1. Creates Flask app instance
    2. Enables CORS for iOS app connectivity
    3. Registers REST API blueprint
    4. Adds error handlers

    Returns:
        Flask: Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)

    # Enable CORS (Cross-Origin Resource Sharing)
    # This allows the iOS app to make requests to this server
    # In production, you should restrict this to specific origins
    CORS(app, resources={
        r"/*": {
            "origins": "*",  # Allow all origins (change in production)
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register REST API blueprint
    # All routes from rest_api.py will be available
    app.register_blueprint(rest_api_bp)

    # Register GraphQL endpoint
    # GraphQL playground will be available at /graphql in the browser
    # This enables both REST and GraphQL to run simultaneously
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql_view',
            schema=schema,
            graphiql=True  # Enable GraphQL Playground for testing in browser
        )
    )

    # Register Swagger UI
    # Swagger documentation will be available at /api/docs
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Blog REST API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Root endpoint
    @app.route('/')
    def index():
        """
        Root endpoint - API information
        """
        return jsonify({
            'message': 'Blog API Server',
            'version': '1.0.0',
            'endpoints': {
                'posts': '/posts',
                'users': '/users',
                'health': '/health',
                'graphql': '/graphql'
            },
            'documentation': {
                'swagger': 'http://localhost:5001/api/docs',
                'rest_api': {
                    'posts': 'GET /posts?page=1&limit=10&sort=created_at&order=desc&search=keyword',
                    'single_post': 'GET /posts/<id>',
                    'users': 'GET /users',
                    'single_user': 'GET /users/<id>',
                    'user_posts': 'GET /users/<id>/posts?limit=3'
                },
                'graphql': {
                    'endpoint': 'POST /graphql',
                    'playground': 'Visit http://localhost:5001/graphql in browser',
                    'example_query': 'query { posts { data { id, title, author { name } } } }'
                }
            }
        }), 200

    # Error handler for 404 (Not Found)
    @app.errorhandler(404)
    def not_found(error):
        """
        Handle 404 errors with a JSON response
        """
        return jsonify({
            'error': 'Endpoint not found',
            'message': 'The requested URL was not found on the server'
        }), 404

    # Error handler for 500 (Internal Server Error)
    @app.errorhandler(500)
    def internal_error(error):
        """
        Handle 500 errors with a JSON response
        """
        return jsonify({
            'error': 'Internal server error',
            'message': 'Something went wrong on the server'
        }), 500

    return app


# Entry point
if __name__ == '__main__':
    # Create the Flask app
    app = create_app()

    # Print startup information
    print("=" * 70)
    print("Blog API Server - REST + GraphQL")
    print("=" * 70)
    print("\nServer starting...")
    print("\nREST API Endpoints:")
    print("  - Root:        http://localhost:5001/")
    print("  - Posts:       http://localhost:5001/posts")
    print("  - Users:       http://localhost:5001/users")
    print("  - Health:      http://localhost:5001/health")
    print("\nGraphQL Endpoint:")
    print("  - GraphQL:     http://localhost:5001/graphql")
    print("  - Playground:  Open http://localhost:5001/graphql in browser")
    print("\nAPI Documentation:")
    print("  - Swagger UI:  http://localhost:5001/api/docs")
    print("\nPress CTRL+C to stop the server")
    print("=" * 70)
    print()

    # Run the Flask development server
    # debug=True enables auto-reload and better error messages
    # host='0.0.0.0' allows connections from other devices (iOS simulator)
    # port=5001 to avoid conflicts
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5001
    )
