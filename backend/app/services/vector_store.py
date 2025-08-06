import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.config import settings
from app.services.pdf_processor import PDFChunk
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    """Simplified vector store using TF-IDF instead of sentence-transformers"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.chunks_by_vertical = {}
        self.tfidf_matrix = None
        self.feature_names = None

        # Ensure directory exists
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Try to load existing data
        self._load_persistent_data()
        
        self._initialized = True

    def _save_persistent_data(self):
        """Save vector store data to disk"""
        try:
            data = {
                'chunks_by_vertical': self.chunks_by_vertical,
                'tfidf_matrix': self.tfidf_matrix,
                'feature_names': self.feature_names
            }
            
            with open(os.path.join(self.persist_dir, 'vector_store.pkl'), 'wb') as f:
                pickle.dump(data, f)
            
            logger.info("Vector store data saved to disk")
        except Exception as e:
            logger.error(f"Error saving vector store data: {e}")

    def _load_persistent_data(self):
        """Load vector store data from disk"""
        try:
            file_path = os.path.join(self.persist_dir, 'vector_store.pkl')
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                
                self.chunks_by_vertical = data.get('chunks_by_vertical', {})
                self.tfidf_matrix = data.get('tfidf_matrix')
                self.feature_names = data.get('feature_names')
                
                logger.info(f"Loaded vector store data: {len(self.chunks_by_vertical)} verticals")
            else:
                logger.info("No persistent data found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading vector store data: {e}")
            # Start fresh if loading fails
            self.chunks_by_vertical = {}
            self.tfidf_matrix = None
            self.feature_names = None
    
    def store_chunks(self, vertical: str, chunks: List[PDFChunk]) -> bool:
        """Store chunks for a specific vertical"""
        try:
            if vertical not in self.chunks_by_vertical:
                self.chunks_by_vertical[vertical] = []

            self.chunks_by_vertical[vertical].extend(chunks)

            # Rebuild TF-IDF matrix
            self._rebuild_tfidf_matrix()
            
            # Save data persistently
            self._save_persistent_data()

            logger.info(f"Stored {len(chunks)} chunks for vertical: {vertical}")
            return True

        except Exception as e:
            logger.error(f"Error storing chunks for vertical {vertical}: {e}")
            return False
    
    def _rebuild_tfidf_matrix(self):
        """Rebuild TF-IDF matrix from all stored chunks"""
        try:
            all_texts = []
            for vertical, chunks in self.chunks_by_vertical.items():
                for chunk in chunks:
                    all_texts.append(chunk.content)
            
            if all_texts:
                self.tfidf_matrix = self.vectorizer.fit_transform(all_texts)
                self.feature_names = self.vectorizer.get_feature_names_out()
                logger.info(f"Rebuilt TF-IDF matrix with {len(all_texts)} documents")
            
        except Exception as e:
            logger.error(f"Error rebuilding TF-IDF matrix: {e}")
    
    def search_similar_chunks(
        self, 
        query: str, 
        user_verticals: List[str], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks using TF-IDF cosine similarity"""
        try:
            if self.tfidf_matrix is None or not self.chunks_by_vertical:
                logger.warning("No TF-IDF matrix or chunks available for search")
                return []
            
            # Transform query
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # Get all chunks with their indices
            all_chunks = []
            chunk_index = 0
            
            for vertical, chunks in self.chunks_by_vertical.items():
                if vertical in user_verticals:
                    for chunk in chunks:
                        all_chunks.append({
                            'chunk': chunk,
                            'similarity': similarities[chunk_index],
                            'vertical': vertical,
                            'index': chunk_index
                        })
                        chunk_index += 1
            
            # Sort by similarity and return top_k
            all_chunks.sort(key=lambda x: x['similarity'], reverse=True)
            
            results = []
            for item in all_chunks[:top_k]:
                chunk = item['chunk']
                results.append({
                    'content': chunk.content,
                    'page_number': chunk.page_number,
                    'start_char': chunk.start_char,
                    'end_char': chunk.end_char,
                    'company_vertical': chunk.company_vertical,
                    'confidence_score': chunk.confidence_score,
                    'metadata': chunk.metadata,
                    'similarity_score': float(item['similarity'])
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            return []
    
    def get_context_for_query(self, query: str, user_verticals: List[str]) -> str:
        """Get context for a query by retrieving similar chunks"""
        try:
            similar_chunks = self.search_similar_chunks(query, user_verticals, top_k=3)
            
            if not similar_chunks:
                return "No relevant information found in the balance sheet data."
            
            # Combine chunks into context
            context_parts = []
            for chunk in similar_chunks:
                context_parts.append(f"Page {chunk['page_number']}: {chunk['content']}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return "Error retrieving context from balance sheet data."
    
    def get_vertical_statistics(self, vertical: str) -> Dict[str, Any]:
        """Get statistics for a specific vertical"""
        try:
            if vertical not in self.chunks_by_vertical:
                return {"error": f"Vertical {vertical} not found"}
            
            chunks = self.chunks_by_vertical[vertical]
            
            return {
                "vertical": vertical,
                "total_chunks": len(chunks),
                "total_pages": len(set(chunk.page_number for chunk in chunks)),
                "avg_chunk_length": np.mean([len(chunk.content) for chunk in chunks]) if chunks else 0,
                "chunks_by_page": self._get_chunks_by_page(chunks)
            }
            
        except Exception as e:
            logger.error(f"Error getting vertical statistics: {e}")
            return {"error": str(e)}
    
    def _get_chunks_by_page(self, chunks: List[PDFChunk]) -> Dict[int, int]:
        """Get count of chunks per page"""
        page_counts = {}
        for chunk in chunks:
            page_counts[chunk.page_number] = page_counts.get(chunk.page_number, 0) + 1
        return page_counts
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of vector store"""
        try:
            total_chunks = sum(len(chunks) for chunks in self.chunks_by_vertical.values())
            total_verticals = len(self.chunks_by_vertical)
            
            # Check if data is persisted
            persist_file = os.path.join(self.persist_dir, 'vector_store.pkl')
            data_persisted = os.path.exists(persist_file)
            
            return {
                "status": "healthy",
                "total_chunks": total_chunks,
                "total_verticals": total_verticals,
                "verticals": list(self.chunks_by_vertical.keys()),
                "tfidf_matrix_built": self.tfidf_matrix is not None,
                "data_persisted": data_persisted,
                "persist_file_size": os.path.getsize(persist_file) if data_persisted else 0,
                "chunks_by_vertical": {k: len(v) for k, v in self.chunks_by_vertical.items()}
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
            if vertical in self.chunks_by_vertical:
                del self.chunks_by_vertical[vertical]
                self._rebuild_tfidf_matrix()
                logger.info(f"Deleted data for vertical: {vertical}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting vertical data: {e}")
            return False
    
    def reset_all_data(self) -> bool:
        """Reset all data in vector store"""
        try:
            self.chunks_by_vertical.clear()
            self.tfidf_matrix = None
            self.feature_names = None
            logger.info("Reset all vector store data")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting data: {e}")
            return False 