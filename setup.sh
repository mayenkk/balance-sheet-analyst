#!/bin/bash

echo "🚀 Setting up Balance Sheet Analyst for Vercel deployment..."

# Python virtual environment setup
if [ ! -d ".venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "📦 Creating necessary directories..."
mkdir -p backend/pdfs
mkdir -p backend/chroma_db
mkdir -p backend/uploads

# Node.js dependencies for frontend
if [ -f frontend/package.json ]; then
    echo "🔧 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo "🔧 Setting up environment variables..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/balance_sheet_db
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Groq Configuration
GROQ_API_KEY=your-groq-api-key-here

# Gemini Configuration
GEMINI_API_KEY=your-gemini-api-key-here

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# File Upload
MAX_FILE_SIZE=52428800
UPLOAD_DIR=uploads
PDF_UPLOAD_DIR=pdfs

# PDF Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CHUNKS_PER_COMPANY=100

# Vector Database
CHROMA_PERSIST_DIR=chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# RAG Settings
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7
MAX_CONTEXT_LENGTH=8000
EOF
    echo "✅ Created .env file"
else
    echo "ℹ️  .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Access Information:"
echo "   Backend (local dev): cd backend && uvicorn app.main:app --reload"
echo "   Frontend (local dev): cd frontend && npm run dev"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "🔑 Default Login Credentials:"
echo "   Username: analyst"
echo "   Password: password"
echo ""
echo "📚 Next Steps:"
echo "   1. Get your Groq API key from https://console.groq.com/"
echo "   2. Add your Groq API key to the .env file"
echo "   3. Upload your balance sheet PDF using the PDF processing endpoint"
echo "   4. The system will automatically chunk and store data by vertical"
echo "   5. Start chatting with the AI about your balance sheet data"
echo ""
echo "🔧 PDF Processing Endpoints:"
echo "   POST /api/v1/pdf/process - Upload and process PDF"
echo "   GET /api/v1/pdf/health - Check vector database health"
echo "   GET /api/v1/pdf/access-info - View your access permissions"
echo ""
echo "💡 Example Usage:"
echo "   curl -X POST http://localhost:8000/api/v1/pdf/process \\"
echo "     -H 'Authorization: Bearer YOUR_TOKEN' \\"
echo "     -F 'file=@your_balance_sheet.pdf'"
echo "" 