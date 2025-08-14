"""
LLM Engine - Handles AI model integration for story generation
Manages prompt engineering and context management for narrative creation
"""

import asyncio
import json
import uuid
from typing import List, Dict, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from loguru import logger

from .story_models import StoryState, StoryChoice, StorySegment


class LLMEngine:
    """Handles LLM integration for story generation"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_length = 512
        self.temperature = 0.8
        self.top_p = 0.9
        
        # Prompt templates for different story elements
        self.prompt_templates = self._load_prompt_templates()
    
    async def initialize(self):
        """Initialize the LLM model"""
        logger.info(f"Initializing LLM Engine on device: {self.device}")
        
        try:
            # Use a smaller, efficient model for faster generation
            model_name = "microsoft/DialoGPT-medium"  # Alternative: "gpt2-medium"
            
            logger.info(f"Loading model: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("LLM Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM Engine: {e}")
            # Fallback to mock generation for development
            self.model = None
            logger.warning("Using mock generation mode")
    
    async def cleanup(self):
        """Cleanup LLM resources"""
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        logger.info("LLM Engine cleanup completed")
    
    async def generate_story_continuation(
        self, 
        story_state: StoryState, 
        chosen_choice: StoryChoice
    ) -> StorySegment:
        """Generate the next story segment based on the chosen choice"""
        
        if self.model is None:
            # Mock generation for development/testing
            return await self._mock_generate_segment(story_state, chosen_choice)
        
        try:
            # Build context from story history
            context = self._build_story_context(story_state)
            
            # Create prompt for story continuation
            prompt = self._create_continuation_prompt(context, chosen_choice)
            
            # Generate response
            response = await self._generate_text(prompt)
            
            # Parse the response into a story segment
            segment = self._parse_story_response(response, story_state)
            
            return segment
            
        except Exception as e:
            logger.error(f"Error generating story continuation: {e}")
            # Fallback to mock generation
            return await self._mock_generate_segment(story_state, chosen_choice)
    
    def _build_story_context(self, story_state: StoryState) -> str:
        """Build context string from story history"""
        context_parts = []
        
        # Add world and character info
        if story_state.world_info:
            context_parts.append(f"World: {json.dumps(story_state.world_info)}")
        
        if story_state.character_info:
            context_parts.append(f"Characters: {json.dumps(story_state.character_info)}")
        
        # Add story history
        for i, segment in enumerate(story_state.story_history[-3:]):  # Last 3 segments
            context_parts.append(f"Scene {i+1}: {segment.text}")
            if segment.choices:
                chosen = segment.choices[0]  # Assume first choice was taken
                context_parts.append(f"Action: {chosen.text}")
        
        # Add current segment
        context_parts.append(f"Current Scene: {story_state.current_segment.text}")
        
        return "\n".join(context_parts)
    
    def _create_continuation_prompt(self, context: str, chosen_choice: StoryChoice) -> str:
        """Create prompt for story continuation"""
        template = self.prompt_templates["continuation"]
        
        prompt = template.format(
            context=context,
            choice=chosen_choice.text,
            action=chosen_choice.action
        )
        
        return prompt
    
    async def _generate_text(self, prompt: str) -> str:
        """Generate text using the LLM"""
        try:
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=self.max_length)
            inputs = inputs.to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 200,  # Generate up to 200 more tokens
                    temperature=self.temperature,
                    top_p=self.top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated part
            generated_text = response[len(prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error in text generation: {e}")
            return "The story continues..."
    
    def _parse_story_response(self, response: str, story_state: StoryState) -> StorySegment:
        """Parse LLM response into a story segment"""
        # Simple parsing - in a real implementation, you'd want more sophisticated parsing
        lines = response.split('\n')
        
        # Extract story text (first paragraph)
        story_text = lines[0] if lines else "The story continues..."
        
        # Generate choices based on the story context
        choices = self._generate_choices_for_segment(story_text, story_state)
        
        # Create segment
        segment = StorySegment(
            id=str(uuid.uuid4())[:8],
            text=story_text,
            choices=choices,
            mood=self._detect_mood(story_text),
            location=self._extract_location(story_text)
        )
        
        return segment
    
    def _generate_choices_for_segment(self, story_text: str, story_state: StoryState) -> List[StoryChoice]:
        """Generate choices for a story segment"""
        # This is a simplified choice generation
        # In a real implementation, you'd use the LLM to generate choices
        
        choice_templates = {
            "fantasy": [
                ("Continue forward", "continue"),
                ("Investigate the area", "investigate"),
                ("Use magic", "use_magic"),
                ("Fight", "fight"),
                ("Run away", "flee")
            ],
            "scifi": [
                ("Scan the area", "scan"),
                ("Contact the crew", "contact_crew"),
                ("Use technology", "use_tech"),
                ("Proceed carefully", "proceed_carefully"),
                ("Return to ship", "return_ship")
            ],
            "mystery": [
                ("Search for clues", "search"),
                ("Question someone", "question"),
                ("Examine evidence", "examine"),
                ("Follow a lead", "follow_lead"),
                ("Call for backup", "call_backup")
            ]
        }
        
        templates = choice_templates.get(story_state.genre, choice_templates["fantasy"])
        
        # Select 3-4 choices based on context
        import random
        selected_templates = random.sample(templates, min(3, len(templates)))
        
        choices = []
        for text, action in selected_templates:
            choices.append(StoryChoice(text=text, action=action))
        
        return choices
    
    def _detect_mood(self, text: str) -> str:
        """Detect the mood of a story segment"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["scary", "fear", "terrifying", "dark"]):
            return "tense"
        elif any(word in text_lower for word in ["happy", "joy", "bright", "warm"]):
            return "cheerful"
        elif any(word in text_lower for word in ["mysterious", "strange", "unknown"]):
            return "mysterious"
        else:
            return "neutral"
    
    def _extract_location(self, text: str) -> str:
        """Extract location from story text"""
        # Simple location extraction - in reality, you'd use NER or LLM
        locations = ["cavern", "ship", "mansion", "forest", "city", "castle"]
        
        for location in locations:
            if location in text.lower():
                return location.title()
        
        return "Unknown Location"
    
    async def _mock_generate_segment(self, story_state: StoryState, chosen_choice: StoryChoice) -> StorySegment:
        """Generate a mock story segment for development/testing"""
        
        mock_responses = {
            "bold_entrance": "You stride confidently into the Crystal Caverns. The air is thick with ancient magic, and your footsteps echo through the crystalline passages. Suddenly, you hear a low rumble from deep within the mountain...",
            "cautious_approach": "You carefully examine the entrance, noting the intricate runes carved into the stone. Your careful observation reveals a hidden mechanism that could be either a trap or a blessing...",
            "prepare_equipment": "You take a moment to check your gear. Your sword gleams in the dim light, and you feel the weight of your magical items. You're as ready as you'll ever be for what lies ahead...",
            "investigate": "You decide to investigate the distress signal. As you approach the planet's surface, your sensors detect unusual energy readings that don't match any known technology...",
            "scan_planet": "Your ship's scanners sweep across the planet's surface, revealing structures that defy conventional physics. The readings suggest technology far beyond human capabilities...",
            "enter_mansion": "You step into the mansion, the floorboards creaking beneath your feet. The air is thick with dust and something else - the lingering presence of secrets waiting to be uncovered...",
            "interview_neighbors": "You approach the neighboring houses, hoping to gather information. The locals seem nervous, their eyes darting around as they speak in hushed tones about the mansion's dark history..."
        }
        
        # Get mock response or generate a generic one
        story_text = mock_responses.get(
            chosen_choice.action, 
            f"You choose to {chosen_choice.text.lower()}. The story continues with new challenges and discoveries ahead..."
        )
        
        # Generate choices
        choices = self._generate_choices_for_segment(story_text, story_state)
        
        return StorySegment(
            id=str(uuid.uuid4())[:8],
            text=story_text,
            choices=choices,
            mood=self._detect_mood(story_text),
            location=self._extract_location(story_text)
        )
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates for different story elements"""
        return {
            "continuation": """You are a master storyteller creating an interactive adventure. Based on the following context and the player's choice, continue the story in an engaging way.

Context:
{context}

Player's Choice: {choice} (Action: {action})

Continue the story naturally, maintaining consistency with the established world and characters. End with a compelling situation that presents the player with new choices. Keep the response under 150 words.

Story continuation:""",
            
            "choice_generation": """Based on the following story segment, generate 3-4 compelling choices for the player. Each choice should lead to different interesting outcomes.

Story: {story_text}

Generate choices that are:
1. Clear and actionable
2. Diverse in their potential outcomes
3. Appropriate for the story's genre and tone

Choices:""",
            
            "character_development": """Develop a character based on the following context and story progression.

Context: {context}

Character: {character_name}

Develop this character's personality, motivations, and role in the story. Consider their background and how they've evolved through the narrative.

Character development:"""
        }
