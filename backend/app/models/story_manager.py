"""
Story Manager - Core component for LLM-powered narrative generation
Handles story state, context management, and AI interactions
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from loguru import logger

from .llm_engine import LLMEngine
from .story_models import StoryState, StoryChoice, StorySegment


@dataclass
class StorySession:
    """Represents an active story session"""
    session_id: str
    story_state: StoryState
    created_at: datetime
    last_updated: datetime
    is_active: bool = True


class StoryManager:
    """Manages story sessions and coordinates with LLM for narrative generation"""
    
    def __init__(self):
        self.llm_engine: Optional[LLMEngine] = None
        self.active_sessions: Dict[str, StorySession] = {}
        self.story_templates = self._load_story_templates()
    
    async def initialize(self):
        """Initialize the story manager and LLM engine"""
        logger.info("Initializing Story Manager...")
        self.llm_engine = LLMEngine()
        await self.llm_engine.initialize()
        logger.info("Story Manager initialized successfully")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.llm_engine:
            await self.llm_engine.cleanup()
        logger.info("Story Manager cleanup completed")
    
    def create_new_story(self, genre: str = "fantasy", difficulty: str = "medium") -> str:
        """Create a new story session"""
        session_id = str(uuid.uuid4())
        
        # Get story template
        template = self.story_templates.get(genre, self.story_templates["fantasy"])
        
        # Create initial story state
        initial_state = StoryState(
            story_id=session_id,
            current_segment=StorySegment(
                id="start",
                text=template["opening"],
                choices=template["initial_choices"],
                background_context=template["background"]
            ),
            story_history=[],
            character_info=template.get("characters", {}),
            world_info=template.get("world", {}),
            genre=genre,
            difficulty=difficulty,
            created_at=datetime.now()
        )
        
        # Create session
        session = StorySession(
            session_id=session_id,
            story_state=initial_state,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        logger.info(f"Created new story session: {session_id}")
        
        return session_id
    
    async def generate_next_segment(self, session_id: str, choice_index: int) -> StorySegment:
        """Generate the next story segment based on user choice"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        current_state = session.story_state
        
        # Get the chosen option
        if choice_index >= len(current_state.current_segment.choices):
            raise ValueError(f"Invalid choice index: {choice_index}")
        
        chosen_choice = current_state.current_segment.choices[choice_index]
        
        # Add current segment to history
        current_state.story_history.append(current_state.current_segment)
        
        # Generate next segment using LLM
        next_segment = await self.llm_engine.generate_story_continuation(
            story_state=current_state,
            chosen_choice=chosen_choice
        )
        
        # Update story state
        current_state.current_segment = next_segment
        current_state.last_updated = datetime.now()
        
        # Update session
        session.last_updated = datetime.now()
        
        logger.info(f"Generated next segment for session {session_id}")
        return next_segment
    
    def get_story_state(self, session_id: str) -> Optional[StoryState]:
        """Get the current state of a story session"""
        if session_id not in self.active_sessions:
            return None
        
        return self.active_sessions[session_id].story_state
    
    def end_story_session(self, session_id: str):
        """End a story session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].is_active = False
            logger.info(f"Ended story session: {session_id}")
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return [sid for sid, session in self.active_sessions.items() if session.is_active]
    
    def _load_story_templates(self) -> Dict:
        """Load story templates for different genres"""
        return {
            "fantasy": {
                "opening": "You stand at the entrance of the ancient Crystal Caverns, a legendary place where adventurers seek the fabled Heart of the Mountain. The air is thick with magic, and you can feel the weight of destiny upon your shoulders. Your quest begins now...",
                "initial_choices": [
                    StoryChoice(text="Enter the caverns boldly", action="bold_entrance"),
                    StoryChoice(text="Study the entrance first", action="cautious_approach"),
                    StoryChoice(text="Check your equipment", action="prepare_equipment")
                ],
                "background": "The Crystal Caverns are said to hold ancient treasures and powerful artifacts. Many have entered, but few have returned. The Heart of the Mountain is a legendary gem that grants its wielder immense power.",
                "characters": {
                    "protagonist": "A brave adventurer seeking glory and treasure",
                    "mentor": "The wise old sage who sent you on this quest"
                },
                "world": {
                    "setting": "Fantasy realm with magic and mythical creatures",
                    "time_period": "Medieval fantasy era"
                }
            },
            "scifi": {
                "opening": "The starship Horizon drifts through the vast emptiness of space. You're the captain of this vessel, and you've just received a mysterious distress signal from a nearby planet. The fate of your crew and potentially the galaxy rests in your hands...",
                "initial_choices": [
                    StoryChoice(text="Investigate the distress signal", action="investigate"),
                    StoryChoice(text="Scan the planet first", action="scan_planet"),
                    StoryChoice(text="Consult with your crew", action="crew_meeting")
                ],
                "background": "You're on a deep space exploration mission when you encounter an unknown signal. The planet below shows signs of advanced civilization, but something seems wrong.",
                "characters": {
                    "protagonist": "Captain of the starship Horizon",
                    "crew": "Diverse team of specialists and explorers"
                },
                "world": {
                    "setting": "Deep space exploration",
                    "time_period": "Far future, interstellar era"
                }
            },
            "mystery": {
                "opening": "The old mansion looms before you, its windows dark and foreboding. You're a detective called to investigate the disappearance of the mansion's owner. The local police are stumped, and the family is desperate for answers...",
                "initial_choices": [
                    StoryChoice(text="Enter the mansion", action="enter_mansion"),
                    StoryChoice(text="Interview the neighbors", action="interview_neighbors"),
                    StoryChoice(text="Examine the exterior", action="examine_exterior")
                ],
                "background": "A wealthy businessman has vanished from his mansion without a trace. No signs of forced entry, no ransom note, just an empty house and unanswered questions.",
                "characters": {
                    "protagonist": "Experienced detective with a sharp mind",
                    "victim": "The missing mansion owner",
                    "suspects": "Various family members and staff"
                },
                "world": {
                    "setting": "Modern-day detective work",
                    "time_period": "Present day"
                }
            }
        }
