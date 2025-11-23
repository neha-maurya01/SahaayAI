from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import init_db
from app.api.routes import messaging, health, voice, webhooks, send
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.utils.logger import logger

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting SahaayAI service...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Create storage directories if they don't exist
    os.makedirs(settings.FILE_STORAGE_PATH, exist_ok=True)
    os.makedirs(os.path.join(settings.FILE_STORAGE_PATH, "audio"), exist_ok=True)
    logger.info("Storage directories created")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SahaayAI service...")

# Create FastAPI app
app = FastAPI(
    title="SahaayAI",
    description="AI-Powered Assistant for Underserved Communities",
    version="1.0.0-POC",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Mount static files for audio/images
if os.path.exists(settings.FILE_STORAGE_PATH):
    app.mount("/audio", StaticFiles(directory=os.path.join(settings.FILE_STORAGE_PATH, "audio")), name="audio")

# Mount frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path, html=True), name="frontend")
    logger.info(f"Frontend mounted at /static from {frontend_path}")

# Include routers
app.include_router(health.router)
app.include_router(messaging.router)
app.include_router(voice.router)
app.include_router(webhooks.router)
app.include_router(send.router)

# Root endpoint - Redirect to frontend
@app.get("/")
async def root():
    """Root endpoint - redirect to frontend"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")

# API info endpoint
@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "service": "SahaayAI",
        "version": "1.0.0-POC",
        "description": "AI-Powered Assistant for Underserved Communities",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "messaging": "/api/v1/message/*",
            "voice": "/api/v1/voice/*"
        },
        "supported_languages": settings.supported_languages_list,
        "supported_domains": [
            "health",
            "agriculture",
            "finance",
            "education",
            "government_schemes",
            "climate"
        ]
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred",
            "detail": str(exc) if settings.DEBUG else "Internal server error"
        }
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
