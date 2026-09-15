from sqlalchemy.orm import Session as DBSession
from sqlalchemy.exc import SQLAlchemyError
from app.schema import Profile, User
from app.utils.custom_message import MindatAPIException, ErrorSeverity
from typing import Optional, List, Dict, Any
from uuid import UUID
from langsmith import traceable


class ProfileService:
    """Service for profile management operations"""
    
    def __init__(self, db: DBSession):
        self.db = db
    
    @traceable(run_type="retriever", name="get_profile_by_field")
    def get_profile_by_field(
        self,
        profile_id: Optional[UUID] = None,
        full_name: Optional[str] = None
    ) -> Optional[Profile]:
        """
        Get profile by any of the provided fields (exact match).
        Priority: profile_id > full_name
        
        Args:
            profile_id: Profile's UUID
            full_name: Profile's full name
            
        Returns:
            Profile object if found, None otherwise
        """
        try:
            if profile_id:
                return self.db.query(Profile).filter(Profile.id == profile_id).first()
            
            if full_name:
                return self.db.query(Profile).filter(Profile.full_name == full_name).first()
            
            return None
            
        except SQLAlchemyError as e:
            raise MindatAPIException(
                message=f"Database error while fetching profile: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.ERROR,
                details={"query_params": {"profile_id": str(profile_id), "full_name": full_name}}
            )
        except Exception as e:
            raise MindatAPIException(
                message=f"Error fetching profile: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.CRITICAL,
                details={}
            )

    @traceable(run_type="retriever", name="get_profiles_by_field_like")
    def get_profiles_by_field_like(
        self,
        profile_id: Optional[UUID] = None,
        full_name: Optional[str] = None
    ) -> List[Profile]:
        """
        Get profiles by fuzzy matching using SQL LIKE queries.
        - profile_id: exact match only (UUID)
        - full_name: case-insensitive LIKE match
        
        Priority: profile_id > full_name
        
        Args:
            profile_id: Profile's UUID (exact match)
            full_name: Name search pattern (LIKE)
            
        Returns:
            List of matching Profile objects
        """
        try:
            if profile_id:
                profile = self.db.query(Profile).filter(Profile.id == profile_id).first()
                return [profile] if profile else []
            
            if full_name:
                # Case-insensitive LIKE search for full_name
                search_pattern = f"%{full_name.strip()}%"
                return self.db.query(Profile).filter(Profile.full_name.ilike(search_pattern)).all()
            
            return []
            
        except SQLAlchemyError as e:
            raise MindatAPIException(
                message=f"Database error while searching profiles: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.ERROR,
                details={"query_params": {"profile_id": str(profile_id), "full_name": full_name}}
            )
        except Exception as e:
            raise MindatAPIException(
                message=f"Error searching profiles: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.CRITICAL,
                details={}
            )
    
    @traceable(run_type="chain", name="update_profile")
    def update_profile(
        self, 
        profile: Profile, 
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Profile:
        """
        Update profile fields.
        Only updates fields that are explicitly provided (not None).
        
        Args:
            profile: Profile object to update
            full_name: New full name (optional)
            avatar_url: New avatar URL (optional)
            bio: New bio (optional)
            preferences: New preferences JSON (optional)
            
        Returns:
            Updated Profile object
            
        Raises:
            MindatAPIException if update fails
        """
        try:
            if full_name is not None:
                profile.full_name = full_name
            if avatar_url is not None:
                profile.avatar_url = avatar_url
            if bio is not None:
                profile.bio = bio
            if preferences is not None:
                profile.preferences = preferences
            
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            return profile
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise MindatAPIException(
                message=f"Database error while updating profile: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.ERROR,
                details={"profile_id": str(profile.id)}
            )
        except Exception as e:
            self.db.rollback()
            raise MindatAPIException(
                message=f"Error updating profile: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.CRITICAL,
                details={"profile_id": str(profile.id)}
            )
    
    @traceable(run_type="chain", name="delete_profile_by_email")
    def delete_profile_by_email(self, email: str) -> None:
        """
        Delete a profile by user email.
        
        Args:
            email: User's email
            
        Raises:
            MindatAPIException if user or profile not found or deletion fails
        """
        try:
            # Find user by email
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                raise MindatAPIException(
                    message=f"User not found with email: {email}",
                    status_code=404,
                    severity=ErrorSeverity.ERROR,
                    details={"email": email}
                )
            
            # Get user's profile through relationship
            profile = user.profile
            if not profile:
                raise MindatAPIException(
                    message=f"Profile not found for user with email: {email}",
                    status_code=404,
                    severity=ErrorSeverity.ERROR,
                    details={"email": email}
                )
            
            # Delete the profile
            self.db.delete(profile)
            self.db.commit()
            
        except MindatAPIException:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise MindatAPIException(
                message=f"Database error while deleting profile: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.ERROR,
                details={"email": email}
            )
        except Exception as e:
            self.db.rollback()
            raise MindatAPIException(
                message=f"Error deleting profile: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.CRITICAL,
                details={"email": email}
            )


def get_profile_service(db: DBSession) -> ProfileService:
    """Factory function to get ProfileService instance"""
    return ProfileService(db)
