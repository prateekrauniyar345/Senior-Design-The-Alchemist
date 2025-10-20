import os
from fastapi import FastAPI, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
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
app.add_middleware(SessionMiddleware, secret_key=APP_SECRET)

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
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=HTTP_303_SEE_OTHER)
    msg = None if supabase else "Auth not configured yet. Ask for SUPABASE_URL and SUPABASE_ANON_KEY."
    return templates.TemplateResponse("login.html", {"request": request, "error": msg})

@app.post("/login")
async def login_action(request: Request, email: str = Form(...), password: str = Form(...)):
    if supabase is None:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Auth not configured."})
    try:
        data = supabase.auth.sign_in_with_password({"email": email, "password": password})
        session = data.session
        res = RedirectResponse(url="/dashboard", status_code=HTTP_303_SEE_OTHER)
        # set secure=True when using HTTPS in prod
        res.set_cookie(COOKIE_ACCESS, session.access_token, httponly=True, samesite="lax", secure=False)
        res.set_cookie(COOKIE_REFRESH, session.refresh_token, httponly=True, samesite="lax", secure=False)
        return res
    except Exception as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": str(e)})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=HTTP_303_SEE_OTHER)
    msg = None if supabase else "Auth not configured yet. Ask for SUPABASE_URL and SUPABASE_ANON_KEY."
    return templates.TemplateResponse("register.html", {"request": request, "error": msg})

@app.post("/register")
async def register_action(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if supabase is None:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Auth not configured."})
    try:
        # Save name to user metadata
        supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": name}}
        })
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    except Exception as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": str(e)})

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
