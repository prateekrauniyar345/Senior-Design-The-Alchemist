from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.database import get_db
from app.schema.user import User
from app.config import settings
from supabase import create_client, Client
import uuid

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)


def get_db_user_row(db: DBSession, current_user: User) -> User:
    """
    Re-load the local User row by supabase_user_id so inserts use the primary key
    that actually exists in the database (avoids FK violations on chat_sessions / chat_messages).
    """
    row = (
        db.query(User)
        .filter(User.supabase_user_id == current_user.supabase_user_id)
        .first()
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return row


def _provision_local_user(
    db: DBSession, sb_user, supabase_user_id: uuid.UUID
) -> User:
    """Create a local users row from Supabase JWT claims (OAuth / first API hit)."""
    email = (getattr(sb_user, "email", None) or "").strip()
    if not email:
        email = f"{supabase_user_id}@profile.sync.local"
    meta = getattr(sb_user, "user_metadata", None) or {}
    full_name = None
    if isinstance(meta, dict):
        full_name = meta.get("full_name")
    if not full_name:
        full_name = email.split("@")[0] if "@" in email else "User"
    user = User(
        supabase_user_id=supabase_user_id,
        email=email[:120],
        full_name=(full_name or "User")[:120],
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(User)
            .filter(User.supabase_user_id == supabase_user_id)
            .first()
        )
        if existing:
            return existing
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not synchronize user account",
        )


async def get_current_user(request: Request, db: DBSession = Depends(get_db)) -> User:
    """Validate Supabase JWT and return the local user. Raises 401 if not authenticated."""
    access_token = request.cookies.get("sb-access-token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        sb_response = supabase.auth.get_user(access_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    if not sb_response or not sb_response.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    try:
        supabase_user_id = uuid.UUID(sb_response.user.id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )

    user = db.query(User).filter(User.supabase_user_id == supabase_user_id).first()
    if not user:
        user = _provision_local_user(db, sb_response.user, supabase_user_id)

    return user


async def get_optional_user(request: Request, db: DBSession = Depends(get_db)) -> Optional[User]:
    """Like get_current_user but returns None instead of raising 401. Used for optional auth."""
    access_token = request.cookies.get("sb-access-token")
    if not access_token:
        return None
    try:
        sb_response = supabase.auth.get_user(access_token)
        if not sb_response or not sb_response.user:
            return None
        supabase_user_id = uuid.UUID(sb_response.user.id)
        return db.query(User).filter(User.supabase_user_id == supabase_user_id).first()
    except Exception:
        return None
