from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Union


####################################
# geomaterial query model
####################################
class MindatGeoMaterialQuery(BaseModel):
    """
    Pydantic model for the query parameters of the Mindat API /v1/geomaterials/ endpoint.
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

    # Field Selection
    expand: Optional[List[str]] = Field(None, description="Select fields to expand (e.g., 'description', 'locality', 'relations').")
    fields: Optional[str] = Field(None, description="Specify required fields by comma (e.g., 'id,name,mindat_formula').")
    omit: Optional[str] = Field(None, description="Specify omitted fields by comma.")
    
    
    # Fracture
    fracturetype: Optional[List[Literal[
        "Conchoidal", "Fibrous", "Hackly", "Irregular/Uneven", 
        "Micaceous", "None observed", "Splintery", "Step-Like", "Sub-Conchoidal"
    ]]] = Field(None, description="Fracture: multiple choice (AND).")
    
    # Group ID
    groupid: Optional[int] = Field(None, description="Mindat Group ID.")
    
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
    
    # Meteoritical
    meteoritical_code: Optional[str] = Field(
        None, 
        description="Meteoritical code. Text search supporting * and _ as wildcards."
    )
    meteoritical_code_exists: Optional[bool] = Field(
        None, 
        description="Meteoritical code exists. Include non-empty (true) / include empty only (false)."
    )
    
    # Name Search
    name: Optional[str] = Field(
        None, 
        description="Name. Text search supporting * and _ as wildcards, e.g. 'qu_rtz', 'bario*'."
    )
    non_utf: Optional[bool] = Field(None, description="Include non-UTF mineral names?")
    
    # Optical Properties
    optical2v_max: Optional[str] = Field(None, description="2V upper range (optical2v_min - optical2v_max).")
    optical2v_min: Optional[str] = Field(None, description="2V lower range (optical2v_min - optical2v_max).")
    opticalsign: Optional[Literal[
        "+", "+/-", "-"
    ]] = Field(None, description="Optical sign: single choice (+, +/-, -).")
    opticaltype: Optional[Literal[
        "Biaxial", "Isotropic", "Uniaxial"
    ]] = Field(None, description="Optical type: single choice (Biaxial, Isotropic, Uniaxial).")

    # Ordering and Pagination
    ordering: Optional[str] = Field(
        None, 
        description="Order the response by a field. Prepend '-' for descending order. Example: '-id'. Defaults include: 'name', 'id', 'updttime'."
    )
    page: Optional[int] = Field(None, description="A page number within the paginated result set.")
    page_size: Optional[int] = Field(
        None, 
        alias="page-size", 
        description="Number of results to return per page."
    )
    
    # Relationships
    polytypeof: Optional[int] = Field(None, description="Filter for polytypes of a geomaterial ID.")
    synid: Optional[int] = Field(None, description="Filter for synonyms of a geomaterial ID.")
    varietyof: Optional[int] = Field(None, description="Filter for varieties of a geomaterial ID.")

    # General Query
    q: Optional[str] = Field(None, description="A general search term.")
    
    # Refractive Index
    ri_max: Optional[float] = Field(None, description="Refractive index, to (rimin<=).")
    ri_min: Optional[float] = Field(None, description="Refractive index, from (rimax>=).")
    
    # Streak & Tenacity
    streak: Optional[str] = Field(None, description="Filter by streak colour.")
    tenacity: Optional[List[Literal[
        "brittle", "elastic", "flexible", "fragile", 
        "malleable", "sectile", "very brittle", "waxy"
    ]]] = Field(None, description="Tenacity: multiple choice (AND).")
    # Update Time
    updated_at: Optional[str] = Field(
        None, 
        description="Last updated datetime in format %Y-%m-%d %H:%M:%S."
    )
    class Config:
        """
        Configuration for the Pydantic model.
        - `allow_population_by_field_name = True` is important for passing 
          data to Pydantic using the snake_case field names (like `page_size`), 
          while the model ensures the correct API parameter name (`page-size`) 
          is used via the `alias`.
        """
        allow_population_by_field_name = True
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






####################################
# Locality query model
####################################

class MindatLocalityQuery(BaseModel):
    """
    Pydantic model for the query parameters of the Mindat API /v1/localities/ endpoint.
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
    class Config:
        """
        Configuration for the Pydantic model.
        - `allow_population_by_field_name = True` is necessary for 
          handling the `page-size` parameter using the `page_size` Python field.
        """
        allow_population_by_field_name = True

class MindatLocalityInput(BaseModel):
    """
    Wrapper class for the Locality Query Model.
    """
    query: MindatLocalityQuery = Field(description="""
        Example dicts, all of the keys are optional, leave blank if necessary:
        {
            "country": "Canada",  # Localities in Canada
            "txt": "Ontario",  # Locality name contains "Ontario"
            "elements_inc": ["Au"],  # Must include Gold (Au)
            "page_size": 50,  # Return 50 results per page
        }
        """)