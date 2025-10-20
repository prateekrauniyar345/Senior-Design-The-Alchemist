# Backend/config/supabase_client.py
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env from the Backend folder explicitly
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: Optional[object] = None
try:
    from supabase import create_client, Client
    if SUPABASE_URL and SUPABASE_ANON_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
except ModuleNotFoundError:
    supabase = None
