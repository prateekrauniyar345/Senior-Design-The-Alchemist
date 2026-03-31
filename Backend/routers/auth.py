# FastAPI imports for routing, request/response handling, and error management
from fastapi import APIRouter, HTTPException, Response, status, Depends, Request

# Pydantic models for request validation
from pydantic import BaseModel, EmailStr

# Supabase client
from supabase import create_client, Client

# App settings (contains env, supabase_url, supabase_key, etc.)
from Backend.config import settings


# Create a router specifically for authentication endpoints
# All routes here will be prefixed with /api/auth
router = APIRouter(prefix="/api/auth", tags=["auth"])
print("LOADING AUTH ROUTER FROM:", __file__)


# Initialize Supabase client using project credentials
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

# Admin client for profile updates (requires SUPABASE_SERVICE_ROLE_KEY)
supabase_admin: Client | None = None
if settings.supabase_service_role_key:
    supabase_admin = create_client(settings.supabase_url, settings.supabase_service_role_key)


def _get_display_name(user) -> str:
    """Extract display name from Supabase user metadata. Uses 'name' or 'full_name'."""
    meta = getattr(user, "user_metadata", None) or {}
    if isinstance(meta, dict):
        return (meta.get("name") or meta.get("full_name") or "").strip() or ""
    return ""


# Cookie names used to store JWT tokens
COOKIE_ACCESS = "sb_access"
COOKIE_REFRESH = "sb_refresh"


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """
    Store Supabase access and refresh tokens in HTTP-only cookies.

    Session-only cookies: we do NOT set max_age or expires, so the browser
    treats them as session cookies. Combined with frontend not calling /me on
    load, this supports "logged out on refresh" when VITE_FORCE_LOGOUT_ON_LOAD
    is used; without that flag, session cookies still survive refresh until
    the tab is closed.

    Cookies are:
    - HttpOnly: not accessible via JavaScript (prevents XSS token theft)
    - Secure: only sent over HTTPS in production
    - SameSite=lax: prevents most CSRF attacks
    """

    # If running in production, cookies must be secure (HTTPS only)
    is_prod = False  # local development

    # Session-only: omit max_age so cookie does not persist across browser restarts.
    response.set_cookie(
        key=COOKIE_ACCESS,
        value=access_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        path="/",
    )

    response.set_cookie(
        key=COOKIE_REFRESH,
        value=refresh_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        path="/",
    )


def clear_auth_cookies(response: Response):
    """
    Remove authentication cookies from the client.
    Used during logout.
    """
    response.delete_cookie(COOKIE_ACCESS, path="/")
    response.delete_cookie(COOKIE_REFRESH, path="/")


# Request model for login endpoint
class LoginRequest(BaseModel):
    email: EmailStr  # Automatically validates email format
    password: str


# Request model for registration endpoint
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


@router.post("/login")
def login(req: LoginRequest, response: Response):
    """
    Login endpoint.

    Flow:
    1. Authenticate user using Supabase Auth.
    2. If successful, store access + refresh tokens in cookies.
    3. Return minimal user info to frontend.
    """

    try:
        # Attempt login with Supabase Auth
        auth = supabase.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password
        })

        # Ensure both user and session exist
        if not auth.user or not auth.session:
            raise HTTPException(status_code=401, detail="Invalid login credentials")

        # Store tokens in secure HTTP-only cookies
        set_auth_cookies(response, auth.session.access_token, auth.session.refresh_token)

        name = _get_display_name(auth.user)
        return {
            "user": {
                "id": auth.user.id,
                "email": auth.user.email,
                "name": name,
            }
        }

    except Exception as e:
        # Surface Supabase error message for easier debugging
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/register")
def register(req: RegisterRequest):
    """
    Register endpoint.

    Flow:
    1. Create user in Supabase Auth.
    2. Attach additional metadata (name).
    3. If email confirmation is enabled, user must confirm before login.
    """

    try:
        auth = supabase.auth.sign_up({
            "email": req.email,
            "password": req.password,
            "options": {
                "data": {"name": req.name}  # stored in user metadata
            }
        })

        if not auth.user:
            raise HTTPException(status_code=400, detail="Could not create account")

        return {"message": "Registered. Check email to confirm (if enabled)."}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
def logout(response: Response):
    """
    Logout endpoint.

    Simply clears authentication cookies.
    No need to call Supabase unless you want to revoke refresh token.
    """
    clear_auth_cookies(response)
    return {"message": "Logged out"}


@router.get("/me")
def me(request: Request):
    access_token = request.cookies.get(COOKIE_ACCESS)
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated (no cookie)")

    try:
        # Supabase returns a UserResponse-like object in newer supabase-py
        res = supabase.auth.get_user(access_token)

        # handle both object-style + dict-style responses across versions
        user = None
        if hasattr(res, "user"):
            user = res.user
        elif isinstance(res, dict):
            user = res.get("user")

        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated (invalid token)")

        name = _get_display_name(user)
        return {"user": {"id": user.id, "email": user.email, "name": name}}

    except Exception as e:
        # IMPORTANT: return the real error so frontend shows it
        raise HTTPException(status_code=401, detail=f"/me failed: {str(e)}")


# Profile update request
class ProfileUpdateRequest(BaseModel):
    name: str


def _get_user_from_request(request: Request):
    """Extract authenticated user from request cookies. Raises 401 if not authenticated."""
    access_token = request.cookies.get(COOKIE_ACCESS)
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated (no cookie)")
    res = supabase.auth.get_user(access_token)
    user = getattr(res, "user", None) or (res if isinstance(res, dict) else {}).get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated (invalid token)")
    return user


@router.get("/profile")
def get_profile(request: Request):
    """
    Get current user profile (id, email, name).
    Same shape as /me; useful for refreshing profile in modals.
    """
    user = _get_user_from_request(request)
    name = _get_display_name(user)
    return {
        "id": user.id,
        "email": user.email or "",
        "name": name,
    }


@router.patch("/profile")
def update_profile(req: ProfileUpdateRequest, request: Request):
    """
    Update user display name in Supabase user_metadata.
    Requires SUPABASE_SERVICE_ROLE_KEY to be set in env.
    """
    if not supabase_admin:
        raise HTTPException(
            status_code=503,
            detail="Profile updates are not configured. Set SUPABASE_SERVICE_ROLE_KEY.",
        )
    user = _get_user_from_request(request)
    new_name = (req.name or "").strip()
    meta = getattr(user, "user_metadata", None) or {}
    if not isinstance(meta, dict):
        meta = {}
    meta = dict(meta)
    meta["name"] = new_name
    try:
        updated = supabase_admin.auth.admin.update_user_by_id(
            user.id,
            {"user_metadata": meta},
        )
        u = getattr(updated, "user", None) or (updated if isinstance(updated, dict) else {}).get("user")
        name = _get_display_name(u) if u else (req.name or "").strip()
        return {"id": user.id, "email": user.email or "", "name": name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))