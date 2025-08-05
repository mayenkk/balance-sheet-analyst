#!/usr/bin/env python3
"""
Sample script to demonstrate PDF processing workflow
This script shows how to process a balance sheet PDF and interact with the RAG system
"""

import os
import sys
import asyncio
import requests
import json
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStore
from app.services.ai_analysis import AIAnalysisService
from app.core.database import SessionLocal
from app.models.user import User, UserRole

class PDFProcessingDemo:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.vector_store = VectorStore()
        self.ai_service = AIAnalysisService()
        self.db = SessionLocal()
    
    def create_sample_user(self):
        """Create a sample user for testing"""
        # This would normally be done through the API
        # For demo purposes, we'll create a mock user
        user = User(
            id=1,
            email="demo@example.com",
            username="demo_user",
            full_name="Demo User",
            hashed_password="hashed_password",
            role=UserRole.ANALYST,
            is_active=True
        )
        return user
    
    def create_sample_pdf_content(self):
        """Create sample PDF content for demonstration"""
        sample_content = """
        RELIANCE INDUSTRIES LIMITED - BALANCE SHEET
        
        JIO PLATFORMS LIMITED
        Total Assets: ₹1,50,000 Crores
        Total Liabilities: ₹80,000 Crores
        Current Ratio: 1.8
        Debt-to-Equity: 0.6
        
        RELIANCE RETAIL VENTURES LIMITED
        Total Assets: ₹75,000 Crores
        Total Liabilities: ₹45,000 Crores
        Current Ratio: 1.5
        Debt-to-Equity: 0.8
        
        RELIANCE ENERGY
        Total Assets: ₹2,00,000 Crores
        Total Liabilities: ₹1,20,000 Crores
        Current Ratio: 1.2
        Debt-to-Equity: 1.1
        
        RELIANCE CHEMICALS
        Total Assets: ₹90,000 Crores
        Total Liabilities: ₹60,000 Crores
        Current Ratio: 1.6
        Debt-to-Equity: 0.7
        """
        return sample_content
    
    def save_sample_pdf(self, content, filename="sample_balance_sheet.pdf"):
        """Save sample content as a text file (simulating PDF)"""
        pdf_dir = Path("backend/pdfs")
        pdf_dir.mkdir(exist_ok=True)
        
        file_path = pdf_dir / filename
        
        # For demo purposes, we'll save as text
        # In real scenario, this would be a PDF file
        with open(file_path, "w") as f:
            f.write(content)
        
        return str(file_path)
    
    async def demo_pdf_processing(self):
        """Demonstrate the complete PDF processing workflow"""
        print("🚀 PDF Processing Demo")
        print("=" * 50)
        
        # Step 1: Create sample PDF content
        print("\n1️⃣ Creating sample balance sheet content...")
        sample_content = self.create_sample_pdf_content()
        pdf_path = self.save_sample_pdf(sample_content)
        print(f"✅ Sample content saved to: {pdf_path}")
        
        # Step 2: Process PDF and extract chunks by vertical
        print("\n2️⃣ Processing PDF and extracting chunks by vertical...")
        try:
            vertical_chunks = self.pdf_processor.process_balance_sheet_pdf(pdf_path, self.db)
            
            total_chunks = 0
            for vertical, chunks in vertical_chunks.items():
                if chunks:
                    print(f"   📊 {vertical.upper()}: {len(chunks)} chunks")
                    total_chunks += len(chunks)
            
            print(f"✅ Total chunks extracted: {total_chunks}")
            
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            return
        
        # Step 3: Store chunks in vector database
        print("\n3️⃣ Storing chunks in vector database...")
        storage_results = {}
        for vertical, chunks in vertical_chunks.items():
            if chunks:
                success = self.vector_store.store_chunks(vertical, chunks)
                storage_results[vertical] = success
                status = "✅" if success else "❌"
                print(f"   {status} {vertical.upper()}: {'Stored' if success else 'Failed'}")
        
        # Step 4: Test RAG-based queries
        print("\n4️⃣ Testing RAG-based queries...")
        user = self.create_sample_user()
        
        test_queries = [
            "What is the current ratio for JIO?",
            "How does the debt-to-equity ratio compare across verticals?",
            "What are the total assets for each vertical?",
            "Which vertical has the highest current ratio?"
        ]
        
        for query in test_queries:
            print(f"\n   🤔 Query: {query}")
            try:
                result = await self.ai_service.analyze_balance_sheet_query(
                    user=user,
                    query=query,
                    db=self.db
                )
                
                if "error" in result:
                    print(f"   ❌ Error: {result['error']}")
                else:
                    print(f"   ✅ Response: {result.get('summary', 'No summary available')}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Step 5: Show vector database health
        print("\n5️⃣ Vector database health check...")
        health = self.vector_store.health_check()
        print(f"   Status: {health.get('status', 'Unknown')}")
        print(f"   Embedding Model: {health.get('embedding_model', 'Unknown')}")
        
        for vertical, stats in health.get('collections', {}).items():
            status = stats.get('status', 'Unknown')
            count = stats.get('chunk_count', 0)
            print(f"   📊 {vertical.upper()}: {status} ({count} chunks)")
        
        print("\n🎉 Demo completed!")
        print("\n📋 Next Steps:")
        print("   1. Upload your actual balance sheet PDF")
        print("   2. Use the chat interface to ask questions")
        print("   3. Explore different user roles and access controls")
    
    def cleanup(self):
        """Clean up resources"""
        self.db.close()

async def main():
    """Main function to run the demo"""
    demo = PDFProcessingDemo()
    
    try:
        await demo.demo_pdf_processing()
    finally:
        demo.cleanup()

if __name__ == "__main__":
    print("PDF Processing Demo Script")
    print("This script demonstrates the RAG-based balance sheet analysis system")
    print()
    
    # Check if required directories exist
    if not os.path.exists("backend"):
        print("❌ Backend directory not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Run the demo
    asyncio.run(main()) 