from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatSessionBase(BaseModel):
    title: str
    session_type: str = "analysis"


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionResponse(ChatSessionBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    message_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    query: str


class AnalysisResponse(BaseModel):
    analysis: Dict[str, Any]
    metrics: Dict[str, Any]
    insights: List[Dict[str, Any]]
    balance_sheets_count: int


class Insight(BaseModel):
    title: str
    description: str
    impact: str
    trend: str


class Recommendation(BaseModel):
    title: str
    description: str
    priority: str
    action_items: List[str]


class ChartConfig(BaseModel):
    type: str
    title: str
    description: str
    data_keys: List[str] 