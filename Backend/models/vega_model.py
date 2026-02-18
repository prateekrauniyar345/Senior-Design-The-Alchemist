# Backend/models/vega_models.py
from pydantic import BaseModel
from typing import Dict, Any

class VegaLiteSpec(BaseModel):
    spec: Dict[str, Any]
