"""
Database connection and utilities for MCP Server
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional
from config import CONFIG

def get_db():
    """
    Get PostgreSQL database connection.
    
    Returns:
        psycopg2.connection: Database connection with RealDictCursor
    """
    return psycopg2.connect(
        host=CONFIG['DB_HOST'],
        port=CONFIG['DB_PORT'],
        database=CONFIG['DB_NAME'],
        user=CONFIG['DB_USER'],
        password=CONFIG['DB_PASSWORD'],
        cursor_factory=RealDictCursor
    )

