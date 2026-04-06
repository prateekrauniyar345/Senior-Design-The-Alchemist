from fastapi import APIRouter, HTTPException, Response, status, Depends, Request
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schema import User
from app.config import settings
import uuid
from app.models import LoginRequest, RegisterRequest, AuthResponse
from app.dependencies import get_current_user
from supabase import create_client, Client
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)


def _cookie_security() -> tuple[bool, str]:
    """
    Local HTTP: secure=False + SameSite=lax (browsers reject SameSite=None without Secure).
    Production HTTPS (e.g. API on its own domain): set COOKIE_SECURE=true → Secure + SameSite=none.
    """
    secure = os.getenv("COOKIE_SECURE", "").lower() in ("1", "true", "yes")
    samesite = "none" if secure else "lax"
    return secure, samesite


def _set_auth_cookies(response: Response, session) -> None:
    """Set HttpOnly auth cookies from a Supabase session."""
    secure, samesite = _cookie_security()
    path = "/"

    response.set_cookie(
        key="sb-access-token",
        value=session.access_token,
        path=path,
        httponly=True,
        secure=secure,
        samesite=samesite,
        max_age=session.expires_in,
    )

    response.set_cookie(
        key="sb-refresh-token",
        value=session.refresh_token,
        path=path,
        httponly=True,
        secure=secure,
        samesite=samesite,
        max_age=7 * 24 * 60 * 60,
    )

    # Legacy cookie name — expire if present
    response.set_cookie(
        key="user-id",
        value="",
        path=path,
        httponly=False,
        secure=secure,
        samesite=samesite,
        max_age=0,
    )


def _clear_auth_cookies(response: Response) -> None:
    secure, samesite = _cookie_security()
    path = "/"
    response.delete_cookie(
        key="sb-access-token", path=path, secure=secure, httponly=True, samesite=samesite
    )
    response.delete_cookie(
        key="sb-refresh-token", path=path, secure=secure, httponly=True, samesite=samesite
    )
    response.delete_cookie(
        key="user-id", path=path, secure=secure, httponly=False, samesite=samesite
    )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, response: Response, db: DBSession = Depends(get_db)):
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password,
        })

        print("auth response is", auth_response)
        print("\n\n")

        if not auth_response.user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        supabase_user = auth_response.user
        print("supabase user is", supabase_user)

        user = db.query(User).filter(User.supabase_user_id == uuid.UUID(supabase_user.id)).first()
        print("database user is", user)

        if not user:
            user = User(
                supabase_user_id=uuid.UUID(supabase_user.id),
                email=supabase_user.email,
                full_name=supabase_user.user_metadata.get("full_name", req.email.split("@")[0]),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # set all the cookies from the Supabase session
        _set_auth_cookies(response, auth_response.session)

        return AuthResponse(
            success=True,
            message="Login successful",
            user={"id": str(user.id), "email": user.email, "name": user.full_name},
            session={
                "access_token": auth_response.session.access_token,
                "expires_at": auth_response.session.expires_at,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Authentication failed: {str(e)}")


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, response: Response, db: DBSession = Depends(get_db)):
    try:
        auth_response = supabase.auth.sign_up({
            "email": req.email,
            "password": req.password,
            "options": {"data": {"full_name": req.name}},
        })

        print("auth response is : ", auth_response)

        if not auth_response.user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed. Email may already be in use.")

        supabase_user = auth_response.user
        print("supabase_user is : ", supabase_user)

        supabase_user_id = uuid.UUID(supabase_user.id)
        user = db.query(User).filter(User.supabase_user_id == supabase_user_id).first()
        if user:
            user.email = req.email
            user.full_name = req.name
            db.commit()
            db.refresh(user)
        else:
            user = User(
                supabase_user_id=supabase_user_id,
                email=req.email,
                full_name=req.name,
            )
            db.add(user)
            try:
                db.commit()
                db.refresh(user)
            except IntegrityError:
                db.rollback()
                user = db.query(User).filter(User.supabase_user_id == supabase_user_id).first()
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Could not create local user profile",
                    )

        if auth_response.session:
            _set_auth_cookies(response, auth_response.session)

        return AuthResponse(
            success=True,
            message="Registration successful" if auth_response.session else "Registration successful. Please check your email for verification.",
            user={"id": str(user.id), "email": user.email, "name": user.full_name},
            session={
                "access_token": auth_response.session.access_token if auth_response.session else None,
                "expires_at": auth_response.session.expires_at if auth_response.session else None,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Registration failed: {str(e)}")


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    """Use the refresh token cookie to get a new access token."""
    refresh_token_value = request.cookies.get("sb-refresh-token")
    if not refresh_token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    try:
        result = supabase.auth.refresh_session(refresh_token_value)
        if not result or not result.session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token refresh failed")

        _set_auth_cookies(response, result.session)
        return {"success": True, "message": "Token refreshed"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token refresh failed: {str(e)}")


@router.post("/logout")
async def logout(response: Response):
    """Sign out and clear all auth cookies."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    _clear_auth_cookies(response)

    return {"success": True, "message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user, validated via Supabase JWT."""
    return {
        "success": True,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.full_name,
        },
    }
