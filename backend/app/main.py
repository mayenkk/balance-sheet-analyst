from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import time
import logging
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, chat, companies, pdf_processing, activities
from app.services.audit import AuditService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Balance Sheet Analyst API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Balance Sheet Analyst API...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered balance sheet analysis platform with RAG pipeline",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(companies.router, prefix="/api/v1")
app.include_router(pdf_processing.router, prefix="/api/v1")
app.include_router(activities.router, prefix="/api/v1")

# Mount static files for React app
static_dir = os.path.join(os.getcwd(), "static")
if os.path.exists(static_dir):
    app.mount("/app", StaticFiles(directory=static_dir, html=True), name="static")
    logger.info(f"Static files mounted from: {static_dir}")
else:
    logger.warning(f"Static directory not found: {static_dir}")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return HTTPException(
        status_code=500,
        detail="Internal server error"
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION
    }

# Root endpoint - redirect to React app
@app.get("/")
async def root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.VERSION,
            "docs": "/docs",
            "health": "/health"
        }

# API info endpoint
@app.get("/api/info")
async def api_info():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "description": "AI-Powered Balance Sheet Analysis Platform",
        "features": [
            "Multi-user authentication with role-based access",
            "AI-powered financial analysis",
            "Interactive chat interface",
            "Comprehensive audit logging",
            "Real-time data visualization",
            "Company hierarchy management"
        ]
    } 