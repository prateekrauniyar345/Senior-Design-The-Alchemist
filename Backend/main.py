import os
from fastapi import FastAPI, Request, Form, Depends, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_303_SEE_OTHER

from config.supabase_client import supabase  # supabase client or None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="LLM-Driven Smart Agents for User-Friendly Access to an Open Data Portal",
    description="A FastAPI application with Agentic capabilities to facilitate user-friendly access using Large Language Models (GPT-4o).",
    version="0.0.1",
)

# Sessions for auth cookies
APP_SECRET = os.getenv("APP_SECRET", "change-me")
app.add_middleware(
    SessionMiddleware,
    secret_key=APP_SECRET,
    same_site="lax"       # works fine for local dev
)

# 2️⃣  CORS (React <-> FastAPI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static + templates
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
templates.env.auto_reload = True
templates.env.cache = {}

# ---------- Auth helpers ----------
COOKIE_ACCESS = "sb_access_token"
COOKIE_REFRESH = "sb_refresh_token"

async def get_current_user(request: Request):
    if supabase is None:
        return None
    token = request.cookies.get(COOKIE_ACCESS)
    if not token:
        return None
    try:
        res = supabase.auth.get_user(token)
        return res.user
    except Exception:
        return None

# ---------- Public pages ----------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse("about.html", {"request": request, "user": user})

@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse("privacy_policy.html", {"request": request, "user": user})

@app.get("/terms-of-service", response_class=HTMLResponse)
async def terms_of_service(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse("terms_of_service.html", {"request": request, "user": user})

# ---------- Auth pages ----------
#@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=HTTP_303_SEE_OTHER)
    msg = None if supabase else "Auth not configured yet. Ask for SUPABASE_URL and SUPABASE_ANON_KEY."
    return templates.TemplateResponse("login.html", {"request": request, "error": msg})

@app.post("/api/auth/login")
async def api_login(payload: dict, response: Response):
    """React client sends JSON { email, password }"""
    if supabase is None:
        raise HTTPException(status_code=500, detail="Auth not configured")

    email = (payload or {}).get("email")
    password = (payload or {}).get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Missing email or password")

    try:
        data = supabase.auth.sign_in_with_password({"email": email, "password": password})
        session = data.session
        if not session:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # set cookies (for dev secure=False)
        response.set_cookie(COOKIE_ACCESS, session.access_token, httponly=True, samesite="lax", secure=False)
        response.set_cookie(COOKIE_REFRESH, session.refresh_token, httponly=True, samesite="lax", secure=False)
        return {"ok": True}
    except Exception as e:
        return JSONResponse({"ok":True, "error": str(e)}, status_code=401)

#@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=HTTP_303_SEE_OTHER)
    msg = None if supabase else "Auth not configured yet. Ask for SUPABASE_URL and SUPABASE_ANON_KEY."
    return templates.TemplateResponse("register.html", {"request": request, "error": msg})

@app.post("/api/auth/register")
async def api_register(payload: dict):
    if supabase is None:
        raise HTTPException(status_code=500, detail="Auth not configured (.env)")

    name = (payload or {}).get("name")
    email = (payload or {}).get("email")
    password = (payload or {}).get("password")

    if not name or not email or not password:
        raise HTTPException(status_code=400, detail="Missing name/email/password")

    try:
        # This may require email confirmation depending on your Supabase settings
        supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": name}},
        })
        return {"ok": True}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)

@app.get("/logout")
async def logout():
    res = RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    res.delete_cookie(COOKIE_ACCESS)
    res.delete_cookie(COOKIE_REFRESH)
    return res

# ---------- Protected page ----------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
