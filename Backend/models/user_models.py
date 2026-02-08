
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.orm import relationship
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supabase_user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    email = Column(String(120), nullable=False)
    full_name = Column(String(120))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sessions = relationship("Session", back_populates="user")
    messages = relationship("Message", back_populates="user")
    runs = relationship("AgentRun", backref="user")
    tasks = relationship("AgentTask", backref="user")
    artifacts = relationship("DataArtifact", backref="user")
    visualizations = relationship("Visualization", backref="user")
