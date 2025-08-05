from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyHierarchy
from app.services.ai_analysis import AIAnalysisService
from app.services.audit import AuditService

router = APIRouter(prefix="/companies", tags=["companies"])
ai_service = AIAnalysisService()
audit_service = AuditService()

@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all companies user has access to"""
    if current_user.role in ["analyst", "group_ceo"]:
        companies = db.query(Company).all()
    else:
        companies = current_user.companies
    return [CompanyResponse(
        id=company.id,
        name=company.name,
        ticker_symbol=company.ticker_symbol,
        industry=company.industry,
        sector=company.sector,
        description=company.description,
        parent_company_id=company.parent_company_id
    ) for company in companies]

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if not current_user.has_access_to_company(company_id):
        raise HTTPException(status_code=403, detail="Access denied to this company")
    return CompanyResponse(
        id=company.id,
        name=company.name,
        ticker_symbol=company.ticker_symbol,
        industry=company.industry,
        sector=company.sector,
        description=company.description,
        parent_company_id=company.parent_company_id
    )

@router.post("/", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "analyst":
        raise HTTPException(status_code=403, detail="Only analysts can create companies")
    company = Company(**company_data.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return CompanyResponse(
        id=company.id,
        name=company.name,
        ticker_symbol=company.ticker_symbol,
        industry=company.industry,
        sector=company.sector,
        description=company.description,
        parent_company_id=company.parent_company_id
    )

@router.get("/{company_id}/balance-sheets")
async def get_company_balance_sheets(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get metadata for all balance sheet PDF chunks for a company (for quick review of past balance sheets)"""
    if not current_user.has_access_to_company(company_id):
        raise HTTPException(status_code=403, detail="Access denied to this company")
    # Use vector DB to get all chunks for this company/vertical
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    # Map company to vertical
    vertical = ai_service._map_company_to_vertical(company)
    if not vertical:
        return []
    # Get all chunk metadata for this vertical
    chunks = ai_service.vector_store.collections[vertical].get(include=["metadatas"])
    # Sort by page number or any available date metadata (if present)
    chunk_list = chunks["metadatas"] if "metadatas" in chunks else []
    # Optionally sort by a date field if present
    chunk_list.sort(key=lambda x: x.get("page_number", 0), reverse=True)
    return chunk_list 