from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models.activity import Activity
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityResponse, ActivityList
import logging

logger = logging.getLogger(__name__)


class ActivityService:
    """Service for tracking and retrieving user activities"""
    
    async def log_activity(
        self,
        user_id: int,
        activity_type: str,
        title: str,
        description: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        activity_metadata: Optional[Dict[str, Any]] = None,
        db: Session = None
    ):
        """Log a user activity"""
        
        if not db:
            return
        
        try:
            activity = Activity(
                user_id=user_id,
                activity_type=activity_type,
                title=title,
                description=description,
                resource_type=resource_type,
                resource_id=resource_id,
                activity_metadata=activity_metadata
            )
            
            db.add(activity)
            db.commit()
            db.refresh(activity)
            
            logger.info(f"Logged activity: {activity_type} by user {user_id}")
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            db.rollback()
    
    def get_user_activities(
        self,
        user_id: int,
        limit: int = 10,
        db: Session = None
    ) -> ActivityList:
        """Get activities for a specific user"""
        
        if not db:
            return ActivityList(activities=[], total=0)
        
        activities = db.query(Activity).filter(
            Activity.user_id == user_id
        ).order_by(Activity.created_at.desc()).limit(limit).all()
        
        return ActivityList(
            activities=[ActivityResponse.from_orm(activity) for activity in activities],
            total=len(activities)
        )
    
    def get_all_activities(
        self,
        limit: int = 20,
        db: Session = None
    ) -> ActivityList:
        """Get all activities across all users (for group CEOs)"""
        
        if not db:
            return ActivityList(activities=[], total=0)
        
        activities = db.query(Activity).join(User).order_by(
            Activity.created_at.desc()
        ).limit(limit).all()
        
        return ActivityList(
            activities=[ActivityResponse.from_orm(activity) for activity in activities],
            total=len(activities)
        )
    
    def get_activities_by_type(
        self,
        activity_type: str,
        limit: int = 10,
        db: Session = None
    ) -> ActivityList:
        """Get activities of a specific type"""
        
        if not db:
            return ActivityList(activities=[], total=0)
        
        activities = db.query(Activity).filter(
            Activity.activity_type == activity_type
        ).order_by(Activity.created_at.desc()).limit(limit).all()
        
        return ActivityList(
            activities=[ActivityResponse.from_orm(activity) for activity in activities],
            total=len(activities)
        )
    
    def get_recent_activities(
        self,
        user: User,
        limit: int = 10,
        db: Session = None
    ) -> ActivityList:
        """Get recent activities based on user role and access"""
        
        if not db:
            return ActivityList(activities=[], total=0)
        
        # Group CEOs can see all activities
        if user.role == "group_ceo":
            return self.get_all_activities(limit, db)
        
        # Other users can only see their own activities
        return self.get_user_activities(user.id, limit, db) 