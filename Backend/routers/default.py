from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
from ..core.config import get_templates

# Get templates instance
templates = get_templates()

# Create router instance
router = APIRouter(tags=["pages"])

@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """About page"""
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    """Privacy policy page"""
    return templates.TemplateResponse("privacy_policy.html", {"request": request})

@router.get("/terms-of-service", response_class=HTMLResponse)
async def terms_of_service(request: Request):
    """Terms of service page"""
    return templates.TemplateResponse("terms_of_service.html", {"request": request})