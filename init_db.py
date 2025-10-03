"""
Database Initialization Script

This script creates and initializes the SQLite database for the blog system.
It creates two tables (users and posts) and populates them with sample data.

Usage:
    python init_db.py

This script can be run multiple times safely - it will drop existing tables
and recreate them with fresh sample data.
"""

import sqlite3
from datetime import datetime, timedelta
import random


# Database file name
DATABASE_NAME = 'blog.db'


def create_database():
    """
    Create SQLite database connection and return it.

    Returns:
        sqlite3.Connection: Database connection object
    """
    connection = sqlite3.connect(DATABASE_NAME)
    print(f"✓ Connected to database: {DATABASE_NAME}")
    return connection


def create_tables(connection):
    """
    Create users and posts tables in the database.

    If tables already exist, they will be dropped and recreated.
    This allows the script to be run multiple times safely.

    Args:
        connection: SQLite database connection
    """
    cursor = connection.cursor()

    # Drop existing tables if they exist (allows script re-running)
    cursor.execute('DROP TABLE IF EXISTS posts')
    cursor.execute('DROP TABLE IF EXISTS users')
    print("✓ Dropped existing tables (if any)")

    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    print("✓ Created 'users' table")

    # Create posts table with foreign key to users
    cursor.execute('''
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (author_id) REFERENCES users (id)
        )
    ''')
    print("✓ Created 'posts' table")

    connection.commit()


def seed_users(connection):
    """
    Insert sample user data into the users table.

    Creates 3 users with realistic names and emails.

    Args:
        connection: SQLite database connection

    Returns:
        list: List of user IDs that were created
    """
    cursor = connection.cursor()

    # Sample user data - realistic names and email addresses
    users_data = [
        ('Alice Johnson', 'alice.johnson@example.com'),
        ('Bob Smith', 'bob.smith@example.com'),
        ('Charlie Brown', 'charlie.brown@example.com'),
    ]

    # Insert users and collect their IDs
    user_ids = []
    for name, email in users_data:
        cursor.execute(
            'INSERT INTO users (name, email) VALUES (?, ?)',
            (name, email)
        )
        user_ids.append(cursor.lastrowid)

    connection.commit()
    print(f"✓ Inserted {len(users_data)} users into database")

    return user_ids


def seed_posts(connection, user_ids):
    """
    Insert sample blog post data into the posts table.

    Creates 5 posts for each user (15 total) with varied timestamps.
    Some posts are recent, others are older to simulate a real blog.

    Args:
        connection: SQLite database connection
        user_ids: List of user IDs to assign as post authors
    """
    cursor = connection.cursor()

    # Sample blog post titles - realistic tech blog topics
    post_titles = [
        'Getting Started with Python Web Development',
        'Understanding REST API Design Principles',
        'Introduction to GraphQL: A Modern Approach',
        'Building Scalable Backend Systems',
        'Database Design Best Practices',
        'Mastering SQL Queries for Beginners',
        'Why Flask is Great for Small Projects',
        'Comparing REST and GraphQL APIs',
        'Clean Code Principles Every Developer Should Know',
        'How to Structure Your Python Projects',
        'Understanding Database Relationships',
        'Building Your First API with Flask',
        'GraphQL vs REST: Which Should You Choose?',
        'Essential Python Libraries for Backend Development',
        'Introduction to SQLite for Beginners',
    ]

    # Sample post content - realistic blog post excerpts
    post_contents = [
        'Python has become one of the most popular languages for web development. In this post, we explore the fundamentals of building web applications using Python frameworks like Flask and Django.',
        'REST (Representational State Transfer) is an architectural style for designing networked applications. This article covers the core principles and best practices for creating RESTful APIs.',
        'GraphQL is a query language for APIs that gives clients the power to ask for exactly what they need. Learn how GraphQL solves common problems faced by REST APIs.',
        'As your application grows, scalability becomes crucial. This guide covers essential patterns and practices for building backend systems that can handle increasing loads.',
        'Good database design is the foundation of any successful application. We discuss normalization, relationships, and how to create efficient database schemas.',
        'SQL is a powerful language for working with relational databases. This tutorial covers essential queries, joins, and optimization techniques for beginners.',
        'Flask is a lightweight Python framework perfect for small to medium projects. Discover why Flask\'s simplicity makes it an excellent choice for learning and prototyping.',
        'Both REST and GraphQL have their strengths and weaknesses. This comprehensive comparison helps you understand when to use each approach in your projects.',
        'Writing clean, maintainable code is essential for long-term success. Learn the fundamental principles that will make your code easier to read and maintain.',
        'Organizing your Python project properly from the start saves time and headaches later. This guide shows you how to structure projects for maximum maintainability.',
        'Relationships between data are at the heart of relational databases. Learn about one-to-many, many-to-many, and other relationship types with practical examples.',
        'Ready to create your first API? This step-by-step tutorial walks you through building a simple REST API using Flask and SQLite.',
        'Choosing between GraphQL and REST can be challenging. We break down the pros and cons of each to help you make an informed decision for your next project.',
        'Python\'s ecosystem includes powerful libraries that make backend development easier. Explore must-know libraries for building robust server applications.',
        'SQLite is perfect for learning databases and building lightweight applications. This beginner-friendly guide covers everything you need to get started.',
    ]

    # Get current time for generating varied timestamps
    now = datetime.now()

    # Create 5 posts for each user (15 total)
    post_count = 0
    for i, (title, content) in enumerate(zip(post_titles, post_contents)):
        # Assign posts evenly to users (5 posts each)
        author_id = user_ids[i // 5]

        # Generate varied timestamps - some recent, some older
        # Random days ago between 1 and 60 days
        days_ago = random.randint(1, 60)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)

        created_at = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

        # Insert post into database
        cursor.execute(
            'INSERT INTO posts (title, content, author_id, created_at) VALUES (?, ?, ?, ?)',
            (title, content, author_id, created_at)
        )
        post_count += 1

    connection.commit()
    print(f"✓ Inserted {post_count} posts into database")


def verify_data(connection):
    """
    Verify that data was inserted correctly by counting records.

    Args:
        connection: SQLite database connection
    """
    cursor = connection.cursor()

    # Count users
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    print(f"✓ Verification: {user_count} users in database")

    # Count posts
    cursor.execute('SELECT COUNT(*) FROM posts')
    post_count = cursor.fetchone()[0]
    print(f"✓ Verification: {post_count} posts in database")

    # Show sample data - first user with their post count
    cursor.execute('''
        SELECT u.name, u.email, COUNT(p.id) as post_count
        FROM users u
        LEFT JOIN posts p ON u.id = p.author_id
        GROUP BY u.id
        LIMIT 1
    ''')
    sample = cursor.fetchone()
    if sample:
        print(f"✓ Sample data: User '{sample[0]}' ({sample[1]}) has {sample[2]} posts")


def main():
    """
    Main function to orchestrate database initialization.

    This function:
    1. Creates database connection
    2. Creates tables
    3. Seeds sample data
    4. Verifies data was inserted correctly
    5. Closes connection
    """
    print("=" * 50)
    print("Database Initialization Started")
    print("=" * 50)

    # Create database connection
    connection = create_database()

    try:
        # Create tables
        create_tables(connection)

        # Seed data
        user_ids = seed_users(connection)
        seed_posts(connection, user_ids)

        # Verify data
        verify_data(connection)

        print("=" * 50)
        print("Database Initialization Completed Successfully!")
        print("=" * 50)
        print(f"\nYou can now use the '{DATABASE_NAME}' database.")
        print("Next step: Run 'python app.py' to start the server")

    except Exception as error:
        # If anything goes wrong, show the error
        print(f"\n✗ Error during initialization: {error}")
        connection.rollback()

    finally:
        # Always close the connection
        connection.close()
        print("\n✓ Database connection closed")


# Run the script when executed directly
if __name__ == '__main__':
    main()
