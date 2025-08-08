from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.uploaded_file import UploadedFile
from app.services.plotting_service import plotting_service
from app.services.pdf_processor import PDFProcessor
from app.schemas.analysis import FinancialAnalysisResponse, FinancialAnalysisRequest
from app.services.audit import AuditService
from app.services.activity import ActivityService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analysis", tags=["analysis"])

# Initialize services
audit_service = AuditService()
activity_service = ActivityService()

@router.get("/test")
async def test_analysis_router():
    """Test endpoint to verify router is working"""
    return {"message": "Analysis router is working"}

@router.post("/financial-analysis", response_model=FinancialAnalysisResponse)
async def generate_financial_analysis(
    request: FinancialAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate financial analysis and plots from an uploaded PDF that belongs to the current user"""
    try:
        # Strictly require the file to be uploaded by the current user
        uploaded_file = db.query(UploadedFile).filter(
            UploadedFile.id == request.file_id,
            UploadedFile.user_id == current_user.id
        ).first()

        if not uploaded_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or access denied"
            )

        # Extract text from PDF
        pdf_processor = PDFProcessor()
        pdf_content = pdf_processor._extract_text_from_pdf(uploaded_file.file_path)

        if not pdf_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to extract text from PDF"
            )

        # Generate financial analysis
        analysis_result = await plotting_service.generate_financial_analysis(
            pdf_content, current_user, db
        )

        if not analysis_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analysis_result.get("error", "Failed to generate analysis")
            )

        # Log the analysis
        await audit_service.log_action(
            user_id=current_user.id,
            action="financial_analysis",
            resource_type="uploaded_file",
            resource_id=uploaded_file.id,
            details={
                "file_name": uploaded_file.original_filename,
                "analysis_type": "financial_plots",
                "data_quality": analysis_result["financial_data"].get("data_quality", "unknown")
            },
            db=db
        )

        # Log activity
        await activity_service.log_activity(
            user_id=current_user.id,
            activity_type="financial_analysis",
            title=f"Financial Analysis: {uploaded_file.original_filename}",
            description="Generated financial plots and analysis from uploaded PDF",
            resource_type="uploaded_file",
            resource_id=uploaded_file.id,
            activity_metadata={
                "file_name": uploaded_file.original_filename,
                "plots_generated": len(analysis_result["plots"]),
                "insights_count": len(analysis_result["insights"]),
                "data_quality": analysis_result["financial_data"].get("data_quality", "unknown")
            },
            db=db
        )

        return FinancialAnalysisResponse(
            success=True,
            financial_data=analysis_result["financial_data"],
            plots=analysis_result["plots"],
            insights=analysis_result["insights"],
            file_name=uploaded_file.original_filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in financial analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate financial analysis: {str(e)}"
        )

@router.get("/available-files")
async def get_available_files_for_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of files available for financial analysis (only the current user's uploads)"""
    try:
        files = db.query(UploadedFile).filter(
            UploadedFile.user_id == current_user.id,
            UploadedFile.is_processed == True
        ).all()

        return {
            "files": [
                {
                    "id": file.id,
                    "name": file.original_filename,
                    "uploaded_at": file.created_at.isoformat(),
                    "file_size": file.file_size
                }
                for file in files
            ]
        }

    except Exception as e:
        logger.error(f"Error getting available files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available files"
        ) 