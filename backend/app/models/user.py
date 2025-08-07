from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    ANALYST = "analyst"
    CEO = "ceo"
    GROUP_CEO = "group_ceo"
    TOP_MANAGEMENT = "top_management"


# Association table for user-company relationships
user_companies = Table(
    'user_companies',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('company_id', Integer, ForeignKey('companies.id'))
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default=UserRole.ANALYST)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    companies = relationship("Company", secondary=user_companies, back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    analysis_reports = relationship("AnalysisReport", back_populates="user")
    uploaded_files = relationship("UploadedFile", back_populates="user")
    activities = relationship("Activity", back_populates="user")
    
    def has_access_to_company(self, company_id: int) -> bool:
        """Check if user has access to a specific company"""
        if self.role == UserRole.ANALYST or self.role == UserRole.GROUP_CEO:
            return True
        return any(company.id == company_id for company in self.companies) 