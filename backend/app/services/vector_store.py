import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from app.core.config import settings
from app.services.pdf_processor import PDFChunk
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    """Service for managing vector embeddings and similarity search"""
    
    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        self.embedding_model = settings.EMBEDDING_MODEL
        self.top_k = settings.TOP_K_RESULTS
        self.similarity_threshold = settings.SIMILARITY_THRESHOLD
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        self.embedder = SentenceTransformer(self.embedding_model)
        
        # Create collections for different verticals
        self.collections = {}
        self._initialize_collections()
    
    def _initialize_collections(self):
        """Initialize ChromaDB collections for each vertical"""
        verticals = list(settings.VERTICAL_KEYWORDS.keys())
        
        for vertical in verticals:
            collection_name = f"balance_sheet_{vertical}"
            try:
                # Get or create collection
                collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"vertical": vertical, "description": f"Balance sheet data for {vertical}"}
                )
                self.collections[vertical] = collection
                logger.info(f"Initialized collection: {collection_name}")
            except Exception as e:
                logger.error(f"Error initializing collection {collection_name}: {e}")
    
    def store_chunks(self, vertical: str, chunks: List[PDFChunk]) -> bool:
        """
        Store PDF chunks in the vector database
        Returns: bool indicating success
        """
        if vertical not in self.collections:
            logger.error(f"Collection not found for vertical: {vertical}")
            return False
        
        try:
            collection = self.collections[vertical]
            
            # Prepare data for storage
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                # Create unique ID
                chunk_id = f"{vertical}_{chunk.page_number}_{i}"
                
                documents.append(chunk.content)
                metadatas.append({
                    "vertical": vertical,
                    "page_number": chunk.page_number,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "confidence_score": chunk.confidence_score,
                    "word_count": chunk.metadata.get("word_count", 0),
                    "chunk_index": chunk.metadata.get("chunk_index", i)
                })
                ids.append(chunk_id)
            
            # Add documents to collection
            if documents:
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"Stored {len(documents)} chunks for vertical: {vertical}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error storing chunks for vertical {vertical}: {e}")
            return False
    
    def search_similar_chunks(
        self, 
        query: str, 
        user_verticals: List[str], 
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks based on user's access permissions
        Returns: List of relevant chunks with metadata
        """
        if not top_k:
            top_k = self.top_k
        
        all_results = []
        
        for vertical in user_verticals:
            if vertical not in self.collections:
                continue
            
            try:
                collection = self.collections[vertical]
                
                # Search in this vertical's collection
                results = collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    include=["documents", "metadatas", "distances"]
                )
                
                # Process results
                if results['documents'] and results['documents'][0]:
                    for i, (doc, metadata, distance) in enumerate(zip(
                        results['documents'][0],
                        results['metadatas'][0],
                        results['distances'][0]
                    )):
                        # Convert distance to similarity score
                        similarity_score = 1 - distance
                        
                        if similarity_score >= self.similarity_threshold:
                            all_results.append({
                                "content": doc,
                                "metadata": metadata,
                                "similarity_score": similarity_score,
                                "vertical": vertical
                            })
                
            except Exception as e:
                logger.error(f"Error searching in vertical {vertical}: {e}")
        
        # Sort by similarity score and return top results
        all_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return all_results[:top_k]
    
    def get_context_for_query(
        self, 
        query: str, 
        user_verticals: List[str]
    ) -> str:
        """
        Get relevant context for a query based on user's access
        Returns: Formatted context string
        """
        relevant_chunks = self.search_similar_chunks(query, user_verticals)
        
        if not relevant_chunks:
            return "No relevant information found in the balance sheet data."
        
        # Build context string
        context_parts = []
        total_length = 0
        
        for chunk in relevant_chunks:
            chunk_text = f"[{chunk['vertical'].upper()} - Page {chunk['metadata']['page_number']}]\n{chunk['content']}\n"
            
            # Check if adding this chunk would exceed context limit
            if total_length + len(chunk_text) > settings.MAX_CONTEXT_LENGTH:
                break
            
            context_parts.append(chunk_text)
            total_length += len(chunk_text)
        
        return "\n".join(context_parts)
    
    def get_vertical_statistics(self, vertical: str) -> Dict[str, Any]:
        """
        Get statistics about stored data for a vertical
        Returns: Dict with statistics
        """
        if vertical not in self.collections:
            return {"error": f"Collection not found for vertical: {vertical}"}
        
        try:
            collection = self.collections[vertical]
            count = collection.count()
            
            return {
                "vertical": vertical,
                "total_chunks": count,
                "collection_name": collection.name
            }
        except Exception as e:
            logger.error(f"Error getting statistics for vertical {vertical}: {e}")
            return {"error": str(e)}
    
    def delete_vertical_data(self, vertical: str) -> bool:
        """
        Delete all data for a specific vertical
        Returns: bool indicating success
        """
        if vertical not in self.collections:
            return False
        
        try:
            collection = self.collections[vertical]
            collection.delete(where={"vertical": vertical})
            logger.info(f"Deleted data for vertical: {vertical}")
            return True
        except Exception as e:
            logger.error(f"Error deleting data for vertical {vertical}: {e}")
            return False
    
    def reset_all_data(self) -> bool:
        """
        Reset all vector database data
        Returns: bool indicating success
        """
        try:
            # Delete all collections
            for vertical in list(self.collections.keys()):
                collection_name = f"balance_sheet_{vertical}"
                self.client.delete_collection(collection_name)
                del self.collections[vertical]
            
            # Reinitialize collections
            self._initialize_collections()
            logger.info("Reset all vector database data")
            return True
        except Exception as e:
            logger.error(f"Error resetting vector database: {e}")
            return False
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding model"""
        return self.embedder.get_sentence_embedding_dimension()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on vector database
        Returns: Dict with health status
        """
        try:
            health_status = {
                "status": "healthy",
                "collections": {},
                "embedding_model": self.embedding_model,
                "embedding_dimension": self.get_embedding_dimension()
            }
            
            for vertical, collection in self.collections.items():
                try:
                    count = collection.count()
                    health_status["collections"][vertical] = {
                        "status": "healthy",
                        "chunk_count": count
                    }
                except Exception as e:
                    health_status["collections"][vertical] = {
                        "status": "error",
                        "error": str(e)
                    }
            
            return health_status
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            } 