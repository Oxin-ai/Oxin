"""
Database migration script for Agent Management tables.
Run this script to create the required tables in MySQL.
"""

from bolna.auth.database import engine, Base
from bolna.auth.models import User, Tenant  # Import existing models
from bolna.agent_management.models import Agent, AgentConfiguration, AgentPrompt  # Import new models


def create_tables():
    """Create all tables in the database."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Agent Management tables created successfully!")
        print("Created tables:")
        print("- agents")
        print("- agent_configurations") 
        print("- agent_prompts")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


if __name__ == "__main__":
    create_tables()