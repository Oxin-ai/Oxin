import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# MySQL database configuration from environment variables
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
# Default to 'localhost' for local development
# docker-compose.yml sets MYSQL_HOST=mysql for Docker environment (overrides .env)
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "bolna")

# Create SQLAlchemy database URL
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# Create engine with connection pooling for production
# Note: Engine creation doesn't connect to the database, so this is safe at import time
try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,  # Number of connections to maintain
        max_overflow=20,  # Maximum number of connections beyond pool_size
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=False  # Set to True for SQL query logging
    )
except Exception as e:
    # If engine creation fails, we'll still allow the module to load
    # The error will be raised when trying to use the engine
    import warnings
    warnings.warn(f"Failed to create database engine: {e}")
    engine = None

# Create session factory
if engine is not None:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    SessionLocal = None

# Base class for declarative models
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    if SessionLocal is None:
        raise RuntimeError("Database engine not initialized. Please check your database configuration.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
