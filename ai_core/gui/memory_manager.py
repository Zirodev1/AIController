"""
Memory manager for the AI Companion application.
Manages conversation history and memory.
"""
import logging
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import os
import json

from ai_core.memory.conversation_memory import ConversationMemory

class MemoryManager:
    """
    Manage conversation history and memory for the AI companion.
    Provides context for LLM responses.
    """
    
    def __init__(self, main_window):
        """
        Initialize the memory manager.
        
        Args:
            main_window: Reference to the main application window
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # Initialize conversation memory
        self.conversation_memory = ConversationMemory()
        
        # Conversation context settings
        self.context_window_size = 5  # Number of exchanges to include in context
        self.save_directory = "conversation_history"
        
        # Create save directory if it doesn't exist
        os.makedirs(self.save_directory, exist_ok=True)
        
        self.logger.info("Memory manager initialized")
        
    def add_interaction(self, user_input: str, ai_response: str, 
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an interaction to memory.
        
        Args:
            user_input: The user's input text
            ai_response: The AI's response text
            metadata: Optional additional data about the exchange
        """
        try:
            # Add metadata about the current state if not provided
            if metadata is None:
                metadata = {}
                
            # Add emotional state if available
            if hasattr(self.main_window, 'emotion_engine'):
                emotion_state = self.main_window.emotion_engine.get_emotional_state()
                metadata['emotional_state'] = emotion_state
                
            # Add to conversation memory
            self.conversation_memory.add_exchange(user_input, ai_response, metadata)
            self.logger.debug(f"Added interaction to memory: User: '{user_input[:30]}...', AI: '{ai_response[:30]}...'")
            
        except Exception as e:
            self.logger.error(f"Error adding interaction to memory: {e}")
            
    def get_recent_context(self, max_exchanges: int = None) -> List[Tuple[str, str]]:
        """
        Get recent conversation context for LLM.
        
        Args:
            max_exchanges: Maximum number of exchanges to include (defaults to context_window_size)
            
        Returns:
            List of (user_input, ai_response) tuples
        """
        if max_exchanges is None:
            max_exchanges = self.context_window_size
            
        try:
            return self.conversation_memory.get_recent_exchanges(max_exchanges)
        except Exception as e:
            self.logger.error(f"Error getting recent context: {e}")
            return []
            
    def get_formatted_context(self, max_exchanges: int = None) -> str:
        """
        Get formatted conversation history for LLM prompts.
        
        Args:
            max_exchanges: Maximum number of exchanges to include
            
        Returns:
            Formatted conversation history string
        """
        if max_exchanges is None:
            max_exchanges = self.context_window_size
            
        try:
            return self.conversation_memory.get_formatted_history(max_exchanges)
        except Exception as e:
            self.logger.error(f"Error getting formatted context: {e}")
            return ""
            
    def clear_memory(self) -> None:
        """Clear all conversation memory."""
        try:
            self.conversation_memory.clear()
            self.logger.info("Conversation memory cleared")
            self.main_window.add_message("System", "Conversation memory cleared", animate=False)
        except Exception as e:
            self.logger.error(f"Error clearing memory: {e}")
            
    def save_conversation(self, filename: Optional[str] = None) -> bool:
        """
        Save the current conversation to a file.
        
        Args:
            filename: Optional filename (defaults to timestamp-based name)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"conversation_{timestamp}.json"
                
            filepath = os.path.join(self.save_directory, filename)
            self.conversation_memory.save_to_file(filepath)
            
            self.logger.info(f"Conversation saved to {filepath}")
            self.main_window.add_message("System", f"Conversation saved to {filename}", animate=False)
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving conversation: {e}")
            self.main_window.add_message("System", f"Error saving conversation: {str(e)}", animate=False)
            return False
            
    def load_conversation(self, filename: str) -> bool:
        """
        Load a conversation from a file.
        
        Args:
            filename: Filename to load from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = os.path.join(self.save_directory, filename)
            if not os.path.exists(filepath):
                self.logger.error(f"Conversation file not found: {filepath}")
                self.main_window.add_message("System", f"Conversation file not found: {filename}", animate=False)
                return False
                
            success = self.conversation_memory.load_from_file(filepath)
            
            if success:
                self.logger.info(f"Conversation loaded from {filepath}")
                self.main_window.add_message("System", f"Conversation loaded from {filename}", animate=False)
                return True
            else:
                self.logger.error(f"Failed to load conversation from {filepath}")
                self.main_window.add_message("System", f"Failed to load conversation from {filename}", animate=False)
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading conversation: {e}")
            self.main_window.add_message("System", f"Error loading conversation: {str(e)}", animate=False)
            return False
            
    def list_saved_conversations(self) -> List[str]:
        """
        List all saved conversations.
        
        Returns:
            List of filenames
        """
        try:
            files = os.listdir(self.save_directory)
            return [f for f in files if f.endswith('.json')]
        except Exception as e:
            self.logger.error(f"Error listing saved conversations: {e}")
            return [] 