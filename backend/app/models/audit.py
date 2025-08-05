from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String, nullable=False)  # login, logout, view, create, update, delete
    resource_type = Column(String, nullable=False)  # balance_sheet, company, report, etc.
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON)  # Additional context about the action
    ip_address = Column(String(45))
    user_agent = Column(Text)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class DataAccessLog(Base):
    __tablename__ = "data_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    access_type = Column(String, nullable=False)  # view, export, analyze
    data_type = Column(String, nullable=False)  # balance_sheet, financial_metrics, etc.
    record_count = Column(Integer, default=0)
    access_duration_ms = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    company = relationship("Company") 