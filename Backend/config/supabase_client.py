# Backend/config/supabase_client.py
from typing import Optional
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()  # loads Backend/.env

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_ANON_KEY:
    # Only create the client if both values exist
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
