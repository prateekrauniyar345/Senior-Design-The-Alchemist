from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.schema import User as DBUser
from app.dependencies import get_current_user
from app.services.profile_service import get_profile_service
from app.models.profile_models import ProfileResponse, ProfileUpdate
from typing import Optional, List
from uuid import UUID

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.get("/profile", response_model=List[ProfileResponse])
async def get_profile(
    profile_id: Optional[UUID] = Query(None, description="Search by exact profile ID"),
    full_name: Optional[str] = Query(None, description="Search by full name (fuzzy match, case-insensitive)"),
    db: DBSession = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    Get profile information with fuzzy matching support.
    
    - **profile_id**: Exact UUID match
    - **full_name**: Partial match (e.g., "John" finds "John Doe", "John Smith")
    
    Returns a list of matching profiles.
    Priority: profile_id > full_name
    
    Requires authentication.
    """
    try:
        # Validate that at least one search parameter is provided
        if not any([profile_id, full_name]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one search parameter required: profile_id or full_name"
            )
        
        # Get profile service and search with LIKE
        profile_service = get_profile_service(db)
        found_profiles = profile_service.get_profiles_by_field_like(
            profile_id=profile_id,
            full_name=full_name
        )
        
        if not found_profiles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No profiles found matching the search criteria"
            )
        
        # Convert SQLAlchemy models to Pydantic ProfileResponse models
        return [ProfileResponse.model_validate(profile) for profile in found_profiles]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching profile: {str(e)}"
        )


@router.patch("/profile", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdate,
    current_user: DBUser = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Update current authenticated user's profile.
    Only updates fields that are provided in the request.
    
    Fields that can be updated:
    - **full_name**: User's full name
    - **avatar_url**: Profile picture URL
    - **bio**: User's biography
    - **preferences**: User preferences as JSON object
    """
    try:
        # Get the current user's profile through relationship
        user_profile = current_user.profile
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found for current user"
            )
        
        # Get profile service and update
        profile_service = get_profile_service(db)
        updated_profile = profile_service.update_profile(
            profile=user_profile,
            full_name=request.full_name,
            avatar_url=request.avatar_url,
            bio=request.bio,
            preferences=request.preferences
        )
        
        # Convert SQLAlchemy model to Pydantic ProfileResponse model
        return ProfileResponse.model_validate(updated_profile)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )


@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    email: str = Query(..., description="Email of the user whose profile to delete"),
    current_user: DBUser = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Delete a profile by user email.
    
    Warning: This is a destructive operation and cannot be undone.
    The user must be authenticated to delete any profile.
    
    **email**: The email of the user whose profile to delete (required)
    
    Returns 204 No Content on successful deletion.
    """
    try:
        # Validate email is provided
        if not email or not email.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required for profile deletion"
            )
        
        # Get profile service
        profile_service = get_profile_service(db)
        
        # Delete profile by email
        profile_service.delete_profile_by_email(email.strip())
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting profile: {str(e)}"
        )
