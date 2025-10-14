from pydantic import BaseModel, Field
from typing import Optional


class MindatConfig(BaseModel):
    host:str = Field(..., description="Host URL of the Mindat API", example="https://www.mindat.org/api/v1")
    api_key: str = Field(..., description="API key for accessing the Mindat API", example="******************")