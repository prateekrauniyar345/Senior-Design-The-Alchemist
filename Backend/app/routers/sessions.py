# Backend/app/routers/sessions.py
import json
import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.sql import desc
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.schema.chat import Session as SessionModel
from app.schema.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _parse_meta(raw_meta):
    if raw_meta is None:
        return {}
    if isinstance(raw_meta, dict):
        return raw_meta
    if isinstance(raw_meta, str):
        try:
            return json.loads(raw_meta)
        except Exception:
            return {}
    return {}

class ArtifactResponse(BaseModel):
    id: UUID
    artifact_type: str
    file_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: UUID
    content: str
    sender: str  # "user" or "assistant"
    output_type: str
    meta_data: Optional[dict]
    created_at: datetime
    artifacts: List[ArtifactResponse] = Field(default_factory=list)

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
    auth_user_id = current_user.supabase_user_id
    sessions = db.query(SessionModel).filter(
        SessionModel.user_id == auth_user_id
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
    auth_user_id = current_user.supabase_user_id
    logger.info(
        "sessions.create_session: preparing user_id=%s title=%r",
        auth_user_id,
        request.title,
    )
    new_session = SessionModel(
        user_id=auth_user_id,
        title=request.title
    )
    db.add(new_session)
    try:
        logger.info(
            "sessions.create_session: committing user_id=%s supabase_user_id=%s title=%r",
            auth_user_id,
            auth_user_id,
            request.title,
        )
        db.commit()
        db.refresh(new_session)
    except IntegrityError:
        db.rollback()
        logger.exception("sessions.create_session: commit failed (IntegrityError)")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create chat session",
        )
    except Exception:
        db.rollback()
        logger.exception("sessions.create_session: commit failed (unexpected)")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create chat session",
        )
    return new_session

# Get all messages in a session
@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    session_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all messages in a specific session"""
    auth_user_id = current_user.supabase_user_id
    # Verify the session belongs to the user
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == auth_user_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    logger.info(
        "sessions.get_messages: loading session_id=%s user_id=%s",
        session_id,
        auth_user_id,
    )
    print(f"[sessions.get_messages] loading session_id={session_id}")
    try:
        message_rows = db.execute(
            text(
                """
                SELECT id, content, role, metadata, created_at
                FROM chat_messages
                WHERE session_id = :session_id
                ORDER BY created_at
                """
            ),
            {"session_id": str(session_id)},
        ).mappings().all()

        artifact_rows = db.execute(
            text(
                """
                SELECT id, message_id, type, storage_key, created_at
                FROM chat_artifacts
                WHERE session_id = :session_id
                ORDER BY created_at
                """
            ),
            {"session_id": str(session_id)},
        ).mappings().all()

        artifacts_by_message = {}
        for row in artifact_rows:
            key = str(row["message_id"])
            artifacts_by_message.setdefault(key, []).append(
                {
                    "id": row["id"],
                    "artifact_type": row["type"] or "file",
                    "file_url": row["storage_key"],
                    "created_at": row["created_at"],
                }
            )

        response_items = []
        for row in message_rows:
            meta_data = _parse_meta(row["metadata"])

            response_items.append(
                {
                    "id": row["id"],
                    "content": row["content"],
                    "sender": row["role"],
                    "output_type": meta_data.get("output_type", "text"),
                    "meta_data": meta_data,
                    "created_at": row["created_at"],
                    "artifacts": artifacts_by_message.get(str(row["id"]), []),
                }
            )

        logger.info(
            "sessions.get_messages: loaded %d messages for session_id=%s",
            len(response_items),
            session_id,
        )
        print(
            f"[sessions.get_messages] rows={[{'id': str(item['id']), 'sender': item['sender']} for item in response_items]} session_id={session_id}"
        )
        print(
            f"[sessions.get_messages] loaded count={len(response_items)} session_id={session_id}"
        )
        return response_items
    except Exception:
        logger.exception(
            "sessions.get_messages: failed loading session_id=%s",
            session_id,
        )
        print(f"[sessions.get_messages] failed session_id={session_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not load session messages",
        )

# Save a message to a session
@router.post("/{session_id}/messages", response_model=MessageResponse)
async def save_message(
    session_id: UUID,
    request: SaveMessageRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save a message to a session"""
    auth_user_id = current_user.supabase_user_id
    # Verify the session belongs to the user
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == auth_user_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    message_meta = dict(request.meta_data or {})
    message_meta.setdefault("output_type", request.output_type)

    row = db.execute(
        text(
            """
            INSERT INTO chat_messages (session_id, user_id, role, content, metadata)
            VALUES (:session_id, :user_id, :role, :content, CAST(:metadata AS jsonb))
            RETURNING id, content, role, metadata, created_at
            """
        ),
        {
            "session_id": str(session_id),
            "user_id": str(auth_user_id),
            "role": request.sender,
            "content": request.content,
            "metadata": json.dumps(message_meta),
        },
    ).mappings().first()
    db.commit()

    raw_meta = row["metadata"] if row else None
    parsed_meta = _parse_meta(raw_meta)

    return {
        "id": row["id"],
        "content": row["content"],
        "sender": row["role"],
        "output_type": parsed_meta.get("output_type", "text"),
        "meta_data": parsed_meta,
        "created_at": row["created_at"],
        "artifacts": [],
    }

# Delete a session
@router.delete("/{session_id}")
async def delete_session(
    session_id: UUID,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a session and all its messages"""
    auth_user_id = current_user.supabase_user_id
    logger.info(
        "sessions.delete_session: deleting session_id=%s user_id=%s",
        session_id,
        auth_user_id,
    )
    existing = db.execute(
        text(
            """
            SELECT id
            FROM chat_sessions
            WHERE id = :session_id AND user_id = :user_id
            LIMIT 1
            """
        ),
        {"session_id": str(session_id), "user_id": str(auth_user_id)},
    ).first()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    try:
        db.execute(
            text(
                """
                DELETE FROM chat_sessions
                WHERE id = :session_id AND user_id = :user_id
                """
            ),
            {"session_id": str(session_id), "user_id": str(auth_user_id)},
        )
        db.commit()
        logger.info(
            "sessions.delete_session: deleted session_id=%s user_id=%s",
            session_id,
            auth_user_id,
        )
        return {"message": "Session deleted successfully"}
    except Exception:
        db.rollback()
        logger.exception(
            "sessions.delete_session: failed session_id=%s user_id=%s",
            session_id,
            auth_user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete session",
        )

# Update session title
@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: UUID,
    request: CreateSessionRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update session title"""
    auth_user_id = current_user.supabase_user_id
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == auth_user_id
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
