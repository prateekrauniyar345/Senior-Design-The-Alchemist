from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal, Tuple, Union

class PandasDFInput(BaseModel):
    file_path: str = Field(description="Should be a json file path for pandas to analyze and plot")
    plot_title: Optional[str] = Field(default=None, description="Optional title for the plot")


# ------------------------------
# Request/Response Models
# ------------------------------
class DownloadRequest(BaseModel):
    """Request model for downloading plots"""
    file_name: str
    format: Literal["png", "pdf"] = "png"


class EmailPlotRequest(BaseModel):
    """Request model for emailing plots"""
    file_name: str
    recipient_email: EmailStr
    subject: Optional[str] = "Your Mineral Data Visualization"
    message: Optional[str] = "Please find attached your requested visualization."


class PlotActionResponse(BaseModel):
    """Response model for plot actions"""
    success: bool
    message: str
    error: Optional[str] = None
