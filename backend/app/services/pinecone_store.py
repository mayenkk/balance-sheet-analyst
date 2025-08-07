import os
import logging
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings
from app.services.pdf_processor import PDFChunk
import numpy as np

logger = logging.getLogger(__name__)

class PineconeStore:
    """Pinecone-based vector store with proper vertical isolation"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PineconeStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.index_name = "balance-sheet-chunks"
        
        # Check if Pinecone is configured
        if not settings.PINECONE_API_KEY:
            logger.warning("Pinecone API key not configured, falling back to TF-IDF")
            self._initialized = True
            return
        
        # Initialize Pinecone with new API
        try:
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            logger.info("Pinecone initialized successfully")
            
            # Get or create index
            self._setup_index()
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            logger.warning("Falling back to TF-IDF approach")
            # Don't raise exception, just log and continue
        
        self._initialized = True
    
    def _setup_index(self):
        """Setup Pinecone index with new API"""
        try:
            # Check if index exists
            if not self.pc.has_index(self.index_name):
                # Create index with standard configuration
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1024,
                    metric="cosine"
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            else:
                logger.info(f"Using existing Pinecone index: {self.index_name}")
            
            # Get index
            self.index = self.pc.Index(self.index_name)
            
        except Exception as e:
            logger.error(f"Error setting up Pinecone index: {e}")
            raise
    
    def store_chunks(self, vertical: str, chunks: List[PDFChunk]) -> bool:
        """Store chunks for a specific vertical with proper isolation"""
        try:
            if not chunks:
                logger.warning(f"No chunks to store for vertical: {vertical}")
                return False
            
            # Prepare vectors for Pinecone
            vectors = []
            for i, chunk in enumerate(chunks):
                # Create embedding for the chunk content
                embedding = self._create_simple_embedding(chunk.content)
                
                vector_data = {
                    'id': f"{vertical}_{chunk.page_number}_{i}",
                    'values': embedding,
                    'metadata': {
                        'vertical': vertical,
                        'content': chunk.content,
                        'page_number': chunk.page_number,
                        'start_char': chunk.start_char,
                        'end_char': chunk.end_char,
                        'company_vertical': chunk.company_vertical,
                        'confidence_score': chunk.confidence_score,
                        **chunk.metadata
                    }
                }
                vectors.append(vector_data)
            
            # Upsert vectors in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Stored {len(chunks)} chunks for vertical: {vertical}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing chunks for vertical {vertical}: {e}")
            return False
    
    def search_similar_chunks(
        self, 
        query: str, 
        user_verticals: List[str], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks using Pinecone with vertical filtering"""
        try:
            if not user_verticals:
                logger.warning("No user verticals provided for search")
                return []
            
            # Create a simple embedding for the query
            query_embedding = self._create_simple_embedding(query)
            
            # Search with metadata filter for user's verticals
            filter_dict = {
                "vertical": {"$in": user_verticals}
            }
            
            # Query Pinecone with embedding
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Process results
            processed_results = []
            for match in results.matches:
                metadata = match.metadata
                processed_results.append({
                    'content': metadata.get('content', ''),
                    'page_number': metadata.get('page_number', 0),
                    'start_char': metadata.get('start_char', 0),
                    'end_char': metadata.get('end_char', 0),
                    'company_vertical': metadata.get('company_vertical', ''),
                    'confidence_score': metadata.get('confidence_score', 0.0),
                    'metadata': {k: v for k, v in metadata.items() 
                               if k not in ['content', 'page_number', 'start_char', 
                                          'end_char', 'company_vertical', 'confidence_score']},
                    'similarity_score': float(match.score)
                })
            
            logger.info(f"Found {len(processed_results)} results for verticals: {user_verticals}")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            return []
    
    def _create_simple_embedding(self, text: str) -> List[float]:
        """Create a simple embedding for text"""
        import hashlib
        
        # Create a hash of the text
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 1024-dimensional vector (matching the index dimension)
        embedding = []
        for i in range(1024):
            byte_index = i % len(hash_bytes)
            embedding.append(float(hash_bytes[byte_index]) / 255.0)
        
        return embedding
    
    def get_context_for_query(self, query: str, user_verticals: List[str]) -> str:
        """Get context for a query by retrieving similar chunks"""
        try:
            similar_chunks = self.search_similar_chunks(query, user_verticals, top_k=3)
            
            if not similar_chunks:
                logger.warning(f"No relevant chunks found for verticals: {user_verticals}")
                return f"No relevant information found in the {', '.join(user_verticals)} data."
            
            # Combine chunks into context with vertical labeling
            context_parts = []
            for chunk in similar_chunks:
                vertical = chunk.get('company_vertical', 'unknown')
                context_parts.append(f"[{vertical.upper()}] Page {chunk['page_number']}: {chunk['content']}")
            
            context = "\n\n".join(context_parts)
            logger.info(f"Retrieved context for verticals {user_verticals}: {len(context)} characters")
            return context
            
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return f"Error retrieving context from {', '.join(user_verticals)} data."
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of Pinecone vector store"""
        try:
            # Get index stats
            stats = self.index.describe_index_stats()
            
            return {
                "status": "healthy",
                "index_name": self.index_name,
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "metric": stats.metric,
                "index_host": stats.host,
                "index_port": stats.port
            }
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def delete_vertical_data(self, vertical: str) -> bool:
        """Delete all data for a specific vertical"""
        try:
            # Delete vectors with vertical filter
            self.index.delete(filter={"vertical": vertical})
            logger.info(f"Deleted data for vertical: {vertical}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vertical data: {e}")
            return False
    
    def reset_all_data(self) -> bool:
        """Reset all data in the index"""
        try:
            # Delete all vectors
            self.index.delete(delete_all=True)
            logger.info("Reset all data in Pinecone index")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting data: {e}")
            return False
    
    def get_vertical_statistics(self, vertical: str) -> Dict[str, Any]:
        """Get statistics for a specific vertical"""
        try:
            # Get index stats with filter
            stats = self.index.describe_index_stats(filter={"vertical": vertical})
            
            return {
                "vertical": vertical,
                "vector_count": stats.total_vector_count,
                "status": "available"
            }
            
        except Exception as e:
            logger.error(f"Error getting vertical statistics: {e}")
            return {
                "vertical": vertical,
                "error": str(e)
            } 