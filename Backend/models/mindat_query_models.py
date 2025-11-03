from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal, Union







####################################
# geomaterial query model
####################################
class MindatGeoMaterialQuery(BaseModel):
    """
        Pydantic model for the query parameters of the Mindat API /v1/geomaterials/ endpoint.
        This model encapsulates the parameters used to filter geomaterial data.
        Example dictionary including all possible keys (all keys are optional):
        {
            "bi_max": "1.0",
            "bi_min": "0.1",
            "cleavagetype": ["Perfect", "Very Good"],
            "colour": "Blue",
            "crystal_system": ["Hexagonal"],
            "density_max": 4.5,
            "density_min": 2.5,
            "diapheny": ["Transparent"],
            "el_essential": True,
            "el_exc": ["Cl", "S"],
            "el_inc": ["Fe", "O", "Si"],
            "entrytype": [0, 1],
            "fracturetype": ["Conchoidal"],
            "hardness_max": 7.0,
            "hardness_min": 5.0,
            "ima": True,
            "ima_notes": [1, 2],
            "ima_status": [1],
            "lustretype": ["Vitreous"],
            "name": "Quartz",
            "optical2v_max": "90",
            "optical2v_min": "10",
            "opticalsign": "+",
            "opticaltype": "Uniaxial",  
            "ri_max": 1.7,
            "ri_min": 1.5,
            "streak": "White",
            "tenacity": ["brittle"],
        }
    """
    # Birifrigence
    bi_max: Optional[str] = Field(None, description="Birifrigence. Upper range (bi_min - bi_max). Calculated from refractive index as (rimax-rimin).")
    bi_min: Optional[str] = Field(None, description="Birifrigence. Lower range (bi_min - bi_max). Calculated from refractive index as (rimax-rimin).")
    
    # Cleavage
    cleavagetype: Optional[List[Literal[
        "Distinct/Good", "Imperfect/Fair", "None Observed", 
        "Perfect", "Poor/Indistinct", "Very Good"
    ]]] = Field(None, description="Cleavage: multiple choice.")
   
    # General properties
    colour: Optional[str] = Field(None, description="General colour search.")
    crystal_system: Optional[List[Literal[
        "Amorphous", "Hexagonal", "Icosahedral", "Isometric", 
        "Monoclinic", "Orthorhombic", "Tetragonal", "Triclinic", "Trigonal"
    ]]] = Field(
        None, 
        alias="csystem", 
        description="Crystal system (csystem): multiple choice (OR)."
    ) 
    
    # Density
    density_max: Optional[float] = Field(None, description="Density measured, to (dmeas<=).")
    density_min: Optional[float] = Field(None, description="Density measured, from (dmeas2>=).")
    
    # Diapheny (Transparency)
    diapheny: Optional[List[Literal[
        "Opaque", "Translucent", "Transparent"
    ]]] = Field(None, description="Diapheny (transparency): multiple choice (AND).")
    
    # Elements & Chemistry
    el_essential: Optional[bool] = Field(None, description="Chemsearch: include essential elements only? (true/false)")
    el_exc: Optional[List[str]] = Field(
        None, 
        description="Exclude minerals containing these elements and ions, comma separated."
    )
    el_inc: Optional[List[str]] = Field(
        None, 
        description="Include minerals containing these elements and ions, comma separated."
    )

    # Entry Type
    entrytype: Optional[List[int]] = Field(
        None, 
        description="Entry type. Multiple choice. Values: 0-mineral, 1-synonym, 7-rock, etc."
    ) 

    # Fracture
    fracturetype: Optional[List[Literal[
        "Conchoidal", "Fibrous", "Hackly", "Irregular/Uneven", 
        "Micaceous", "None observed", "Splintery", "Step-Like", "Sub-Conchoidal"
    ]]] = Field(None, description="Fracture: multiple choice (AND).")
    
    # Hardness (Mohs)
    # The API uses hmin for the max value and hmax for the min value in the query params.
    # We maintain this structure but use descriptive Pydantic names with aliases.
    hardness_max: Optional[float] = Field(
        None, 
        alias="hmin", 
        description="Mohs hardness to (hmin<=) - corresponds to API's hmin parameter."
    ) 
    hardness_min: Optional[float] = Field(
        None, 
        alias="hmax", 
        description="Mohs hardness from (hmax>=) - corresponds to API's hmax parameter."
    )
    
    # IMA Status
    ima: Optional[bool] = Field(
        None, 
        description="Include IMA-approved names only (true) / exclude IMA-approved (false)."
    )
    ima_notes: Optional[List[int]] = Field(
        None, 
        description="Ima notes: multiple choice (OR). Values include GROUP, INTERMEDIATE, PENDING_APPROVAL, etc."
    )
    ima_status: Optional[List[int]] = Field(
        None, 
        description="Ima status: multiple choice (OR). Values include APPROVED, DISCREDITED, GRANDFATHERED, etc."
    )
    
    # Lustre
    lustretype: Optional[List[Literal[
        "Adamantine", "Dull", "Earthy", "Greasy", "Metallic", 
        "Pearly", "Resinous", "Silky", "Sub-Adamantine", 
        "Sub-Metallic", "Sub-Vitreous", "Vitreous", "Waxy"
    ]]] = Field(None, description="Lustretype: multiple choice (AND).")
    

    # Name Search
    name: Optional[str] = Field(
        None, 
        description="Name. Text search supporting * and _ as wildcards, e.g. 'qu_rtz', 'bario*'."
    )
    
    # Optical Properties
    optical2v_max: Optional[str] = Field(None, description="2V upper range (optical2v_min - optical2v_max).")
    optical2v_min: Optional[str] = Field(None, description="2V lower range (optical2v_min - optical2v_max).")
    opticalsign: Optional[Literal[
        "+", "+/-", "-"
    ]] = Field(None, description="Optical sign: single choice (+, +/-, -).")
    opticaltype: Optional[Literal[
        "Biaxial", "Isotropic", "Uniaxial"
    ]] = Field(None, description="Optical type: single choice (Biaxial, Isotropic, Uniaxial).")

    # Refractive Index
    ri_max: Optional[float] = Field(None, description="Refractive index, to (rimin<=).")
    ri_min: Optional[float] = Field(None, description="Refractive index, from (rimax>=).")
    
    # Streak & Tenacity
    streak: Optional[str] = Field(None, description="Filter by streak colour.")
    tenacity: Optional[List[Literal[
        "brittle", "elastic", "flexible", "fragile", 
        "malleable", "sectile", "very brittle", "waxy"
    ]]] = Field(None, description="Tenacity: multiple choice (AND).")

    # Pydantic model configuration  for verison v2, it will allow population by field name and alias
    # eg : ri_min can be populated using 'ri_min' or 'rimin'
    model_config = ConfigDict(populate_by_name=True)


class MindatGeomaterialInput(BaseModel):
    query: MindatGeoMaterialQuery = Field(description="""
        Example dictionary including all possible keys (all keys are optional):
        {
            "bi_max": "1.0",
            "bi_min": "0.1",
            "cleavagetype": ["Perfect", "Very Good"],
            "colour": "Blue",
            "crystal_system": ["Hexagonal"],
            "density_max": 4.5,
            "density_min": 2.5,
            "diapheny": ["Transparent"],
            "el_essential": True,
            "el_exc": ["Cl", "S"],
            "el_inc": ["Fe", "O", "Si"],
            "entrytype": [0, 1],
            "fracturetype": ["Conchoidal"],
            "hardness_max": 7.0,
            "hardness_min": 5.0,
            "ima": True,
            "ima_notes": [1, 2],
            "ima_status": [1],
            "lustretype": ["Vitreous"],
            "name": "Quartz",
            "optical2v_max": "90",
            "optical2v_min": "10",
            "opticalsign": "+",
            "opticaltype": "Uniaxial",
            "ri_max": 1.7,
            "ri_min": 1.5,
            "streak": "White",
            "tenacity": ["brittle"],
        }
        """)













####################################
# Locality query model
####################################

class MindatLocalityQuery(BaseModel):
    """
    Pydantic model for the query parameters of the Mindat API /v1/localities/ endpoint.
    This model encapsulates the parameters used to filter locality data.
    """
    country: Optional[str] = Field(
        None, 
        description="Country or top level parent name (e.g. Brazil). Full list of options available in the API docs."
    )
    description: Optional[str] = Field(
        None, 
        description="Locality description contains this string."
    )
    elements_exc: Optional[List[str]] = Field(
        None, 
        alias="elements_exc", 
        description="Exclude chemical elements (e.g. 'Fe,Mg'), comma separated string."
    )
    elements_inc: Optional[List[str]] = Field(
        None, 
        alias="elements_inc", 
        description="Include chemical elements (e.g. 'Au,Ag'), comma separated string."
    )
    
    # pydantic model configuration
    # to allow population by field name and alias
    # eg : elements_inc can be populated using 'elements_inc' or 'el_inc'
    model_config = ConfigDict(populate_by_name=True)

class MindatLocalityInput(BaseModel):
    """
    Wrapper class for the Locality Query Model.
    This is used to encapsulate the query parameters for locality data collection.
    """
    query: MindatLocalityQuery = Field(description="""
        Example dicts, all of the keys are optional, leave blank if necessary:
        {
            "country": "Canada",  # Find localities within Canada
            "description": "British Columbia", # Locality description containing this string
            "elements_inc": ["Au", "Ag"],  # Must include Gold (Au) and Silver (Ag)
            "elements_exc": ["Pb", "Zn"]   # Exclude Lead (Pb) and Zinc (Zn)
        }
        """)