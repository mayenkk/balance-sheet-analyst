from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    ticker_symbol = Column(String, unique=True, index=True)
    industry = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    description = Column(Text)
    parent_company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent_company = relationship("Company", remote_side=[id], backref="subsidiaries")
    users = relationship("User", secondary="user_companies", back_populates="companies")
    balance_sheets = relationship("BalanceSheet", back_populates="company")
    chat_sessions = relationship("ChatSession", back_populates="company")
    
    def get_all_subsidiaries(self):
        """Get all subsidiaries recursively"""
        subsidiaries = []
        for subsidiary in self.subsidiaries:
            subsidiaries.append(subsidiary)
            subsidiaries.extend(subsidiary.get_all_subsidiaries())
        return subsidiaries
    
    def get_hierarchy_level(self):
        """Get the hierarchy level of the company"""
        level = 0
        current = self
        while current.parent_company:
            level += 1
            current = current.parent_company
        return level 