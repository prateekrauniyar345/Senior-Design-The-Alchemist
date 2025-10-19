import os

from fastapi import FastAPI, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER

# --- Supabase client (keep if you added auth) ---
from config.supabase_client import supabase

# --- DB imports (keep only if your app uses them) ---
# from Backend.DataBase.database import Base, engine
# from Backend.models.chat_models import Message

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from fastapi import FastAPI, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER
import os

# --- Supabase client (see step 2 below) ---
from config.supabase_client import supabase 

app = FastAPI(
    title="LLM-Driven Smart Agents for User-Friendly Access to an Open Data Portal",
    description="A FastAPI application with Agentic capabilities to facilitate user-friendly access using Large Language Models (GPT-4o).",
    version="0.0.1",
)

# --- Static files and templates ---
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Session middleware for secure cookies
APP_SECRET = os.getenv("APP_SECRET", "change-me")
app.add_middleware(SessionMiddleware, secret_key=APP_SECRET)

# Static + templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
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

async def require_user(user = Depends(get_current_user)):
    if not user:
        return None
    return user

# ---------- Public pages (yours) ----------
@app.get("/", response_class=HTMLResponse)
async def root(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("about.html", {"request": request, "user": user})

@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("privacy_policy.html", {"request": request, "user": user})

@app.get("/terms-of-service", response_class=HTMLResponse)
async def terms_of_service(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("terms_of_service.html", {"request": request, "user": user})

# ---------- Auth pages ----------
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login_action(response: Response, email: str = Form(...), password: str = Form(...)):
    if supabase is None:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Auth not configured yet. Ask teammate for SUPABASE_URL and SUPABASE_ANON_KEY."})
    try:
        data = supabase.auth.sign_in_with_password({"email": email, "password": password})
        session = data.session
        res = RedirectResponse(url="/dashboard", status_code=HTTP_303_SEE_OTHER)
        res.set_cookie(COOKIE_ACCESS, session.access_token, httponly=True, samesite="lax", secure=False)
        res.set_cookie(COOKIE_REFRESH, session.refresh_token, httponly=True, samesite="lax", secure=False)
        return res
    except Exception as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": str(e)})

@app.get("/register", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@app.post("/register")
async def signup_action(email: str = Form(...), password: str = Form(...)):
    if supabase is None:
        # Redirect back to /login with a gentle message or render register page with an error
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    supabase.auth.sign_up({"email": email, "password": password})
    return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)

@app.get("/logout")
async def logout():
    res = RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    res.delete_cookie(COOKIE_ACCESS)
    res.delete_cookie(COOKIE_REFRESH)
    return res

# ---------- Protected page ----------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user = Depends(require_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
