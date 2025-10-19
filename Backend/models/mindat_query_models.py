from pydantic import BaseModel, Field
from typing import Optional

class MindatGeoMaterialQuery(BaseModel):
    """
    Mindat Query Parameters
    """
    ima: Optional[bool] = Field(description="Only IMA-approved names, should be True by default")
    hardness_min: Optional[float] = Field(description="Mohs hardness from")
    hardness_max: Optional[float] = Field(description="Mohs hardness to")
    crystal_system: Optional[list[str]] = Field(description=" Crystal system (csystem): multiple choice (OR), Items Enum: 'Amorphous','Hexagonal','Icosahedral','Isometric','Monoclinic','Orthorhombic','Tetragonal','Triclinic','Trigonal'")
    el_inc: Optional[str] = Field(description="Chemical elements must include, e.g., 'Fe,Cu'")
    el_exc: Optional[str] = Field(description="Chemical elements must exclude, e.g., 'Fe,Cu'")
    expand: Optional[str] = Field(description="Expand the search scope, 'description','type_localities','locality','relations','minstats', leave blank if necessary")


class MindatGeomaterialInput(BaseModel):
    query: MindatGeoMaterialQuery = Field(description="""Example dicts, all of the keys are optional, leave blank if necessary:
        {
            "ima": True,  # Only IMA-approved names
            "hardness_min": 1.0,  # Mohs hardness from 1
            "hardness_max": 10.0,  # Mohs hardness to 10
            "crystal_system": ["Hexagonal"],  # Hexagonal crystal system
            "el_inc": "Ag,H",  # Must include Gold (Ag) and Hxygen (H)
            "el_exc": "Fe",  # Exclude Iron (Fe)
        }
        """)


