import openai
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.company import Company
from app.core.config import settings
from app.services.vector_store import VectorStore
from app.services.pdf_processor import PDFProcessor
import logging

logger = logging.getLogger(__name__)

# Configure OpenAI
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY

class AIAnalysisService:
    """Service for AI-powered balance sheet analysis using RAG pipeline"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.pdf_processor = PDFProcessor()
    
    async def analyze_balance_sheet_query(
        self, 
        user: User, 
        query: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Analyze balance sheet data using RAG pipeline
        Returns: Dict with analysis results
        """
        try:
            # Get user's accessible verticals
            user_verticals = self._get_user_verticals(user)
            
            if not user_verticals:
                return {
                    "error": "No accessible company data found for your role",
                    "insights": [],
                    "recommendations": [],
                    "charts": []
                }
            
            # Get relevant context from vector store
            context = self.vector_store.get_context_for_query(query, user_verticals)
            
            if not context or context == "No relevant information found in the balance sheet data.":
                return {
                    "error": "No relevant information found in the balance sheet data for your query",
                    "insights": [],
                    "recommendations": [],
                    "charts": []
                }
            
            # Create analysis prompt with context
            prompt = self._create_rag_analysis_prompt(query, context, user_verticals)
            
            # Get AI response
            response = await self._get_ai_response(prompt)
            
            # Parse and structure the response
            analysis_result = self._parse_ai_response(response)
            
            # Add metadata
            analysis_result["context_used"] = len(context)
            analysis_result["verticals_accessed"] = user_verticals
            analysis_result["query"] = query
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "insights": [],
                "recommendations": [],
                "charts": []
            }
    
    def _get_user_verticals(self, user: User) -> List[str]:
        """Get list of verticals user has access to based on role and company assignments"""
        if user.role == "analyst" or user.role == "group_ceo":
            # Full access to all verticals
            return list(settings.VERTICAL_KEYWORDS.keys())
        
        elif user.role == "ceo":
            # Access to assigned companies only
            user_verticals = []
            for company in user.companies:
                # Map company to vertical based on industry/sector
                vertical = self._map_company_to_vertical(company)
                if vertical and vertical not in user_verticals:
                    user_verticals.append(vertical)
            return user_verticals
        
        elif user.role == "top_management":
            # Limited access based on assignments
            user_verticals = []
            for company in user.companies:
                vertical = self._map_company_to_vertical(company)
                if vertical and vertical not in user_verticals:
                    user_verticals.append(vertical)
            return user_verticals
        
        return []
    
    def _map_company_to_vertical(self, company: Company) -> Optional[str]:
        """Map company to vertical based on industry/sector"""
        industry_lower = company.industry.lower()
        sector_lower = company.sector.lower()
        name_lower = company.name.lower()
        
        # Map based on keywords
        for vertical, keywords in settings.VERTICAL_KEYWORDS.items():
            for keyword in keywords:
                if (keyword.lower() in industry_lower or 
                    keyword.lower() in sector_lower or 
                    keyword.lower() in name_lower):
                    return vertical
        
        return None
    
    def _create_rag_analysis_prompt(
        self, 
        query: str, 
        context: str, 
        user_verticals: List[str]
    ) -> str:
        """Create prompt for RAG-based analysis"""
        
        prompt = f"""
You are a senior financial analyst with expertise in balance sheet analysis and corporate finance. 
You have access to balance sheet data from the following company verticals: {', '.join(user_verticals).upper()}.

Based on the following context from the balance sheet PDF, please provide a comprehensive analysis for the user's query.

CONTEXT FROM BALANCE SHEET:
{context}

USER QUERY: {query}

Please provide your analysis in the following JSON format:
{{
    "summary": "Brief summary of the analysis",
    "insights": [
        {{
            "title": "Insight title",
            "description": "Detailed insight description",
            "impact": "high/medium/low",
            "evidence": "Supporting evidence from the data"
        }}
    ],
    "recommendations": [
        {{
            "title": "Recommendation title",
            "description": "Detailed recommendation",
            "priority": "high/medium/low",
            "rationale": "Why this recommendation is important"
        }}
    ],
    "key_metrics": {{
        "metric_name": "value or trend description"
    }},
    "risks": [
        {{
            "risk_type": "Type of risk",
            "description": "Risk description",
            "severity": "high/medium/low"
        }}
    ]
}}

Focus on providing actionable insights and clear recommendations based on the available data. 
If the context doesn't contain enough information to answer the query comprehensively, 
acknowledge the limitations and provide insights based on what is available.
"""
        
        return prompt
    
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from OpenAI API"""
        if not settings.OPENAI_API_KEY:
            raise Exception("OpenAI API key not configured")
        
        try:
            response = openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior financial analyst with expertise in balance sheet analysis and corporate finance. Provide clear, actionable insights based on the provided context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"Failed to get AI response: {str(e)}")
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract structured data"""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                parsed_response = json.loads(json_str)
                
                # Ensure all required fields are present
                return {
                    "summary": parsed_response.get("summary", ""),
                    "insights": parsed_response.get("insights", []),
                    "recommendations": parsed_response.get("recommendations", []),
                    "key_metrics": parsed_response.get("key_metrics", {}),
                    "risks": parsed_response.get("risks", []),
                    "charts": []  # Will be populated if needed
                }
            else:
                # Fallback: return as text
                return {
                    "summary": response,
                    "insights": [],
                    "recommendations": [],
                    "key_metrics": {},
                    "risks": [],
                    "charts": []
                }
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return {
                "summary": response,
                "insights": [],
                "recommendations": [],
                "key_metrics": {},
                "risks": [],
                "charts": []
            }
    
    async def process_pdf_and_store(
        self, 
        pdf_path: str, 
        db: Session
    ) -> Dict[str, Any]:
        """
        Process PDF and store chunks in vector database
        Returns: Dict with processing results
        """
        try:
            # Validate PDF
            validation = self.pdf_processor.validate_pdf_structure(pdf_path)
            if not validation["is_valid"]:
                return {
                    "success": False,
                    "error": f"PDF validation failed: {validation['errors']}"
                }
            
            # Process PDF and extract chunks by vertical
            vertical_chunks = self.pdf_processor.process_balance_sheet_pdf(pdf_path, db)
            
            # Store chunks in vector database
            storage_results = {}
            total_chunks = 0
            
            for vertical, chunks in vertical_chunks.items():
                if chunks:
                    success = self.vector_store.store_chunks(vertical, chunks)
                    storage_results[vertical] = {
                        "success": success,
                        "chunks_stored": len(chunks)
                    }
                    total_chunks += len(chunks)
                else:
                    storage_results[vertical] = {
                        "success": False,
                        "chunks_stored": 0,
                        "error": "No chunks extracted"
                    }
            
            return {
                "success": True,
                "total_chunks": total_chunks,
                "vertical_results": storage_results,
                "validation": validation
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_vector_store_health(self) -> Dict[str, Any]:
        """Get health status of vector store"""
        return self.vector_store.health_check()
    
    def get_vertical_statistics(self, vertical: str) -> Dict[str, Any]:
        """Get statistics for a specific vertical"""
        return self.vector_store.get_vertical_statistics(vertical) 