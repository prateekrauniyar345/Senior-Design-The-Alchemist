from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..database import Base
from .agent_models import AgentTask  


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # link session to a user
    title = Column(String(100), default="New Chat")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    messages = relationship("Message", back_populates="session")
    user = relationship("User", back_populates="sessions")
    tasks = relationship("AgentTask", back_populates="session", cascade="all, delete-orphan")



class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # add user tracking
    sender = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    output_type = Column(String(50), default="text")
    meta_data = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("Session", back_populates="messages")
    user = relationship("User", back_populates="messages")


class AgentOutput(Base):
    __tablename__ = "agent_outputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"))
    output_data = Column(Text, nullable=False)  # could store JSON or serialized output
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    input_tasks = relationship("AgentTask", back_populates="input_message", foreign_keys="AgentTask.input_message_id")
    output_tasks = relationship("AgentTask", back_populates="output_message", foreign_keys="AgentTask.output_message_id")

