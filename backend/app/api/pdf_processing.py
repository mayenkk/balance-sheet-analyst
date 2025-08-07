from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import os
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.core.config import settings
from app.models.user import User
from app.models.uploaded_file import UploadedFile
from app.schemas.uploaded_file import UploadedFileResponse, UploadedFileList
from app.services.ai_analysis import AIAnalysisService
from app.services.pinecone_store import PineconeStore
from app.services.audit import AuditService
from app.services.activity import ActivityService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdf", tags=["pdf-processing"])
ai_service = AIAnalysisService()
audit_service = AuditService()
activity_service = ActivityService()

@router.post("/process")
async def process_balance_sheet_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process and store balance sheet PDF in vector database
    Analysts, CEOs, and top management can upload PDFs
    """
    
    # Check permissions - allow analysts, CEOs, and top management
    if current_user.role not in ["analyst", "group_ceo", "ceo", "top_management"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only analysts, CEOs, and top management can process PDFs"
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
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Save uploaded file record to database
        uploaded_file = UploadedFile(
            user_id=current_user.id,
            filename=file.filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            content_type=file.content_type or "application/pdf",
            processing_status="processing"
        )
        db.add(uploaded_file)
        db.commit()
        db.refresh(uploaded_file)
        
        # Process PDF and store in vector database
        result = await ai_service.process_pdf_and_store(file_path, db)
        
        # Update processing status
        uploaded_file.is_processed = True
        uploaded_file.processing_status = "completed"
        db.commit()
        
        # Log the action
        await audit_service.log_action(
            user_id=current_user.id,
            action="process_pdf",
            resource_type="pdf",
            details={
                "filename": file.filename,
                "file_size": len(content),
                "processing_result": result,
                "uploaded_file_id": uploaded_file.id
            },
            db=db
        )
        
        # Log activity
        await activity_service.log_activity(
            user_id=current_user.id,
            activity_type="pdf_upload",
            title=f"Uploaded {file.filename}",
            description=f"PDF file uploaded and processed successfully",
            resource_type="pdf",
            resource_id=uploaded_file.id,
            activity_metadata={
                "filename": file.filename,
                "file_size": len(content),
                "processing_result": result
            },
            db=db
        )
        
        return {
            "message": "PDF processed successfully",
            "result": result,
            "uploaded_file_id": uploaded_file.id
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        
        # Update processing status to failed
        if 'uploaded_file' in locals():
            uploaded_file.processing_status = "failed"
            uploaded_file.error_message = str(e)
            db.commit()
        
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

@router.get("/debug/vector-store")
async def debug_vector_store(
    current_user: User = Depends(get_current_user)
):
    """Debug endpoint to check vector store status"""
    
    health = ai_service.get_vector_store_health()
    user_verticals = ai_service._get_user_verticals(current_user)
    
    return {
        "vector_store_health": health,
        "user_verticals": user_verticals,
        "user_role": current_user.role,
        "user_companies": [c.name for c in current_user.companies]
    } 

@router.post("/test/load-sample-data")
async def load_sample_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Load sample data for testing"""
    
    # Check permissions
    if current_user.role not in ["analyst", "group_ceo"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only analysts and group CEOs can load test data"
        )
    
    try:
        # Create sample PDF content
        sample_content = """
        RELIANCE INDUSTRIES LIMITED - BALANCE SHEET
        
        JIO PLATFORMS LIMITED
        Total Assets: ₹1,50,000 Crores
        Total Liabilities: ₹80,000 Crores
        Current Ratio: 1.8
        Debt-to-Equity: 0.6
        
        RELIANCE RETAIL VENTURES LIMITED
        Total Assets: ₹75,000 Crores
        Total Liabilities: ₹45,000 Crores
        Current Ratio: 1.5
        Debt-to-Equity: 0.8
        
        RELIANCE ENERGY
        Total Assets: ₹2,00,000 Crores
        Total Liabilities: ₹1,20,000 Crores
        Current Ratio: 1.2
        Debt-to-Equity: 1.1
        
        RELIANCE CHEMICALS
        Total Assets: ₹90,000 Crores
        Total Liabilities: ₹60,000 Crores
        Current Ratio: 1.6
        Debt-to-Equity: 0.7
        """
        
        # Save sample content as text file
        os.makedirs(settings.PDF_UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.PDF_UPLOAD_DIR, "sample_balance_sheet.txt")
        
        with open(file_path, "w") as f:
            f.write(sample_content)
        
        # Process the sample data
        result = await ai_service.process_pdf_and_store(file_path, db)
        
        return {
            "message": "Sample data loaded successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load sample data: {str(e)}"
        ) 

@router.get("/uploaded-files", response_model=UploadedFileList)
async def get_uploaded_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all uploaded files for the current user"""
    
    files = db.query(UploadedFile).filter(
        UploadedFile.user_id == current_user.id
    ).order_by(UploadedFile.created_at.desc()).all()
    
    return UploadedFileList(
        files=[UploadedFileResponse.from_orm(file) for file in files],
        total=len(files)
    )

@router.get("/uploaded-files/{file_id}", response_model=UploadedFileResponse)
async def get_uploaded_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific uploaded file by ID"""
    
    file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return UploadedFileResponse.from_orm(file)

@router.get("/all-files", response_model=UploadedFileList)
async def get_all_uploaded_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all uploaded files across all users (for dashboard overview)"""
    # Only allow analysts and group CEOs to see all files
    if current_user.role not in ["analyst", "group_ceo"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only analysts and group CEOs can view all files"
        )
    
    files = db.query(UploadedFile).join(User).order_by(UploadedFile.created_at.desc()).all()
    return UploadedFileList(
        files=[UploadedFileResponse.from_orm(file) for file in files],
        total=len(files)
    )