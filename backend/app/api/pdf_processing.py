from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any
import os
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.core.config import settings
from app.models.user import User
from app.services.ai_analysis import AIAnalysisService
from app.services.audit import AuditService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdf", tags=["pdf-processing"])
ai_service = AIAnalysisService()
audit_service = AuditService()

@router.post("/process")
async def process_balance_sheet_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process and store balance sheet PDF in vector database
    Only analysts and group CEOs can upload PDFs
    """
    
    # Check permissions
    if current_user.role not in ["analyst", "group_ceo"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only analysts and group CEOs can process PDFs"
        )
    
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    try:
        # Create upload directory if it doesn't exist
        os.makedirs(settings.PDF_UPLOAD_DIR, exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(settings.PDF_UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process PDF and store in vector database
        result = await ai_service.process_pdf_and_store(file_path, db)
        
        # Log the action
        await audit_service.log_action(
            user_id=current_user.id,
            action="process_pdf",
            resource_type="pdf",
            details={
                "filename": file.filename,
                "file_size": len(content),
                "processing_result": result
            },
            db=db
        )
        
        return {
            "message": "PDF processed successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF: {str(e)}"
        )

@router.get("/health")
async def get_vector_store_health(
    current_user: User = Depends(get_current_user)
):
    """Get health status of vector database"""
    
    health_status = ai_service.get_vector_store_health()
    return health_status

@router.get("/statistics/{vertical}")
async def get_vertical_statistics(
    vertical: str,
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a specific vertical"""
    
    # Check if user has access to this vertical
    user_verticals = ai_service._get_user_verticals(current_user)
    if vertical not in user_verticals:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this vertical"
        )
    
    stats = ai_service.get_vertical_statistics(vertical)
    return stats

@router.delete("/vertical/{vertical}")
async def delete_vertical_data(
    vertical: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete all data for a specific vertical
    Only analysts and group CEOs can delete data
    """
    
    # Check permissions
    if current_user.role not in ["analyst", "group_ceo"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only analysts and group CEOs can delete data"
        )
    
    try:
        success = ai_service.vector_store.delete_vertical_data(vertical)
        
        if success:
            # Log the action
            await audit_service.log_action(
                user_id=current_user.id,
                action="delete_vertical_data",
                resource_type="vertical",
                resource_id=vertical,
                db=db
            )
            
            return {"message": f"Data for vertical '{vertical}' deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete data for vertical '{vertical}'"
            )
            
    except Exception as e:
        logger.error(f"Error deleting vertical data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete vertical data: {str(e)}"
        )

@router.post("/reset")
async def reset_vector_database(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset all vector database data
    Only group CEOs can reset the entire database
    """
    
    # Check permissions
    if current_user.role != "group_ceo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group CEOs can reset the vector database"
        )
    
    try:
        success = ai_service.vector_store.reset_all_data()
        
        if success:
            # Log the action
            await audit_service.log_action(
                user_id=current_user.id,
                action="reset_vector_database",
                resource_type="database",
                details={"reset_all": True},
                db=db
            )
            
            return {"message": "Vector database reset successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset vector database"
            )
            
    except Exception as e:
        logger.error(f"Error resetting vector database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset vector database: {str(e)}"
        )

@router.get("/access-info")
async def get_user_access_info(
    current_user: User = Depends(get_current_user)
):
    """Get information about user's access to different verticals"""
    
    user_verticals = ai_service._get_user_verticals(current_user)
    
    access_info = {
        "user_role": current_user.role,
        "accessible_verticals": user_verticals,
        "total_verticals": len(settings.VERTICAL_KEYWORDS),
        "vertical_keywords": settings.VERTICAL_KEYWORDS
    }
    
    return access_info 