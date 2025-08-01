#!/usr/bin/env python3
"""
Simple FastAPI application for DigitalOcean deployment
Universal Consultant Intelligence Platform - Minimal Demo
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
import os

# Create FastAPI app
app = FastAPI(
    title="Universal Consultant Intelligence Platform",
    version="1.0.0",
    description="AI-powered consultant intelligence and research platform"
)

@app.get("/")
async def root():
    """Root endpoint returning platform information"""
    return {
        "name": "Universal Consultant Intelligence Platform",
        "version": "1.0.0",
        "status": "operational",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "version": "1.0.0"
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_status": "running",
        "platform": "Universal Consultant Intelligence Platform",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "endpoints": {
            "health": "/health",
            "status": "/api/v1/status",
            "root": "/"
        }
    }

@app.get("/api/v1/consultants")
async def list_consultants():
    """Mock consultants endpoint for demo"""
    return {
        "consultants": [
            {
                "id": 1,
                "name": "Demo Consultant",
                "expertise": ["Technology", "Business Strategy", "Digital Transformation"],
                "status": "active"
            }
        ],
        "total": 1,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )