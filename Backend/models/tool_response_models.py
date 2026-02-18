# Backend/models/tool_response_models.py
from pydantic import BaseModel, Field
from typing import Optional, Any, Literal, Dict, List, Tuple, Union

class GeomaterialToolResponse(BaseModel):
    """Structured response for the geomaterial collection tool"""
    status: Literal["OK", "ERROR"] = Field(..., description="The status of the operation")
    error: Optional[str] = Field(None, description="Detailed error message if status is ERROR")
    file_path: Optional[str] = Field("", description="The path where the JSON data was saved")



class LocalityToolResponse(BaseModel):
    """Structured response for the Mindat Locality collection tool"""
    status: Literal["OK", "ERROR"] = Field(..., description="Operation status. 'OK' if successful, 'ERROR' if something went wrong.")
    error: Optional[str] = Field(None, description="Detailed error message; null if status is OK.")
    file_path: str = Field(default="", description="The local file system path where the locality results are stored as JSON.")
    count: int = Field(default=0, description="The number of locality records successfully retrieved.")


class HistogramToolResponse(BaseModel):
    status: Literal["OK", "ERROR"]
    error: Optional[str] = None
    plot_file_path: str = ""
    data_file_path: Optional[str] = None
    chart_spec: Optional[Dict[str, Any]] = None
