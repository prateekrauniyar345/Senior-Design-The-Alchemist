from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any



class SessionBase(BaseModel):
    title: Optional[str] = "New Chat"
    user_id: Optional[UUID] = None

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MessageBase(BaseModel):
    session_id: UUID
    user_id: UUID
    sender: str = Field(..., description="e.g., 'user' or 'assistant'")
    content: str
    output_type: str = "text"
    meta_data: Optional[str] = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentOutputBase(BaseModel):
    message_id: UUID
    user_id: Optional[UUID] = None
    output_data: str  # JSON strings or serialized data

class AgentOutputCreate(AgentOutputBase):
    pass

class AgentOutput(AgentOutputBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionWithMessages(Session):
    """Useful for fetching a full chat history in one go"""
    messages: List[Message] = []