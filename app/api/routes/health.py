from fastapi import APIRouter
from datetime import datetime
import psutil
import os

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns service status and basic metrics
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "SahaayAI",
        "version": "1.0.0-POC"
    }

@router.get("/metrics")
async def get_metrics():
    """
    Get system metrics
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_usage_percent": cpu_percent,
            "memory": {
                "total_mb": memory.total / (1024 * 1024),
                "available_mb": memory.available / (1024 * 1024),
                "percent_used": memory.percent
            },
            "disk": {
                "total_gb": disk.total / (1024 * 1024 * 1024),
                "used_gb": disk.used / (1024 * 1024 * 1024),
                "free_gb": disk.free / (1024 * 1024 * 1024),
                "percent_used": disk.percent
            }
        }
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/ready")
async def readiness_check():
    """
    Readiness check for load balancer
    """
    # Check if essential services are available
    checks = {
        "database": True,  # Add actual database check
        "ai_service": True,  # Add actual AI service check
        "storage": os.path.exists("./storage")
    }
    
    all_ready = all(checks.values())
    
    return {
        "ready": all_ready,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
