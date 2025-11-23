from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from datetime import datetime, timedelta
from app.config import settings
from app.utils.logger import logger

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.request_counts = defaultdict(lambda: {"minute": [], "hour": []})
        self.cleanup_interval = timedelta(hours=1)
        self.last_cleanup = datetime.utcnow()
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/ready", "/metrics"]:
            return await call_next(request)
        
        # Get client identifier (IP or user ID from header)
        client_id = request.client.host if request.client else "unknown"
        
        # Check if client is authenticated and use user ID if available
        if "X-User-ID" in request.headers:
            client_id = request.headers["X-User-ID"]
        
        # Clean up old entries periodically
        await self._cleanup_old_entries()
        
        # Check rate limits
        current_time = datetime.utcnow()
        
        # Check per-minute limit
        minute_requests = [
            t for t in self.request_counts[client_id]["minute"]
            if current_time - t < timedelta(minutes=1)
        ]
        
        if len(minute_requests) >= settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(f"Rate limit exceeded for client {client_id} (per minute)")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests. Please try again later.",
                    "retry_after": 60
                }
            )
        
        # Check per-hour limit
        hour_requests = [
            t for t in self.request_counts[client_id]["hour"]
            if current_time - t < timedelta(hours=1)
        ]
        
        if len(hour_requests) >= settings.RATE_LIMIT_PER_HOUR:
            logger.warning(f"Rate limit exceeded for client {client_id} (per hour)")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests. Please try again later.",
                    "retry_after": 3600
                }
            )
        
        # Add current request to counts
        self.request_counts[client_id]["minute"].append(current_time)
        self.request_counts[client_id]["hour"].append(current_time)
        
        # Update counts (keep only recent ones)
        self.request_counts[client_id]["minute"] = minute_requests + [current_time]
        self.request_counts[client_id]["hour"] = hour_requests + [current_time]
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add response headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            settings.RATE_LIMIT_PER_MINUTE - len(self.request_counts[client_id]["minute"])
        )
        
        return response
    
    async def _cleanup_old_entries(self):
        """Remove old entries from request counts"""
        current_time = datetime.utcnow()
        
        if current_time - self.last_cleanup > self.cleanup_interval:
            for client_id in list(self.request_counts.keys()):
                # Remove entries older than 1 hour
                self.request_counts[client_id]["minute"] = [
                    t for t in self.request_counts[client_id]["minute"]
                    if current_time - t < timedelta(minutes=1)
                ]
                self.request_counts[client_id]["hour"] = [
                    t for t in self.request_counts[client_id]["hour"]
                    if current_time - t < timedelta(hours=1)
                ]
                
                # Remove client if no recent requests
                if not self.request_counts[client_id]["hour"]:
                    del self.request_counts[client_id]
            
            self.last_cleanup = current_time
            logger.info("Cleaned up old rate limit entries")
