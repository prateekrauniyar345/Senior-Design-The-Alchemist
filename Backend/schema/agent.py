from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from Backend.database import Base
import uuid


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # link task to user
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
    agent_name = Column(String(100), nullable=False)
    input_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    output_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    status = Column(String(50), default="pending")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))

    # Relationships
    session = relationship("Session", back_populates="tasks")
    input_message = relationship("Message", foreign_keys=[input_message_id], back_populates="input_tasks")
    output_message = relationship("Message", foreign_keys=[output_message_id], back_populates="output_tasks")

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # link run to user
    agent_name = Column(String(100), nullable=False)       # e.g., "Collector", "Plotter"
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    status = Column(String(50), default="running")          # running, success, failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship: One run can produce multiple artifacts
    artifacts = relationship("DataArtifact", back_populates="run")

    def __repr__(self):
        return f"<AgentRun(agent_name={self.agent_name}, status={self.status})>"

class DataArtifact(Base):
    __tablename__ = "data_artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # link artifact to user
    run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.id"))
    artifact_type = Column(String(50))  # e.g., 'json', 'plot', 'map'
    file_path = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    run = relationship("AgentRun", back_populates="artifacts")


    # Relationships
    run = relationship("AgentRun", back_populates="artifacts")
    visualizations = relationship("Visualization", back_populates="artifact", cascade="all, delete-orphan")


class Visualization(Base):
    __tablename__ = "visualizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # link visualization to user
    artifact_id = Column(UUID(as_uuid=True), ForeignKey("data_artifacts.id"))
    viz_type = Column(String(50))  # e.g. 'histogram', 'heatmap', 'network'
    title = Column(String(120))
    description = Column(Text)
    rendered_html_path = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    artifact = relationship("DataArtifact", back_populates="visualizations")