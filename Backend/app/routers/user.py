from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.schema import User as DBUser
from app.dependencies import get_current_user
from app.services.user_service import get_user_service
from app.models.user_models import UserResponse, UserUpdate
from typing import Optional, List
from uuid import UUID

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/user", response_model=List[UserResponse])
async def get_user(
    user_id: Optional[UUID] = Query(None, description="Search by exact user ID"),
    email: Optional[str] = Query(None, description="Search by email (fuzzy match, case-insensitive)"),
    full_name: Optional[str] = Query(None, description="Search by full name (fuzzy match, case-insensitive)"),
    db: DBSession = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    Get user information with fuzzy matching support.
    
    - **user_id**: Exact UUID match
    - **email**: Partial match (e.g., "john@" finds "john@example.com")
    - **full_name**: Partial match (e.g., "John" finds "John Doe", "John Smith")
    
    Returns a list of matching users.
    Priority: user_id > email > full_name
    
    Requires authentication.
    """
    try:
        # Validate that at least one search parameter is provided
        if not any([user_id, email, full_name]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one search parameter required: user_id, email, or full_name"
            )
        
        # Get user service and search with LIKE
        user_service = get_user_service(db)
        found_users = user_service.get_users_by_field_like(
            user_id=user_id,
            email=email,
            full_name=full_name
        )
        
        if not found_users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found matching the search criteria"
            )
        
        # Convert SQLAlchemy models to Pydantic UserResponse models
        return [UserResponse.model_validate(user) for user in found_users]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}"
        )


@router.patch("/user", response_model=UserResponse)
async def update_user_full_name(
    request: UserUpdate,
    current_user: DBUser = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Update current authenticated user's full name only.
    Email cannot be updated.
    """
    try:
        # Validate full_name is not empty
        if not request.full_name or not request.full_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="full_name cannot be empty"
            )
        
        # Use user service to update
        user_service = get_user_service(db)
        updated_user = user_service.update_user_full_name(current_user, request.full_name.strip())
        
        # Convert SQLAlchemy model to Pydantic UserResponse model
        return UserResponse.model_validate(updated_user)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )


@router.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    email: str = Query(..., description="Email of the user to delete"),
    current_user: DBUser = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """
    Delete a user by email.
    
    Warning: This is a destructive operation and cannot be undone.
    The user must be authenticated to delete any user.
    
    **email**: The email of the user to delete (required)
    
    Returns 204 No Content on successful deletion.
    """
    try:
        # Validate email is provided
        if not email or not email.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required for deletion"
            )
        
        # Get user service
        user_service = get_user_service(db)
        
        # Find user by email (exact match)
        user_to_delete = user_service.get_user_by_field(email=email.strip())
        
        if not user_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found with the provided email"
            )
        
        # Delete the user
        user_service.delete_user(user_to_delete)
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )
