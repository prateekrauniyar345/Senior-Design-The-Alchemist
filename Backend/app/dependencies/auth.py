from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session as DBSession
from typing import Optional
from app.database import get_db
from app.schema.user import User
from app.config import settings
from supabase import create_client, Client
import uuid

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)


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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

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
