# Backend/app/routers/sessions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.sql import desc
from app.database import get_db
from app.schema.chat import Session as SessionModel, Message
from app.schema.user import User
from app.dependencies import get_current_user
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import json

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

class MessageResponse(BaseModel):
    id: UUID
    content: str
    sender: str  # "user" or "assistant"
    output_type: str
    meta_data: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True

class SessionResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class CreateSessionRequest(BaseModel):
    title: str = "New Chat"

class SaveMessageRequest(BaseModel):
    content: str
    sender: str  # "user" or "assistant"
    output_type: str = "text"
    meta_data: Optional[dict] = None

# Get all sessions for logged-in user
@router.get("", response_model=List[SessionResponse])
async def get_sessions(db: DBSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all sessions for the current user, ordered by most recent"""
    sessions = db.query(SessionModel).filter(
        SessionModel.user_id == current_user.id
    ).order_by(desc(SessionModel.created_at)).all()
    
    return sessions

# Create a new session
@router.post("", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat session"""
    new_session = SessionModel(
        user_id=current_user.id,
        title=request.title
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

# Get all messages in a session
@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    session_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all messages in a specific session"""
    # Verify the session belongs to the user
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at.asc(), Message.id.asc()).all()
    
    # Parse meta_data JSON strings back to dicts
    for msg in messages:
        if msg.meta_data:
            try:
                msg.meta_data = json.loads(msg.meta_data)
            except:
                msg.meta_data = {}
    
    return messages

# Save a message to a session
@router.post("/{session_id}/messages", response_model=MessageResponse)
async def save_message(
    session_id: UUID,
    request: SaveMessageRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save a message to a session"""
    # Verify the session belongs to the user
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Convert meta_data dict to JSON string
    meta_data_str = json.dumps(request.meta_data) if request.meta_data else None
    
    new_message = Message(
        session_id=session_id,
        user_id=current_user.id,
        sender=request.sender,
        content=request.content,
        output_type=request.output_type,
        meta_data=meta_data_str
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    # Parse meta_data for response
    if new_message.meta_data:
        try:
            new_message.meta_data = json.loads(new_message.meta_data)
        except:
            new_message.meta_data = {}
    
    return new_message

# Delete a session
@router.delete("/{session_id}")
async def delete_session(
    session_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a session and all its messages"""
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully"}

# Update session title
@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: UUID,
    request: CreateSessionRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update session title"""
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.title = request.title
    db.commit()
    db.refresh(session)
    
    return session
