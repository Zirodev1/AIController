"""
Conversation memory system for maintaining context in conversations.
"""
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import json
import os

class ConversationExchange:
    """Represents a single exchange in a conversation (user input and AI response)."""
    
    def __init__(self, user_input: str, ai_response: str, 
                timestamp: Optional[datetime] = None, 
                metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a conversation exchange.
        
        Args:
            user_input: The user's input text
            ai_response: The AI's response text
            timestamp: When the exchange occurred (defaults to now)
            metadata: Optional additional data about the exchange
        """
        self.user_input = user_input
        self.ai_response = ai_response
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'user_input': self.user_input,
            'ai_response': self.ai_response,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationExchange':
        """Create from dictionary."""
        return cls(
            user_input=data['user_input'],
            ai_response=data['ai_response'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data['metadata']
        )
        
class ConversationMemory:
    """Manages conversation history and provides context for AI responses."""
    
    def __init__(self, max_exchanges: int = 100):
        """
        Initialize the conversation memory.
        
        Args:
            max_exchanges: Maximum number of exchanges to store in memory
        """
        self.exchanges: List[ConversationExchange] = []
        self.max_exchanges = max_exchanges
        self.session_start = datetime.now()
        self.session_metadata: Dict[str, Any] = {}
        
    def add_exchange(self, user_input: str, ai_response: str, 
                    metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a new conversation exchange to memory.
        
        Args:
            user_input: The user's input text
            ai_response: The AI's response text
            metadata: Optional additional data about the exchange
        """
        exchange = ConversationExchange(user_input, ai_response, metadata=metadata)
        self.exchanges.append(exchange)
        
        # Maintain the maximum size
        if len(self.exchanges) > self.max_exchanges:
            self.exchanges.pop(0)
            
    def get_recent_exchanges(self, count: int = 5) -> List[Tuple[str, str]]:
        """
        Get the most recent conversation exchanges.
        
        Args:
            count: Number of recent exchanges to retrieve
            
        Returns:
            List of (user_input, ai_response) tuples
        """
        recent = self.exchanges[-count:] if count < len(self.exchanges) else self.exchanges
        return [(exchange.user_input, exchange.ai_response) for exchange in recent]
    
    def get_formatted_history(self, count: int = 5) -> str:
        """
        Get formatted conversation history for LLM context.
        
        Args:
            count: Number of recent exchanges to include
            
        Returns:
            Formatted conversation history string
        """
        recent = self.exchanges[-count:] if count < len(self.exchanges) else self.exchanges
        
        history = []
        for exchange in recent:
            history.append(f"User: {exchange.user_input}")
            history.append(f"Assistant: {exchange.ai_response}")
            
        return "\n".join(history)
    
    def search_history(self, query: str) -> List[ConversationExchange]:
        """
        Search for exchanges containing the query string.
        
        Args:
            query: Search string
            
        Returns:
            List of matching conversation exchanges
        """
        query = query.lower()
        return [
            exchange for exchange in self.exchanges
            if query in exchange.user_input.lower() or query in exchange.ai_response.lower()
        ]
        
    def clear(self) -> None:
        """Clear all conversation exchanges."""
        self.exchanges = []
        self.session_start = datetime.now()
        
    def save_to_file(self, filepath: str) -> None:
        """
        Save conversation history to a file.
        
        Args:
            filepath: Path to save file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {
            'exchanges': [exchange.to_dict() for exchange in self.exchanges],
            'session_start': self.session_start.isoformat(),
            'session_metadata': self.session_metadata
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def load_from_file(self, filepath: str) -> bool:
        """
        Load conversation history from a file.
        
        Args:
            filepath: Path to load file from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.exchanges = [
                ConversationExchange.from_dict(exchange_data)
                for exchange_data in data['exchanges']
            ]
            self.session_start = datetime.fromisoformat(data['session_start'])
            self.session_metadata = data['session_metadata']
            return True
            
        except Exception as e:
            print(f"Error loading conversation memory: {e}")
            return False 