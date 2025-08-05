from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatSessionCreate, 
    ChatSessionResponse, 
    ChatMessageCreate, 
    ChatMessageResponse, 
    AnalysisRequest, 
    AnalysisResponse
)
from app.services.ai_analysis import AIAnalysisService
from app.services.audit import AuditService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])
ai_service = AIAnalysisService()
audit_service = AuditService()

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    
    # Create chat session
    session = ChatSession(
        user_id=current_user.id,
        title=session_data.title,
        session_type=session_data.session_type
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Log the action
    await audit_service.log_action(
        user_id=current_user.id,
        action="create_chat_session",
        resource_type="chat_session",
        resource_id=session.id,
        db=db
    )
    
    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        session_type=session.session_type,
        is_active=session.is_active,
        created_at=session.created_at
    )

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for the current user"""
    
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.is_active == True
    ).order_by(ChatSession.updated_at.desc()).all()
    
    return [
        ChatSessionResponse(
            id=session.id,
            title=session.title,
            session_type=session.session_type,
            is_active=session.is_active,
            created_at=session.created_at
        )
        for session in sessions
    ]

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages in a chat session"""
    
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return [
        ChatMessageResponse(
            id=message.id,
            role=message.role,
            content=message.content,
            metadata=message.metadata,
            created_at=message.created_at
        )
        for message in messages
    ]

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    session_id: int,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a chat session and get AI response using RAG"""
    
    # Get chat session
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Save user message
    user_message = ChatMessage(
        session_id=session_id,
        role="user",
        content=message_data.content
    )
    db.add(user_message)
    db.commit()
    
    # Generate AI response using RAG
    try:
        analysis_result = await ai_service.analyze_balance_sheet_query(
            user=current_user,
            query=message_data.content,
            db=db
        )
        
        # Create AI response content
        ai_content = _format_ai_response(analysis_result)
        
        # Save AI message
        ai_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=ai_content,
            metadata=analysis_result
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        # Log the interaction
        await audit_service.log_action(
            user_id=current_user.id,
            action="chat_message",
            resource_type="chat_session",
            resource_id=session_id,
            details={
                "query": message_data.content,
                "verticals_accessed": analysis_result.get("verticals_accessed", []),
                "context_used": analysis_result.get("context_used", 0)
            },
            db=db
        )
        
        return ChatMessageResponse(
            id=ai_message.id,
            role=ai_message.role,
            content=ai_message.content,
            metadata=ai_message.metadata,
            created_at=ai_message.created_at
        )
        
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        # Save error message
        error_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=f"Sorry, I encountered an error while analyzing the data: {str(e)}"
        )
        db.add(error_message)
        db.commit()
        db.refresh(error_message)
        
        return ChatMessageResponse(
            id=error_message.id,
            role=error_message.role,
            content=error_message.content,
            metadata=None,
            created_at=error_message.created_at
        )

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_company(
    analysis_request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform direct analysis using RAG pipeline"""
    
    # Generate AI response using RAG
    try:
        analysis_result = await ai_service.analyze_balance_sheet_query(
            user=current_user,
            query=analysis_request.query,
            db=db
        )
        
        # Log the analysis
        await audit_service.log_action(
            user_id=current_user.id,
            action="direct_analysis",
            resource_type="analysis",
            details={
                "query": analysis_request.query,
                "verticals_accessed": analysis_result.get("verticals_accessed", []),
                "context_used": analysis_result.get("context_used", 0)
            },
            db=db
        )
        
        return AnalysisResponse(
            analysis=analysis_result,
            metrics=analysis_result.get("key_metrics", {}),
            insights=analysis_result.get("insights", []),
            balance_sheets_count=0  # Not applicable for RAG approach
        )
        
    except Exception as e:
        logger.error(f"Error in direct analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

def _format_ai_response(analysis_result: dict) -> str:
    """Format AI analysis result into readable text"""
    
    if "error" in analysis_result:
        return f"❌ **Error**: {analysis_result['error']}"
    
    response_parts = []
    
    # Summary
    if analysis_result.get("summary"):
        response_parts.append(f"📊 **Summary**: {analysis_result['summary']}")
    
    # Key Metrics
    if analysis_result.get("key_metrics"):
        response_parts.append("\n📈 **Key Metrics**:")
        for metric, value in analysis_result["key_metrics"].items():
            response_parts.append(f"• {metric}: {value}")
    
    # Insights
    if analysis_result.get("insights"):
        response_parts.append("\n💡 **Key Insights**:")
        for insight in analysis_result["insights"]:
            impact_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(insight.get("impact", "medium"), "🟡")
            response_parts.append(f"{impact_emoji} **{insight['title']}**: {insight['description']}")
    
    # Recommendations
    if analysis_result.get("recommendations"):
        response_parts.append("\n🎯 **Recommendations**:")
        for rec in analysis_result["recommendations"]:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec.get("priority", "medium"), "🟡")
            response_parts.append(f"{priority_emoji} **{rec['title']}**: {rec['description']}")
    
    # Risks
    if analysis_result.get("risks"):
        response_parts.append("\n⚠️ **Risks**:")
        for risk in analysis_result["risks"]:
            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk.get("severity", "medium"), "🟡")
            response_parts.append(f"{severity_emoji} **{risk['risk_type']}**: {risk['description']}")
    
    # Add metadata about data access
    if analysis_result.get("verticals_accessed"):
        response_parts.append(f"\n📋 *Analysis based on data from: {', '.join(analysis_result['verticals_accessed']).upper()}*")
    
    return "\n".join(response_parts) 