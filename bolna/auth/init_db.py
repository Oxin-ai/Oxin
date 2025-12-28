"""
Database initialization script.
Run this to create the database and all database tables.
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from bolna.auth.database import Base, engine, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from bolna.auth.models import User, Tenant  # Import auth models
from bolna.agent_management.models import Agent, AgentConfiguration, AgentPrompt  # Import agent models
from bolna.helpers.logger_config import configure_logger
from urllib.parse import quote_plus

logger = configure_logger(__name__)


def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    try:
        # Use root user to create database (has CREATE DATABASE permission)
        MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD", "StrongPassword123")
        encoded_root = quote_plus("root")
        encoded_root_password = quote_plus(MYSQL_ROOT_PASSWORD)
        server_url = f"mysql+pymysql://{encoded_root}:{encoded_root_password}@{MYSQL_HOST}:{MYSQL_PORT}"
        
        server_engine = create_engine(server_url, pool_pre_ping=True)
        
        with server_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SHOW DATABASES LIKE '{MYSQL_DB}'"))
            if result.fetchone() is None:
                logger.info(f"Database '{MYSQL_DB}' does not exist. Creating it...")
                # Create database
                conn.execute(text(f"CREATE DATABASE `{MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                conn.commit()
                logger.info(f"Database '{MYSQL_DB}' created successfully")
            else:
                logger.info(f"Database '{MYSQL_DB}' already exists")
        
        server_engine.dispose()
    except Exception as e:
        logger.error(f"Error creating database: {e}", exc_info=True)
        # Don't raise - continue with table creation even if database creation fails
        pass


def init_db():
    """Create the database (if needed) and all database tables."""
    try:
        # First, ensure the database exists
        create_database_if_not_exists()
        
        # Then create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        # Don't raise - let the application start even if DB init fails
        pass


if __name__ == "__main__":
    init_db()
