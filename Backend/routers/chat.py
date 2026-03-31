"""
Chat history API using existing sessions and messages tables.
Auth via _get_user_from_request. Sessions use user_id (users.id).
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import text
from typing import Optional
import uuid

from Backend.database import get_db
from Backend.routers.auth import _get_user_from_request

router = APIRouter(prefix="/chat", tags=["chat"])


class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New conversation"


class RenameSessionRequest(BaseModel):
    title: str = Field(..., min_length=1)


class CreateMessageRequest(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)
    image_url: Optional[str] = None
    metadata: Optional[dict] = None


def _get_internal_user_id(request: Request, db: DBSession) -> uuid.UUID:
    """Resolve Supabase auth user to users.id. Creates user if not exists."""
    auth_user = _get_user_from_request(request)
    supabase_user_id = str(auth_user.id)
    email = auth_user.email or ""

    row = db.execute(
        text("SELECT id FROM public.users WHERE supabase_user_id = :sid LIMIT 1"),
        {"sid": supabase_user_id},
    ).mappings().first()

    if row:
        return row["id"]

    # Create user on first chat access (ignore conflict if already exists)
    meta = getattr(auth_user, "user_metadata", None) or {}
    full_name = (meta.get("name") or meta.get("full_name") or "") if isinstance(meta, dict) else ""
    db.execute(
        text("""
            INSERT INTO public.users (id, supabase_user_id, email, full_name)
            VALUES (gen_random_uuid(), CAST(:sid AS uuid), :email, :full_name)
            ON CONFLICT (supabase_user_id) DO NOTHING
        """),
        {"sid": supabase_user_id, "email": email, "full_name": full_name or None},
    )
    db.commit()
    row = db.execute(
        text("SELECT id FROM public.users WHERE supabase_user_id = :sid LIMIT 1"),
        {"sid": supabase_user_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=500, detail="Could not resolve user")
    return row["id"]


def _get_owned_session(db: DBSession, session_id: str, user_id: uuid.UUID) -> dict:
    row = db.execute(
        text("""
            SELECT id, user_id, title, created_at, updated_at
            FROM public.sessions
            WHERE id = :sid AND user_id = :uid
            LIMIT 1
        """),
        {"sid": session_id, "uid": str(user_id)},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
    return dict(row)


# --- Endpoints ---

@router.post("/sessions")
def create_session(
    payload: CreateSessionRequest,
    request: Request,
    db: DBSession = Depends(get_db),
):
    """Create a new session for the logged-in user."""
    user_id = _get_internal_user_id(request, db)
    row = db.execute(
        text("""
            INSERT INTO public.sessions (id, user_id, title)
            VALUES (gen_random_uuid(), :user_id, :title)
            RETURNING id, user_id, title, created_at, updated_at
        """),
        {"user_id": str(user_id), "title": payload.title or "New conversation"},
    ).mappings().first()
    db.commit()
    return dict(row)


@router.get("/sessions")
def list_sessions(
    request: Request,
    db: DBSession = Depends(get_db),
):
    """List all sessions for the logged-in user, ordered by updated_at DESC."""
    user_id = _get_internal_user_id(request, db)
    rows = db.execute(
        text("""
            SELECT id, user_id, title, created_at, updated_at
            FROM public.sessions
            WHERE user_id = :user_id
            ORDER BY updated_at DESC NULLS LAST, created_at DESC
        """),
        {"user_id": str(user_id)},
    ).mappings().all()
    return [dict(r) for r in rows]


@router.get("/sessions/{session_id}")
def get_session(
    session_id: str,
    request: Request,
    db: DBSession = Depends(get_db),
):
    """Get session and its messages. User must own the session."""
    user_id = _get_internal_user_id(request, db)
    session = _get_owned_session(db, session_id, user_id)

    msg_rows = db.execute(
        text("""
            SELECT id, session_id, sender, content, output_type, meta_data, created_at
            FROM public.messages
            WHERE session_id = :sid
            ORDER BY created_at ASC
        """),
        {"sid": session_id},
    ).mappings().all()

    messages = []
    for m in msg_rows:
        d = dict(m)
        # Frontend expects "image" for plot URL - use meta_data when output_type is plot
        if m.get("output_type") == "plot" and m.get("meta_data"):
            d["image"] = m["meta_data"]
        messages.append(d)
    return {
        "id": session["id"],
        "title": session["title"],
        "created_at": session["created_at"],
        "updated_at": session["updated_at"],
        "messages": messages,
    }


@router.post("/sessions/{session_id}/messages")
def create_message(
    session_id: str,
    payload: CreateMessageRequest,
    request: Request,
    db: DBSession = Depends(get_db),
):
    """Insert a message and update session.updated_at."""
    user_id = _get_internal_user_id(request, db)
    session = _get_owned_session(db, session_id, user_id)

    sender = "user" if payload.role == "user" else "assistant"
    img = payload.image_url or (payload.metadata or {}).get("plot_file_path") or (payload.metadata or {}).get("image")
    output_type = "plot" if img else "text"
    meta_data = img

    row = db.execute(
        text("""
            INSERT INTO public.messages (id, session_id, sender, content, output_type, meta_data)
            VALUES (gen_random_uuid(), :session_id, :sender, :content, :output_type, :meta_data)
            RETURNING id, session_id, sender, content, output_type, meta_data, created_at
        """),
        {
            "session_id": session_id,
            "sender": sender,
            "content": payload.content,
            "output_type": output_type,
            "meta_data": meta_data,
        },
    ).mappings().first()

    # Update session.updated_at
    db.execute(
        text("""
            UPDATE public.sessions
            SET updated_at = NOW()
            WHERE id = :sid AND user_id = :uid
        """),
        {"sid": session_id, "uid": str(user_id)},
    )

    # Auto-update title from first user message
    if payload.role == "user":
        title = (session.get("title") or "").strip().lower()
        if not title or title == "new conversation" or title == "new chat":
            new_title = (payload.content.strip()[:60] or "New conversation")
            db.execute(
                text("""
                    UPDATE public.sessions
                    SET title = :title, updated_at = NOW()
                    WHERE id = :sid AND user_id = :uid
                """),
                {"title": new_title, "sid": session_id, "uid": str(user_id)},
            )

    db.commit()
    out = dict(row)
    if row.get("output_type") == "plot" and row.get("meta_data"):
        out["image"] = row["meta_data"]
    return out


@router.patch("/sessions/{session_id}")
def rename_session(
    session_id: str,
    payload: RenameSessionRequest,
    request: Request,
    db: DBSession = Depends(get_db),
):
    """Rename a session."""
    user_id = _get_internal_user_id(request, db)
    _get_owned_session(db, session_id, user_id)

    row = db.execute(
        text("""
            UPDATE public.sessions
            SET title = :title, updated_at = NOW()
            WHERE id = :sid AND user_id = :uid
            RETURNING id, title, updated_at
        """),
        {"title": payload.title.strip(), "sid": session_id, "uid": str(user_id)},
    ).mappings().first()
    db.commit()
    return dict(row)


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: str,
    request: Request,
    db: DBSession = Depends(get_db),
):
    """Delete session. Messages cascade delete if configured in DB."""
    user_id = _get_internal_user_id(request, db)
    _get_owned_session(db, session_id, user_id)

    db.execute(
        text("DELETE FROM public.sessions WHERE id = :sid AND user_id = :uid"),
        {"sid": session_id, "uid": str(user_id)},
    )
    db.commit()
    return {"message": "Deleted"}
