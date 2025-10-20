# Backend/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import secrets

class Settings(BaseSettings):
    # ---- External APIs (OPTIONAL for now) ----
    MINDAT_API_KEY: Optional[str] = None

    # Azure OpenAI (OPTIONAL — leave blank if not using Azure)
    AZURE_DEPLOYMENT_NAME: Optional[str] = None
    AZURE_OPENAI_API_VERSION: Optional[str] = None
    AZURE_OPENAI_API_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None

    # Supabase / DB (these can be blank until teammate shares)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    # App session secret (auto-generated if not provided)
    APP_SECRET: str = secrets.token_hex(32)

    # Load from Backend/.env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
