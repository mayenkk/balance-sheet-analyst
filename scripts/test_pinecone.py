#!/usr/bin/env python3
"""
Script to test Pinecone integration and verify vertical isolation
"""

import sys
import os
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.services.pinecone_store import PineconeStore
from app.services.pdf_processor import PDFProcessor
from app.core.config import settings

def test_pinecone_integration():
    """Test Pinecone integration with vertical isolation"""
    
    print("🧪 Testing Pinecone Integration...")
    
    try:
        # Initialize Pinecone store
        pinecone_store = PineconeStore()
        print("✅ Pinecone store initialized successfully")
        
        # Test health check
        health = pinecone_store.health_check()
        print(f"📊 Health check: {health}")
        
        # Test with sample data
        print("\n📝 Testing with sample data...")
        
        # Create sample chunks for different verticals
        from app.services.pdf_processor import PDFChunk
        
        jio_chunks = [
            PDFChunk(
                content="JIO Platforms Limited - Total Assets: ₹1,50,000 Crores",
                page_number=1,
                start_char=0,
                end_char=50,
                company_vertical="jio",
                confidence_score=0.9,
                metadata={"source": "jio_balance_sheet"}
            ),
            PDFChunk(
                content="JIO Digital Services - Revenue: ₹25,000 Crores",
                page_number=2,
                start_char=0,
                end_char=45,
                company_vertical="jio",
                confidence_score=0.8,
                metadata={"source": "jio_balance_sheet"}
            )
        ]
        
        retail_chunks = [
            PDFChunk(
                content="Reliance Retail - Total Assets: ₹75,000 Crores",
                page_number=1,
                start_char=0,
                end_char=45,
                company_vertical="retail",
                confidence_score=0.9,
                metadata={"source": "retail_balance_sheet"}
            ),
            PDFChunk(
                content="Reliance Digital - Revenue: ₹15,000 Crores",
                page_number=2,
                start_char=0,
                end_char=40,
                company_vertical="retail",
                confidence_score=0.8,
                metadata={"source": "retail_balance_sheet"}
            )
        ]
        
        # Store chunks
        print("💾 Storing JIO chunks...")
        pinecone_store.store_chunks("jio", jio_chunks)
        
        print("💾 Storing Retail chunks...")
        pinecone_store.store_chunks("retail", retail_chunks)
        
        # Test search with vertical filtering
        print("\n🔍 Testing search with vertical filtering...")
        
        # Test JIO-only search
        jio_results = pinecone_store.search_similar_chunks(
            "What are the total assets?", 
            ["jio"], 
            top_k=3
        )
        print(f"JIO search results: {len(jio_results)} chunks")
        for result in jio_results:
            print(f"  - {result['content'][:50]}... (vertical: {result['company_vertical']})")
        
        # Test Retail-only search
        retail_results = pinecone_store.search_similar_chunks(
            "What are the total assets?", 
            ["retail"], 
            top_k=3
        )
        print(f"Retail search results: {len(retail_results)} chunks")
        for result in retail_results:
            print(f"  - {result['content'][:50]}... (vertical: {result['company_vertical']})")
        
        # Test cross-vertical search (should be empty for proper isolation)
        cross_results = pinecone_store.search_similar_chunks(
            "What are the total assets?", 
            ["jio"], 
            top_k=3
        )
        print(f"Cross-vertical search results: {len(cross_results)} chunks")
        
        # Verify isolation
        jio_verticals = set(result['company_vertical'] for result in jio_results)
        retail_verticals = set(result['company_vertical'] for result in retail_results)
        
        print(f"\n🔒 Vertical Isolation Test:")
        print(f"JIO results only contain: {jio_verticals}")
        print(f"Retail results only contain: {retail_verticals}")
        
        if jio_verticals == {"jio"} and retail_verticals == {"retail"}:
            print("✅ Vertical isolation working correctly!")
        else:
            print("❌ Vertical isolation failed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Pinecone integration: {e}")
        return False

if __name__ == "__main__":
    success = test_pinecone_integration()
    if success:
        print("\n🎉 Pinecone integration test completed successfully!")
    else:
        print("\n💥 Pinecone integration test failed!") 