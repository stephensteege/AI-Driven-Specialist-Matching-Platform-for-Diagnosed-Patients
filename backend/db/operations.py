"""
File: operations.py

Description:
Provides database operation functions for interacting with the application’s data.
This file acts as an abstraction layer between the Flask application and the database,
handling common queries such as inserting, retrieving, and managing records.

Purpose:
- Encapsulates all database-related logic in one location.
- Prevents raw SQL from being scattered throughout the application.
- Improves code organization, readability, and maintainability.

Typical Responsibilities:
- Insert new records (e.g., predictions, slot data).
- Retrieve stored data (e.g., history, search results).
- Update or delete records when necessary.

Note:
This file serves a similar role to stored procedures in databases that do not
support them (e.g., SQLite), by implementing reusable logic in Python instead.
"""