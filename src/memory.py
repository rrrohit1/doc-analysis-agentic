"""
Chat Memory Manager

Manages conversation history with configurable message limits.
Provides conversation context for AI model prompts.
"""

from datetime import datetime
from collections import deque
from typing import Dict, List, Optional


class ChatMemoryManager:
    """
    Manages chat history with a rolling window of recent messages.
    
    Attributes:
        max_messages (int): Maximum number of messages to retain
        chat_history (deque): Deque storing recent conversation messages
    """
    
    def __init__(self, max_messages: int = 10):
        """
        Initialize the chat memory manager.
        
        Args:
            max_messages (int): Maximum number of messages to keep in memory
        """
        self.max_messages = max_messages
        self.chat_history = deque(maxlen=max_messages)
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a new message to the chat history.
        
        Args:
            role (str): Message role ('user' or 'assistant')
            content (str): Message content
        """
        if not isinstance(role, str) or role not in ['user', 'assistant']:
            raise ValueError("Role must be either 'user' or 'assistant'")
        
        if not isinstance(content, str):
            raise ValueError("Content must be a string")
        
        message = {
            "role": role,
            "content": content.strip(),
            "timestamp": datetime.now().isoformat()
        }
        self.chat_history.append(message)
    
    def format_for_prompt(self) -> str:
        """
        Format chat history for inclusion in AI model prompts.
        
        Returns:
            str: Formatted conversation history or empty string if no history
        """
        if not self.chat_history:
            return ""
        
        formatted_messages = []
        for message in self.chat_history:
            role = message["role"].capitalize()
            content = message["content"]
            formatted_messages.append(f"{role}: {content}")
        
        return "Previous conversation:\n" + "\n".join(formatted_messages) + "\n"
    
    def get_recent_messages(self, count: Optional[int] = None) -> List[Dict]:
        """
        Get the most recent messages from history.
        
        Args:
            count (int, optional): Number of recent messages to retrieve.
                                 If None, returns all messages.
        
        Returns:
            List[Dict]: List of recent message dictionaries
        """
        if count is None:
            return list(self.chat_history)
        
        return list(self.chat_history)[-count:] if self.chat_history else []
    
    def clear_history(self) -> None:
        """Clear all chat history."""
        self.chat_history.clear()
    
    def get_message_count(self) -> int:
        """
        Get the current number of messages in history.
        
        Returns:
            int: Number of messages currently stored
        """
        return len(self.chat_history)
    
    def is_empty(self) -> bool:
        """
        Check if the chat history is empty.
        
        Returns:
            bool: True if no messages are stored, False otherwise
        """
        return len(self.chat_history) == 0
    
    def get_memory_stats(self) -> Dict[str, int]:
        """
        Get memory usage statistics.
        
        Returns:
            Dict[str, int]: Dictionary containing memory statistics
        """
        return {
            "current_messages": len(self.chat_history),
            "max_messages": self.max_messages,
            "remaining_capacity": self.max_messages - len(self.chat_history)
        }
    
    def export_history(self) -> List[Dict]:
        """
        Export complete chat history for backup or analysis.
        
        Returns:
            List[Dict]: Complete chat history as a list of dictionaries
        """
        return [dict(message) for message in self.chat_history]
    
    def import_history(self, history: List[Dict]) -> None:
        """
        Import chat history from a list of message dictionaries.
        
        Args:
            history (List[Dict]): List of message dictionaries to import
        """
        self.clear_history()
        for message in history[-self.max_messages:]:  # Only import recent messages
            if all(key in message for key in ["role", "content"]):
                self.chat_history.append(message)


# Example usage and testing
if __name__ == "__main__":
    # Create a memory manager for testing
    memory = ChatMemoryManager(max_messages=5)
    
    # Test adding messages
    memory.add_message("user", "Hello, how are you?")
    memory.add_message("assistant", "I'm doing well, thank you! How can I help you?")
    memory.add_message("user", "Can you explain quantum physics?")
    memory.add_message("assistant", "Quantum physics is the branch of physics that studies...")
    
    # Test formatting for prompt
    print("Formatted for prompt:")
    print(memory.format_for_prompt())
    
    # Test memory stats
    print("\nMemory stats:")
    print(memory.get_memory_stats())
    
    # Test overflow (adding more than max_messages)
    memory.add_message("user", "Tell me about AI")
    memory.add_message("assistant", "AI is artificial intelligence...")
    memory.add_message("user", "What about machine learning?")
    
    print(f"\nAfter overflow - Messages count: {memory.get_message_count()}")
    print("Recent messages:")
    for msg in memory.get_recent_messages():
        print(f"  {msg['role']}: {msg['content'][:50]}...")