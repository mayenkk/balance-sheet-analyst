from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.activity import ActivityList
from app.services.activity import ActivityService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/activities", tags=["activities"])
activity_service = ActivityService()


@router.get("/recent", response_model=ActivityList)
async def get_recent_activities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent activities based on user role and access"""
    
    try:
        activities = activity_service.get_recent_activities(current_user, limit=10, db=db)
        return activities
        
    except Exception as e:
        logger.error(f"Error getting recent activities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activities"
        )


@router.get("/user/{user_id}", response_model=ActivityList)
async def get_user_activities(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activities for a specific user (only accessible by group CEOs or the user themselves)"""
    
    # Check permissions
    if current_user.role != "group_ceo" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own activities"
        )
    
    try:
        activities = activity_service.get_user_activities(user_id, limit=20, db=db)
        return activities
        
    except Exception as e:
        logger.error(f"Error getting user activities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user activities"
        )


@router.get("/all", response_model=ActivityList)
async def get_all_activities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all activities across all users (only accessible by group CEOs)"""
    
    # Check permissions
    if current_user.role != "group_ceo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group CEOs can view all activities"
        )
    
    try:
        activities = activity_service.get_all_activities(limit=20, db=db)
        return activities
        
    except Exception as e:
        logger.error(f"Error getting all activities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve all activities"
        ) 