from pydantic import BaseModel
from typing import Optional
from datetime import date


class CompanyBase(BaseModel):
    name: str
    ticker_symbol: Optional[str] = None
    industry: str
    sector: str
    description: Optional[str] = None
    parent_company_id: Optional[int] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int
    
    class Config:
        from_attributes = True


class CompanyHierarchy(BaseModel):
    id: int
    name: str
    children: Optional[list] = None
    level: Optional[int] = None 