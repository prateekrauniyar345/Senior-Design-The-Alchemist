from pydantic import BaseModel, Field

class PandasDFInput(BaseModel):
    file_path: str = Field(description="Should be a json file path for pandas to analyze and plot")