from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from Backend.DataBase.database import Base  # this now works because database.py exists

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=True)
    sender = Column(String(50), nullable=False)         # 'user' or 'agent'
    content = Column(Text, nullable=False)
    output_type = Column(String(50), default="text")    # 'text', 'plot', 'map', etc.
    meta_data = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
