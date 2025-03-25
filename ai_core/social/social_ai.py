"""
Social AI system that combines platform management, personality management, and memory system.
"""
import uuid
import json
import os
import sqlite3
from typing import Optional, Dict, List
from datetime import datetime
import logging
from ..platforms.platform_manager import PlatformManager, Platform
from ..personality.personality_manager import PersonalityManager, PersonaType
from ..memory.memory_system import MemorySystem

class SocialAI:
    def __init__(self, api_key: str):
        self.platform_manager = PlatformManager()
        self.personality_manager = PersonalityManager()
        self.memory_system = MemorySystem(api_key=api_key)
        self.logger = logging.getLogger(__name__)
        
    def initialize_platform(self, platform: Platform, credentials: dict, user_id: Optional[str] = None):
        """Initialize a platform with credentials and user ID."""
        if user_id is None:
            user_id = self._generate_user_id(platform)
            
        self.platform_manager.initialize_platform(platform, credentials)
        self.platform_manager.manage_user_identity(platform, user_id)
        self.memory_system.add_user(user_id, platform.value)
        
        # Load appropriate persona
        persona_type = PersonaType.TWITTER if platform == Platform.TWITTER else PersonaType.ONLYFANS
        persona_path = f"personas/{platform.value}_persona.json"
        self.personality_manager.load_persona(persona_type, persona_path)
        
        return user_id
        
    def _generate_user_id(self, platform: Platform) -> str:
        """Generate or load user ID for a platform."""
        config_file = f"{platform.value}_config.json"
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                if 'user_id' in config:
                    return config['user_id']
        
        new_user_id = str(uuid.uuid4())
        with open(config_file, 'w') as f:
            json.dump({'user_id': new_user_id}, f, indent=4)
            
        return new_user_id
        
    def get_context(self, platform: Platform, user_id: str) -> str:
        """Get context for the current interaction."""
        recent_conversations = self.memory_system.get_recent_conversations(user_id)
        important_memories = self.memory_system.get_important_memories(user_id)
        personality_adaptations = self.memory_system.get_personality_adaptations(user_id)
        
        # Get user preferences
        with sqlite3.connect(self.memory_system.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT preferences FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            user_preferences = json.loads(result[0]) if result and result[0] else {}
        
        # Format context
        context = self._format_context(
            recent_conversations, 
            important_memories, 
            user_preferences
        )
        
        return context
        
    def _format_context(self, conversations: List[dict], memories: List[dict], 
                       preferences: Dict) -> str:
        """Format context from conversations, memories, and preferences."""
        context = ""
        
        # Add personal information
        personal_info = [m for m in memories if m['memory_type'] == 'personal_info']
        if personal_info:
            context += "Personal Information:\n"
            for info in personal_info:
                context += f"- {info['content']}\n"
            context += "\n"
        
        # Add recent conversations
        context += "Recent conversations:\n"
        for conv in conversations:
            context += f"User: {conv['user_message']}\n"
            context += f"Assistant: {conv['assistant_response']}\n"
        
        # Add other memories
        other_memories = [m for m in memories if m['memory_type'] != 'personal_info']
        if other_memories:
            context += "\nOther important memories:\n"
            for memory in other_memories:
                context += f"- {memory['content']} (importance: {memory['importance_score']})\n"
        
        # Add preferences
        if preferences:
            context += "\nUser preferences:\n"
            for pref_type, value in preferences.items():
                context += f"- {pref_type}: {value}\n"
        
        return context
        
    def generate_response(self, platform: Platform, user_id: str, user_input: str) -> str:
        """Generate a response based on platform, context, and personality."""
        # Set active platform and persona
        self.platform_manager.set_active_platform(platform)
        persona_type = PersonaType.TWITTER if platform == Platform.TWITTER else PersonaType.ONLYFANS
        self.personality_manager.set_active_persona(persona_type)
        
        # Get context and personality
        context = self.get_context(platform, user_id)
        personality_config = self.personality_manager.get_persona_config()
        
        # Construct prompt
        prompt = self._construct_prompt(personality_config, context, user_input)
        
        # Generate response
        response = self._generate_ai_response(prompt)
        
        # Store conversation
        self.memory_system.store_conversation(user_id, user_input, response)
        
        return response
        
    def _construct_prompt(self, personality: dict, context: str, user_input: str) -> str:
        """Construct the prompt for the AI model."""
        return (
            f"Personality:\n{json.dumps(personality, indent=2)}\n\n"
            f"Context:\n{context}\n\n"
            f"User: {user_input}\n"
            "Response: Generate a response following the personality rules and "
            "considering the provided context."
        )
        
    def _generate_ai_response(self, prompt: str) -> str:
        """Generate response using the AI model."""
        # TODO: Implement AI model integration
        # This will use the appropriate AI model based on the platform
        pass
        
    def post_content(self, platform: Platform, content: str, media_urls: List[str] = None):
        """Post content to the specified platform."""
        # Validate content against platform rules
        if not self.personality_manager.validate_content(content):
            self.logger.error("Content validation failed")
            return False
            
        # Format content according to platform rules
        formatted_content = self.personality_manager.format_response(content)
        
        # Post to platform
        return self.platform_manager.post_content(formatted_content, media_urls) 