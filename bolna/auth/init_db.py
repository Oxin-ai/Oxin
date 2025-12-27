"""
Database initialization script.
Run this to create all database tables.
"""
from bolna.auth.database import Base, engine
from bolna.helpers.logger_config import configure_logger

logger = configure_logger(__name__)


def init_db():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    init_db()
