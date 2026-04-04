from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    # The UUID here will match the Supabase Auth user ID for easy integration
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # This matches the ID from Supabase Auth
    supabase_user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    email = Column(String(120), nullable=False)
    full_name = Column(String(120))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    # One-to-one relationship with Profile
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    sessions = relationship("Session", back_populates="user")
    messages = relationship("Message", back_populates="user")
    runs = relationship("AgentRun", backref="user")
    tasks = relationship("AgentTask", backref="user")
    artifacts = relationship("DataArtifact", backref="user")
    visualizations = relationship("Visualization", backref="user")

