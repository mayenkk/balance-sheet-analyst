from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    session_type = Column(String, default="analysis")  # analysis, qa, report
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    metadata = Column(JSON)  # Store AI analysis results, context info, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    report_type = Column(String, nullable=False)  # 'executive_summary', 'risk_analysis', etc.
    content = Column(Text, nullable=False)
    metadata = Column(JSON)  # Store analysis parameters, charts, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analysis_reports") 