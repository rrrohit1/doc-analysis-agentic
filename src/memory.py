# --- Chat Memory Manager ---
from datetime import datetime
from collections import deque

class ChatMemoryManager:
    """Manages chat history with a maximum of 10 recent messages."""
    
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self.chat_history = deque(maxlen=max_messages)
    
    def add_message(self, role: str, content: str):
        """Add a new message to chat history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.chat_history.append(message)
    
    def format_for_prompt(self) -> str:
        """Format chat history for inclusion in the prompt."""
        if not self.chat_history:
            return ""
        
        formatted_history = []
        for msg in self.chat_history:
            role = msg["role"].capitalize()
            content = msg["content"]
            formatted_history.append(f"{role}: {content}")
        
        return "Previous conversation:\n" + "\n".join(formatted_history) + "\n"
    
    def clear_history(self):
        """Clear all chat history."""
        self.chat_history.clear()