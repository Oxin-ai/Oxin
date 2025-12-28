from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from bolna.auth.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    agent_type = Column(String(50), nullable=False, default="other")
    status = Column(String(20), nullable=False, default="active")  # active, disabled, deleted
    welcome_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", backref="agents")
    created_by = relationship("User", backref="created_agents")
    configurations = relationship("AgentConfiguration", back_populates="agent", cascade="all, delete-orphan")
    prompts = relationship("AgentPrompt", back_populates="agent", cascade="all, delete-orphan")

    # Indexes for security and performance
    __table_args__ = (
        Index('idx_tenant_uuid', 'tenant_id', 'uuid'),
        Index('idx_tenant_status', 'tenant_id', 'status'),
        Index('idx_created_by', 'created_by_user_id'),
    )


class AgentConfiguration(Base):
    __tablename__ = "agent_configurations"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    configuration_data = Column(JSON, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship
    agent = relationship("Agent", back_populates="configurations")

    # Indexes
    __table_args__ = (
        Index('idx_agent_active', 'agent_id', 'is_active'),
        Index('idx_agent_version', 'agent_id', 'version'),
    )


class AgentPrompt(Base):
    __tablename__ = "agent_prompts"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    prompt_data = Column(JSON, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship
    agent = relationship("Agent", back_populates="prompts")

    # Indexes
    __table_args__ = (
        Index('idx_agent_active', 'agent_id', 'is_active'),
        Index('idx_agent_version', 'agent_id', 'version'),
    )