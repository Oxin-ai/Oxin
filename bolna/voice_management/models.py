from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.sql import func
from bolna.auth.database import Base


class Voice(Base):
    __tablename__ = "voices"

    id = Column(String(36), primary_key=True, index=True)
    voice_id = Column(String(255), nullable=False)
    provider = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    model = Column(String(255), nullable=False)
    accent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_provider', 'provider'),
    )