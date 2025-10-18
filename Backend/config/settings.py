from pydantic import BaseSettings, Field, validator
from typing import Optional
import os

class Settings(BaseSettings):
    # Mindat API
    mindat_api_key: str = Field(..., env="MINDAT_API_KEY")
    mindat_base_url: str = Field(default="https://api.mindat.org/v1/", env="MINDAT_HOST")
    
    # Azure OpenAI
    azure_deployment_name: str = Field(..., env="AZURE_DEPLOYMENT_NAME")
    azure_api_version: str = Field(..., env="AZURE_OPENAI_API_VERSION")
    azure_endpoint: str = Field(..., env="AZURE_OPENAI_API_ENDPOINT")
    azure_api_key: str = Field(..., env="AZURE_OPENAI_API_KEY")
    
    # Application
    debug: bool = Field(default=False, env="DEBUG")
    
    # API limits
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    
    class Config:
        env_file = ".env"        # Load environment variables from .env file
        case_sensitive = False      # Environment variable names are not case-sensitive (AZURE_API_KEY or azure_api_key both work).
    
    @validator('mindat_api_key', 'azure_api_key')
    def validate_api_keys(cls, v):    #cls = class, v = value, cls is Settings class
        if not v or len(v) < 10:
            raise ValueError("API key is too short or missing")
        return v

# Singleton pattern for settings
settings = Settings()