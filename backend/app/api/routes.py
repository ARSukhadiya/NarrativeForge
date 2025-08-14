"""
API Routes - FastAPI endpoints for story management and interaction
Handles story creation, choice making, and state retrieval
"""

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from ..models.story_models import (
    CreateStoryRequest, 
    MakeChoiceRequest, 
    StoryResponse, 
    StorySegmentResponse,
    StoryState
)
from ..models.story_manager import StoryManager

# Create router
story_router = APIRouter()

# Global story manager instance (in production, use dependency injection)
story_manager: StoryManager = None

def get_story_manager() -> StoryManager:
    """Dependency to get story manager instance"""
    if story_manager is None:
        raise HTTPException(status_code=503, detail="Story manager not initialized")
    return story_manager


@story_router.post("/stories", response_model=StoryResponse)
async def create_story(
    request: CreateStoryRequest,
    manager: StoryManager = Depends(get_story_manager)
):
    """Create a new story session"""
    try:
        session_id = manager.create_new_story(
            genre=request.genre,
            difficulty=request.difficulty
        )
        
        logger.info(f"Created new story session: {session_id}")
        
        return StoryResponse(
            success=True,
            message="Story created successfully",
            data={"session_id": session_id}
        )
        
    except Exception as e:
        logger.error(f"Error creating story: {e}")
        raise HTTPException(status_code=500, detail="Failed to create story")


@story_router.get("/stories/{session_id}", response_model=StoryResponse)
async def get_story_state(
    session_id: str,
    manager: StoryManager = Depends(get_story_manager)
):
    """Get the current state of a story session"""
    try:
        story_state = manager.get_story_state(session_id)
        
        if story_state is None:
            raise HTTPException(status_code=404, detail="Story session not found")
        
        return StoryResponse(
            success=True,
            message="Story state retrieved successfully",
            data=story_state.dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving story state: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve story state")


@story_router.post("/stories/{session_id}/choices", response_model=StorySegmentResponse)
async def make_choice(
    session_id: str,
    request: MakeChoiceRequest,
    manager: StoryManager = Depends(get_story_manager)
):
    """Make a choice in the story and generate the next segment"""
    try:
        # Validate session exists
        story_state = manager.get_story_state(session_id)
        if story_state is None:
            raise HTTPException(status_code=404, detail="Story session not found")
        
        # Validate choice index
        if request.choice_index >= len(story_state.current_segment.choices):
            raise HTTPException(status_code=400, detail="Invalid choice index")
        
        # Generate next segment
        next_segment = await manager.generate_next_segment(session_id, request.choice_index)
        
        logger.info(f"Generated next segment for session {session_id}")
        
        return StorySegmentResponse(
            segment=next_segment,
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making choice: {e}")
        raise HTTPException(status_code=500, detail="Failed to process choice")


@story_router.get("/stories/{session_id}/history", response_model=StoryResponse)
async def get_story_history(
    session_id: str,
    manager: StoryManager = Depends(get_story_manager)
):
    """Get the complete story history for a session"""
    try:
        story_state = manager.get_story_state(session_id)
        
        if story_state is None:
            raise HTTPException(status_code=404, detail="Story session not found")
        
        # Convert history to serializable format
        history_data = []
        for segment in story_state.story_history:
            history_data.append(segment.dict())
        
        return StoryResponse(
            success=True,
            message="Story history retrieved successfully",
            data={
                "history": history_data,
                "total_segments": len(history_data)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving story history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve story history")


@story_router.delete("/stories/{session_id}", response_model=StoryResponse)
async def end_story(
    session_id: str,
    manager: StoryManager = Depends(get_story_manager)
):
    """End a story session"""
    try:
        manager.end_story_session(session_id)
        
        logger.info(f"Ended story session: {session_id}")
        
        return StoryResponse(
            success=True,
            message="Story session ended successfully"
        )
        
    except Exception as e:
        logger.error(f"Error ending story session: {e}")
        raise HTTPException(status_code=500, detail="Failed to end story session")


@story_router.get("/stories", response_model=StoryResponse)
async def list_active_stories(
    manager: StoryManager = Depends(get_story_manager)
):
    """List all active story sessions"""
    try:
        active_sessions = manager.get_active_sessions()
        
        return StoryResponse(
            success=True,
            message="Active sessions retrieved successfully",
            data={
                "active_sessions": active_sessions,
                "count": len(active_sessions)
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing active stories: {e}")
        raise HTTPException(status_code=500, detail="Failed to list active stories")


@story_router.get("/genres", response_model=StoryResponse)
async def get_available_genres():
    """Get available story genres"""
    try:
        genres = [
            {
                "id": "fantasy",
                "name": "Fantasy",
                "description": "Epic adventures in magical realms with dragons, wizards, and ancient artifacts"
            },
            {
                "id": "scifi",
                "name": "Science Fiction",
                "description": "Space exploration, advanced technology, and encounters with the unknown"
            },
            {
                "id": "mystery",
                "name": "Mystery",
                "description": "Detective work, solving puzzles, and uncovering hidden secrets"
            }
        ]
        
        return StoryResponse(
            success=True,
            message="Genres retrieved successfully",
            data={"genres": genres}
        )
        
    except Exception as e:
        logger.error(f"Error retrieving genres: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve genres")


@story_router.get("/difficulties", response_model=StoryResponse)
async def get_available_difficulties():
    """Get available difficulty levels"""
    try:
        difficulties = [
            {
                "id": "easy",
                "name": "Easy",
                "description": "Gentle storytelling with straightforward choices"
            },
            {
                "id": "medium",
                "name": "Medium",
                "description": "Balanced challenge with meaningful consequences"
            },
            {
                "id": "hard",
                "name": "Hard",
                "description": "Complex narratives with difficult moral choices"
            }
        ]
        
        return StoryResponse(
            success=True,
            message="Difficulties retrieved successfully",
            data={"difficulties": difficulties}
        )
        
    except Exception as e:
        logger.error(f"Error retrieving difficulties: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve difficulties")
