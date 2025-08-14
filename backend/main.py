#!/usr/bin/env python3
"""
NarrativeForge Backend - Main Application Entry Point
Interactive storytelling with LLM-powered narrative generation
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.routes import story_router
from app.models.story_manager import StoryManager

# Initialize FastAPI app
app = FastAPI(
    title="NarrativeForge API",
    description="Interactive storytelling with AI-powered narrative generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for iOS app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your iOS app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(story_router, prefix="/api/v1", tags=["story"])

# Initialize story manager
story_manager = StoryManager()

# Set global story manager instance
from app.api.routes import story_manager as global_story_manager
global_story_manager = story_manager

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("🚀 Starting NarrativeForge Backend...")
    await story_manager.initialize()
    logger.info("✅ NarrativeForge Backend ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("🛑 Shutting down NarrativeForge Backend...")
    await story_manager.cleanup()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to NarrativeForge! ⚔️",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "narrative-forge"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
