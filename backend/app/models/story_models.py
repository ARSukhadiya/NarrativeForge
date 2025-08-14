"""
Story Data Models - Pydantic models for story state and components
Defines the structure for story segments, choices, and overall state
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, Field


class StoryChoice(BaseModel):
    """Represents a choice option in the story"""
    text: str = Field(..., description="The choice text displayed to the user")
    action: str = Field(..., description="The action identifier for this choice")
    description: Optional[str] = Field(None, description="Additional description of the choice")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Enter the caverns boldly",
                "action": "bold_entrance",
                "description": "Charge forward with confidence"
            }
        }


class StorySegment(BaseModel):
    """Represents a segment of the story"""
    id: str = Field(..., description="Unique identifier for this segment")
    text: str = Field(..., description="The story text for this segment")
    choices: List[StoryChoice] = Field(..., description="Available choices for the user")
    background_context: Optional[str] = Field(None, description="Background context for this segment")
    mood: Optional[str] = Field(None, description="The mood/atmosphere of this segment")
    location: Optional[str] = Field(None, description="The location where this segment takes place")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "crystal_caverns_entrance",
                "text": "You stand at the entrance of the ancient Crystal Caverns...",
                "choices": [
                    {"text": "Enter boldly", "action": "bold_entrance"},
                    {"text": "Study first", "action": "cautious_approach"}
                ],
                "background_context": "The Crystal Caverns are legendary...",
                "mood": "mysterious",
                "location": "Crystal Caverns Entrance"
            }
        }


class StoryState(BaseModel):
    """Represents the complete state of a story session"""
    story_id: str = Field(..., description="Unique identifier for the story session")
    current_segment: StorySegment = Field(..., description="The current story segment")
    story_history: List[StorySegment] = Field(default_factory=list, description="Previous story segments")
    character_info: Dict[str, str] = Field(default_factory=dict, description="Information about characters")
    world_info: Dict[str, str] = Field(default_factory=dict, description="Information about the world")
    genre: str = Field(..., description="The genre of the story")
    difficulty: str = Field(..., description="The difficulty level")
    created_at: datetime = Field(..., description="When the story was created")
    last_updated: Optional[datetime] = Field(None, description="When the story was last updated")
    
    class Config:
        schema_extra = {
            "example": {
                "story_id": "uuid-12345",
                "current_segment": {
                    "id": "start",
                    "text": "You begin your adventure...",
                    "choices": []
                },
                "story_history": [],
                "character_info": {"protagonist": "Brave adventurer"},
                "world_info": {"setting": "Fantasy realm"},
                "genre": "fantasy",
                "difficulty": "medium",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class CreateStoryRequest(BaseModel):
    """Request model for creating a new story"""
    genre: str = Field(default="fantasy", description="The genre of the story")
    difficulty: str = Field(default="medium", description="The difficulty level")
    
    class Config:
        schema_extra = {
            "example": {
                "genre": "fantasy",
                "difficulty": "medium"
            }
        }


class MakeChoiceRequest(BaseModel):
    """Request model for making a story choice"""
    choice_index: int = Field(..., ge=0, description="Index of the chosen option")
    
    class Config:
        schema_extra = {
            "example": {
                "choice_index": 0
            }
        }


class StoryResponse(BaseModel):
    """Response model for story operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict] = Field(None, description="Response data")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Story created successfully",
                "data": {"session_id": "uuid-12345"}
            }
        }


class StorySegmentResponse(BaseModel):
    """Response model for story segment generation"""
    segment: StorySegment = Field(..., description="The generated story segment")
    session_id: str = Field(..., description="The story session ID")
    
    class Config:
        schema_extra = {
            "example": {
                "segment": {
                    "id": "next_segment",
                    "text": "You continue your journey...",
                    "choices": []
                },
                "session_id": "uuid-12345"
            }
        }
