from pydantic import BaseModel, Field
from typing import Optional

class PandasDFInput(BaseModel):
    file_path: str = Field(description="Should be a json file path for pandas to analyze and plot")
    plot_title: Optional[str] = Field(default=None, description="Optional title for the plot")