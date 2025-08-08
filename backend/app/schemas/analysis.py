from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

class FinancialAnalysisRequest(BaseModel):
    file_id: int

class FinancialAnalysisResponse(BaseModel):
    success: bool
    financial_data: Dict[str, Any]
    plots: Dict[str, str]  # Base64 encoded plot images
    insights: List[Dict[str, str]]
    file_name: str
    error: Optional[str] = None

class FinancialDataPoint(BaseModel):
    value: float
    unit: str

class FinancialMetric(BaseModel):
    sales: Optional[Dict[str, FinancialDataPoint]] = None
    growth_rate: Optional[Dict[str, FinancialDataPoint]] = None
    total_assets: Optional[Dict[str, FinancialDataPoint]] = None
    total_liabilities: Optional[Dict[str, FinancialDataPoint]] = None
    net_worth: Optional[Dict[str, FinancialDataPoint]] = None
    profit_margin: Optional[Dict[str, FinancialDataPoint]] = None
    debt_to_equity: Optional[Dict[str, FinancialDataPoint]] = None
    extracted_companies: List[str] = []
    accessible_companies: List[str] = []
    currency: str = "USD"
    data_quality: str = "unknown"

class Insight(BaseModel):
    type: str  # positive, warning, error
    title: str
    description: str

class PlotResponse(BaseModel):
    plot_type: str
    image_data: str  # Base64 encoded
    title: str
    description: str 