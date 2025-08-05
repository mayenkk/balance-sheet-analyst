# Balance Sheet Analyst - AI-Powered Financial Analysis Platform

## Overview
A comprehensive AI-powered platform for balance sheet analysis, designed for financial analysts and top management to review company performance, generate insights, and make data-driven decisions using **RAG (Retrieval-Augmented Generation)** technology.

## 🚀 Key Features

### **Multi-User Authentication & Role-Based Access Control**
- **Analysts**: Full access to all company verticals and analysis tools
- **CEOs**: Company-specific access (e.g., JIO CEO sees only JIO data)
- **Group CEOs**: Access to all group companies (e.g., Ambani sees all Reliance companies)
- **Top Management**: Limited access to assigned companies

### **PDF-Based Balance Sheet Processing**
- **Intelligent PDF Parsing**: Automatically extracts and chunks balance sheet data
- **Vertical-Based Segmentation**: Separates data by company verticals (JIO, Retail, Energy, etc.)
- **Access Control**: Users only see data from their authorized verticals
- **No Manual Data Entry**: Direct PDF upload and processing

### **RAG-Powered AI Chat Interface**
- **Context-Aware Responses**: AI provides insights based on relevant PDF chunks
- **Natural Language Queries**: Ask questions in plain English
- **Real-time Analysis**: Instant responses with actionable insights
- **Source Attribution**: See which verticals and pages data comes from

### **Advanced Financial Analysis**
- **Trend Analysis**: Identify patterns and trends in financial data
- **Risk Assessment**: Automated risk identification and severity analysis
- **Performance Metrics**: Key financial ratios and indicators
- **Executive Summaries**: Concise reports for top management

### **Data Security & Audit**
- **Role-Based Access Control**: Granular permissions based on user roles
- **Comprehensive Audit Logging**: Track all user actions and data access
- **Secure API Endpoints**: JWT-based authentication and authorization
- **Data Encryption**: End-to-end security for sensitive financial data

## 🏗️ Technical Architecture

### **Backend (FastAPI + Python)**
- **Web Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Vector Database**: ChromaDB for RAG pipeline
- **PDF Processing**: PyMuPDF, pdfplumber for text extraction
- **AI Integration**: OpenAI GPT-4 with custom prompts
- **Authentication**: JWT with OAuth2
- **Caching**: Redis for performance optimization

### **Frontend (React + TypeScript)**
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS with responsive design
- **State Management**: React Query for server state
- **Charts**: Interactive financial visualizations
- **Real-time Chat**: Live chat interface with AI

### **AI/ML Stack**
- **RAG Pipeline**: ChromaDB + Sentence Transformers
- **Embedding Model**: all-MiniLM-L6-v2 for text embeddings
- **LLM**: OpenAI GPT-4 for intelligent analysis
- **Text Processing**: NLTK, spaCy for NLP tasks

### **Infrastructure**
- **Vercel**: For serverless deployment (frontend and backend)
- **Database**: PostgreSQL (cloud or managed)
- **Vector Store**: ChromaDB for semantic search

## 🚀 Quick Start

### **Prerequisites**
- Python 3.9+
- Node.js 18+
- PostgreSQL (local or managed)
- OpenAI API key (for AI features)

### **Local Development**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd balance-sheet-analyst
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure OpenAI API**
   ```bash
   # Edit .env file and add your OpenAI API key
   OPENAI_API_KEY=your-openai-api-key-here
   ```

4. **Start the backend (FastAPI)**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

5. **Start the frontend (React)**
   ```bash
   cd frontend
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### **Default Login Credentials**
- **Username**: `analyst`
- **Password**: `password`

## 🌐 Vercel Deployment

### **Backend (FastAPI) on Vercel**
- Use [Vercel Python Serverless Functions](https://vercel.com/docs/functions/serverless-functions/runtimes/python) or [Vercel's FastAPI integration](https://vercel.com/guides/deploying-fastapi-with-vercel) for deployment.
- Place your FastAPI app in `api/` or configure `vercel.json` for custom routing.
- Ensure all environment variables are set in the Vercel dashboard.
- Use managed PostgreSQL (e.g., Neon, Supabase, or Vercel Postgres) and Redis if needed.
- ChromaDB vector store should be cloud-hosted or use a managed vector DB.

### **Frontend (React) on Vercel**
- Deploy the `frontend/` directory as a Vercel project.
- Set environment variables in the Vercel dashboard for API URLs and keys.
- Configure rewrites/proxies if needed for API routes.

### **Environment Variables**
Set these in the Vercel dashboard for both frontend and backend:
- `DATABASE_URL`
- `REDIS_URL` (if used)
- `SECRET_KEY`
- `OPENAI_API_KEY`
- `CHROMA_PERSIST_DIR` (or use a cloud vector DB)

## 📊 Usage Guide

### **1. Upload Balance Sheet PDF**
```bash
curl -X POST http://localhost:8000/api/v1/pdf/process \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -F 'file=@your_balance_sheet.pdf'
```

### **2. Start AI Chat**
- Navigate to the Chat interface
- Ask questions like:
  - "What is the current ratio trend for JIO?"
  - "How does our debt-to-equity ratio compare to industry standards?"
  - "What are the key risks in our balance sheet?"
  - "Generate a liquidity analysis for the past 5 years"

### **3. Access Control Examples**
- **JIO CEO**: Can only see JIO-related data and insights
- **Group CEO**: Can see all Reliance companies' data
- **Analyst**: Full access to all verticals and analysis tools

## 🔧 API Endpoints

### **Authentication**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info

### **PDF Processing**
- `POST /api/v1/pdf/process` - Upload and process PDF
- `GET /api/v1/pdf/health` - Check vector database health
- `GET /api/v1/pdf/access-info` - View access permissions
- `DELETE /api/v1/pdf/vertical/{vertical}` - Delete vertical data

### **Chat & Analysis**
- `POST /api/v1/chat/sessions` - Create chat session
- `POST /api/v1/chat/sessions/{id}/messages` - Send message
- `POST /api/v1/chat/analyze` - Direct analysis

### **Companies**
- `GET /api/v1/companies` - List accessible companies
- `GET /api/v1/companies/{id}` - Get company details

## 🏗️ Project Structure

```
balance-sheet-analyst/
├── backend/
│   ├── app/
│   │   ├── api/                 # API endpoints
│   │   ├── core/               # Core configuration
│   │   ├── models/             # Database models
│   │   ├── schemas/            # Pydantic schemas
│   │   └── services/           # Business logic
│   │       ├── ai_analysis.py  # RAG-based AI analysis
│   │       ├── pdf_processor.py # PDF processing
│   │       ├── vector_store.py # Vector database
│   │       └── audit.py        # Audit logging
│   ├── pdfs/                   # PDF upload directory
│   ├── chroma_db/              # Vector database storage
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   └── contexts/          # React contexts
│   └── package.json           # Node.js dependencies
├── setup.sh                   # Setup script
└── README.md                  # This file
```

## 🔒 Security Features

### **Access Control**
- **Role-Based Permissions**: Different access levels based on user roles
- **Company-Specific Access**: CEOs only see their company's data
- **Vertical Segmentation**: Data automatically separated by business verticals
- **Audit Trail**: Complete logging of all data access and actions

### **Data Protection**
- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for password security
- **CORS Protection**: Configured for secure cross-origin requests
- **Input Validation**: Comprehensive data validation with Pydantic

## 📈 Performance Features

### **RAG Pipeline**
- **Semantic Search**: Find relevant context using embeddings
- **Chunking Strategy**: Intelligent text chunking with overlap
- **Similarity Thresholds**: Configurable relevance filtering
- **Context Length Management**: Optimized for token limits

### **Caching & Optimization**
- **Redis Caching**: Fast response times for repeated queries
- **Vector Indexing**: Efficient similarity search
- **Connection Pooling**: Optimized database connections
- **Async Processing**: Non-blocking operations

## 🧪 Testing

### **Backend Tests**
```bash
cd backend
pytest tests/
```

### **Frontend Tests**
```bash
cd frontend
npm test
```

## 🚀 Deployment

### **Production Setup (Vercel)**
1. Push your code to a GitHub/GitLab repo
2. Import the repo into Vercel (for both frontend and backend)
3. Set environment variables in the Vercel dashboard
4. Use managed PostgreSQL and vector DB (ChromaDB or similar)
5. Configure custom domains and SSL as needed

### **Environment Variables**
```bash
# Required
DATABASE_URL=postgresql://user:pass@host:port/db
OPENAI_API_KEY=your-openai-key
SECRET_KEY=your-secret-key

# Optional
REDIS_URL=redis://host:port
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the user guide in the application

---

**Built with ❤️ for financial analysts and top management**