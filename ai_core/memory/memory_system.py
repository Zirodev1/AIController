"""
Memory system for storing and retrieving experiences, with support for both short-term and long-term memory.
"""
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime
import json

class Memory:
    def __init__(self, content: Dict[str, Any], importance: float = 0.5):
        """
        Initialize a memory with content and importance.
        
        Args:
            content: Dictionary containing memory data
            importance: Importance value (0.0 to 1.0)
        """
        self.content = content
        self.importance = max(0.0, min(1.0, importance))
        self.timestamp = datetime.now()
        self.connections: List[str] = []  # IDs of connected memories
        self.emotional_valence = 0.0  # -1.0 (negative) to 1.0 (positive)
        self.access_count = 0
        self.last_accessed = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary format."""
        return {
            'content': self.content,
            'importance': self.importance,
            'timestamp': self.timestamp.isoformat(),
            'connections': self.connections,
            'emotional_valence': self.emotional_valence,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """Create memory from dictionary format."""
        memory = cls(data['content'], data['importance'])
        memory.timestamp = datetime.fromisoformat(data['timestamp'])
        memory.connections = data['connections']
        memory.emotional_valence = data['emotional_valence']
        memory.access_count = data['access_count']
        if data['last_accessed']:
            memory.last_accessed = datetime.fromisoformat(data['last_accessed'])
        return memory

class MemorySystem:
    def __init__(self):
        """Initialize the memory system with short-term and long-term storage."""
        # Short-term memory (recent experiences)
        self.short_term_memories: List[Memory] = []
        self.short_term_capacity = 10
        
        # Long-term memory (significant experiences)
        self.long_term_memories: Dict[str, Memory] = {}
        
        # Memory consolidation parameters
        self.consolidation_threshold = 0.7
        self.forgetting_rate = 0.1
        
        # Emotional memory parameters
        self.emotional_boost = 1.5  # Emotional memories are more likely to be retained
        
    def store_interaction(self, interaction_data: Dict[str, Any]) -> None:
        """
        Store a new interaction in memory.
        
        Args:
            interaction_data: Dictionary containing interaction details
        """
        # Create new memory
        memory = Memory(
            content=interaction_data,
            importance=self._calculate_importance(interaction_data)
        )
        
        # Add to short-term memory
        self.short_term_memories.append(memory)
        
        # Maintain short-term memory capacity
        if len(self.short_term_memories) > self.short_term_capacity:
            self._consolidate_oldest_memory()
            
    def retrieve_relevant_memories(self, context: Dict[str, Any], limit: int = 5) -> List[Memory]:
        """
        Retrieve memories relevant to the current context.
        
        Args:
            context: Current context to match against
            limit: Maximum number of memories to return
            
        Returns:
            List of relevant memories
        """
        # Combine short-term and long-term memories
        all_memories = self.short_term_memories + list(self.long_term_memories.values())
        
        # Calculate relevance scores
        relevance_scores = [
            self._calculate_relevance(memory, context)
            for memory in all_memories
        ]
        
        # Sort by relevance and return top memories
        sorted_memories = [
            memory for _, memory in sorted(
                zip(relevance_scores, all_memories),
                reverse=True
            )
        ]
        
        # Update access counts
        for memory in sorted_memories[:limit]:
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            
        return sorted_memories[:limit]
        
    def _calculate_importance(self, interaction_data: Dict[str, Any]) -> float:
        """Calculate the importance of a memory based on various factors."""
        importance = 0.5  # Base importance
        
        # Emotional intensity affects importance
        if 'emotion' in interaction_data:
            emotion_intensity = max(abs(v) for v in interaction_data['emotion'].values())
            importance += emotion_intensity * 0.3
            
        # User interaction importance
        if 'user_interaction' in interaction_data:
            importance += 0.2
            
        # Novelty factor
        if self._is_novel_interaction(interaction_data):
            importance += 0.2
            
        return min(1.0, importance)
        
    def _calculate_relevance(self, memory: Memory, context: Dict[str, Any]) -> float:
        """Calculate how relevant a memory is to the current context."""
        relevance = 0.0
        
        # Recency factor
        time_diff = (datetime.now() - memory.timestamp).total_seconds()
        recency_factor = 1.0 / (1.0 + time_diff / 3600)  # Decay over hours
        relevance += recency_factor * 0.3
        
        # Importance factor
        relevance += memory.importance * 0.3
        
        # Emotional relevance
        if 'emotion' in context and 'emotion' in memory.content:
            emotion_similarity = self._calculate_emotion_similarity(
                context['emotion'],
                memory.content['emotion']
            )
            relevance += emotion_similarity * 0.2
            
        # Context similarity
        if 'environment_context' in context and 'environment_context' in memory.content:
            context_similarity = self._calculate_context_similarity(
                context['environment_context'],
                memory.content['environment_context']
            )
            relevance += context_similarity * 0.2
            
        return min(1.0, relevance)
        
    def _is_novel_interaction(self, interaction_data: Dict[str, Any]) -> bool:
        """Check if an interaction is novel compared to recent memories."""
        # TODO: Implement novelty detection
        return True
        
    def _calculate_emotion_similarity(self, emotion1: Dict[str, float], emotion2: Dict[str, float]) -> float:
        """Calculate similarity between two emotional states."""
        # Convert emotion dictionaries to vectors
        vec1 = np.array([emotion1.get(e, 0.0) for e in self.emotions])
        vec2 = np.array([emotion2.get(e, 0.0) for e in self.emotions])
        
        # Calculate cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)
        
    def _calculate_context_similarity(self, context1: Dict[str, Any], context2: Dict[str, Any]) -> float:
        """Calculate similarity between two contexts."""
        # TODO: Implement context similarity calculation
        return 0.5
        
    def _consolidate_oldest_memory(self) -> None:
        """Move the oldest memory from short-term to long-term storage."""
        if not self.short_term_memories:
            return
            
        oldest_memory = self.short_term_memories.pop(0)
        
        # Only consolidate if memory is important enough
        if oldest_memory.importance >= self.consolidation_threshold:
            memory_id = f"memory_{len(self.long_term_memories)}"
            self.long_term_memories[memory_id] = oldest_memory
            
    def save_to_file(self, filepath: str) -> None:
        """Save memory system state to file."""
        data = {
            'short_term_memories': [m.to_dict() for m in self.short_term_memories],
            'long_term_memories': {
                k: v.to_dict() for k, v in self.long_term_memories.items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
            
    def load_from_file(self, filepath: str) -> None:
        """Load memory system state from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        self.short_term_memories = [
            Memory.from_dict(m) for m in data['short_term_memories']
        ]
        self.long_term_memories = {
            k: Memory.from_dict(v) for k, v in data['long_term_memories'].items()
        } 