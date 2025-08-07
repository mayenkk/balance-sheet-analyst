import asyncio
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
from app.services.activity import ActivityService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])
ai_service = AIAnalysisService()
audit_service = AuditService()
activity_service = ActivityService()

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    
    try:
        # Create chat session
        session = ChatSession(
            user_id=current_user.id,
            title=session_data.title,
            session_type=session_data.session_type
        )

        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"Created chat session {session.id} for user {current_user.id}")

        # Log the action
        try:
            await audit_service.log_action(
                user_id=current_user.id,
                action="create_chat_session",
                resource_type="chat_session",
                resource_id=session.id,
                db=db
            )
        except Exception as audit_error:
            logger.error(f"Audit logging failed: {audit_error}")

        # Log activity
        try:
            await activity_service.log_activity(
                user_id=current_user.id,
                activity_type="chat_session",
                title=f"Created chat session: {session_data.title}",
                description="New AI chat session started",
                resource_type="chat_session",
                resource_id=session.id,
                activity_metadata={
                    "session_type": session_data.session_type,
                    "title": session_data.title
                },
                db=db
            )
        except Exception as activity_error:
            logger.error(f"Activity logging failed: {activity_error}")

        return ChatSessionResponse(
            id=session.id,
            title=session.title,
            session_type=session.session_type,
            is_active=session.is_active,
            created_at=session.created_at
        )
        
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chat session: {str(e)}"
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
            role=message.message_type,  # Use message_type instead of role
            content=message.content,
            message_metadata=message.message_metadata,
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
        user_id=current_user.id,
        content=message_data.content,
        message_type="user"
    )
    db.add(user_message)
    db.commit()

    # Generate AI response using RAG
    try:
        logger.info(f"Starting AI analysis for session {session_id}, user: {current_user.username}")
        
        # Add timeout to AI analysis
        analysis_result = await asyncio.wait_for(
            ai_service.analyze_balance_sheet_query(
                user=current_user,
                query=message_data.content,
                db=db
            ),
            timeout=90.0  # Increased timeout to 90 seconds for complex queries
        )

        logger.info(f"AI analysis completed for session {session_id}")

        # Create AI response content
        ai_content = _format_ai_response(analysis_result)

        # Save AI message
        ai_message = ChatMessage(
            session_id=session_id,
            user_id=current_user.id,
            content=ai_content,
            message_type="assistant",
            message_metadata=analysis_result
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)

        logger.info(f"AI message saved for session {session_id}")

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

        # Log activity
        await activity_service.log_activity(
            user_id=current_user.id,
            activity_type="chat_message",
            title=f"AI Analysis: {message_data.content[:50]}...",
            description="AI analysis completed for financial query",
            resource_type="chat_session",
            resource_id=session_id,
            activity_metadata={
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
            message_metadata=ai_message.message_metadata,
            created_at=ai_message.created_at
        )

    except asyncio.TimeoutError:
        logger.error(f"AI analysis timed out for session {session_id}")
        # Save timeout message
        timeout_message = ChatMessage(
            session_id=session_id,
            user_id=current_user.id,
            content="I'm taking longer than expected to analyze the data. This can happen with complex financial queries. Please try again in a moment or rephrase your question to be more specific.",
            message_type="assistant"
        )
        db.add(timeout_message)
        db.commit()
        db.refresh(timeout_message)

        return ChatMessageResponse(
            id=timeout_message.id,
            role=timeout_message.message_type,
            content=timeout_message.content,
            message_metadata=None,
            created_at=timeout_message.created_at
        )
    except Exception as e:
        logger.error(f"Error generating AI response for session {session_id}: {e}")
        # Save error message
        error_message = ChatMessage(
            session_id=session_id,
            user_id=current_user.id,
            content="Sorry, I encountered an error while analyzing the data. Please try again or contact support if the issue persists.",
            message_type="assistant"
        )
        db.add(error_message)
        db.commit()
        db.refresh(error_message)

        return ChatMessageResponse(
            id=error_message.id,
            role=error_message.message_type,
            content=error_message.content,
            message_metadata=None,
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
        # Add timeout to AI analysis
        analysis_result = await asyncio.wait_for(
            ai_service.analyze_balance_sheet_query(
                user=current_user,
                query=analysis_request.query,
                db=db
            ),
            timeout=30.0  # 30 second timeout
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

    except asyncio.TimeoutError:
        logger.error(f"AI analysis timed out for direct analysis")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Analysis timed out. Please try again."
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