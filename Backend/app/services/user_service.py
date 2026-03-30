from sqlalchemy.orm import Session as DBSession
from sqlalchemy.exc import SQLAlchemyError
from app.schema import User
from app.utils.custom_message import MindatAPIException, ErrorSeverity
from typing import Optional, List
from uuid import UUID
from langsmith import traceable


class UserService:
    """Service for user management operations"""
    
    def __init__(self, db: DBSession):
        self.db = db
    
    @traceable(run_type="retriever", name="get_user_by_field")
    def get_user_by_field(
        self,
        user_id: Optional[UUID] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None
    ) -> Optional[User]:
        """
        Get user by any of the provided fields (exact match).
        Priority: user_id > email > full_name
        
        Args:
            user_id: User's UUID
            email: User's email
            full_name: User's full name
            
        Returns:
            User object if found, None otherwise
        """
        try:
            if user_id:
                return self.db.query(User).filter(User.id == user_id).first()
            
            if email:
                return self.db.query(User).filter(User.email == email).first()
            
            if full_name:
                return self.db.query(User).filter(User.full_name == full_name).first()
            
            return None
            
        except SQLAlchemyError as e:
            raise MindatAPIException(
                message=f"Database error while fetching user: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.ERROR,
                details={"query_params": {"user_id": str(user_id), "email": email, "full_name": full_name}}
            )
        except Exception as e:
            raise MindatAPIException(
                message=f"Error fetching user: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.CRITICAL,
                details={}
            )

    @traceable(run_type="retriever", name="get_users_by_field_like")
    def get_users_by_field_like(
        self,
        user_id: Optional[UUID] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None
    ) -> List[User]:
        """
        Get users by fuzzy matching using SQL LIKE queries.
        - user_id: exact match only (UUID)
        - email: case-insensitive LIKE match
        - full_name: case-insensitive LIKE match
        
        Priority: user_id > email > full_name
        
        Args:
            user_id: User's UUID (exact match)
            email: Email search pattern (LIKE)
            full_name: Name search pattern (LIKE)
            
        Returns:
            List of matching User objects
        """
        try:
            if user_id:
                user = self.db.query(User).filter(User.id == user_id).first()
                return [user] if user else []
            
            if email:
                # Case-insensitive LIKE search for email
                search_pattern = f"%{email.strip()}%"
                return self.db.query(User).filter(User.email.ilike(search_pattern)).all()
            
            if full_name:
                # Case-insensitive LIKE search for full_name
                search_pattern = f"%{full_name.strip()}%"
                return self.db.query(User).filter(User.full_name.ilike(search_pattern)).all()
            
            return []
            
        except SQLAlchemyError as e:
            raise MindatAPIException(
                message=f"Database error while searching users: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.ERROR,
                details={"query_params": {"user_id": str(user_id), "email": email, "full_name": full_name}}
            )
        except Exception as e:
            raise MindatAPIException(
                message=f"Error searching users: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.CRITICAL,
                details={}
            )
    
    @traceable(run_type="chain", name="update_user_full_name")
    def update_user_full_name(self, user: User, full_name: str) -> User:
        """
        Update user's full name.
        
        Args:
            user: User object to update
            full_name: New full name
            
        Returns:
            Updated User object
            
        Raises:
            MindatAPIException if update fails
        """
        try:
            user.full_name = full_name
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise MindatAPIException(
                message=f"Database error while updating user: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.ERROR,
                details={"user_id": str(user.id)}
            )
        except Exception as e:
            self.db.rollback()
            raise MindatAPIException(
                message=f"Error updating user: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.CRITICAL,
                details={"user_id": str(user.id)}
            )


def get_user_service(db: DBSession) -> UserService:
    """Factory function to get UserService instance"""
    return UserService(db)
