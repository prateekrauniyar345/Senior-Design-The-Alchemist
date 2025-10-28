# Backend/config/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    # Mindat API
    mindat_api_key: str = Field(..., validation_alias="MINDAT_API_KEY")
    mindat_base_url: str = Field("https://api.mindat.org/v1/", validation_alias="MINDAT_HOST")

    # Azure OpenAI
    azure_deployment: str = Field(..., validation_alias="AZURE_DEPLOYMENT_NAME")
    azure_api_version: str = Field(..., validation_alias="AZURE_OPENAI_API_VERSION")
    azure_endpoint: str = Field(..., validation_alias="AZURE_OPENAI_API_ENDPOINT")
    azure_api_key: str = Field(..., validation_alias="AZURE_OPENAI_API_KEY")

    # Application
    debug: bool = Field(False, validation_alias="DEBUG")

    # API limits
    request_timeout: int = Field(30, validation_alias="REQUEST_TIMEOUT")
    max_retries: int = Field(3, validation_alias="MAX_RETRIES")

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",   # ignore unexpected env vars
    )

    @field_validator("mindat_api_key", "azure_api_key")
    @classmethod
    def validate_api_keys(cls, v: str) -> str:
        if not v or len(v) < 10:
            raise ValueError("API key is too short or missing")
        return v

# Singleton
settings = Settings()
