"""
Conversation State Management
"""

class ConversationState:
    def __init__(self):
        self.active = False
        self.history = []
        self.speaking = False
        self.stop_requested = False
        
    def activate(self):
        """Start a new conversation"""
        self.active = True
        self.history = []
        self.stop_requested = False
        
    def deactivate(self):
        """End the current conversation"""
        self.active = False
        
    def add_utterance(self, role, content):
        """Add an utterance to the conversation history"""
        self.history.append({"role": role, "content": content})
        
    def get_history(self):
        """Get full conversation history"""
        return self.history
        
    def start_speaking(self):
        """Mark speech as started"""
        self.speaking = True
        
    def stop_speaking(self):
        """Mark speech as stopped"""
        self.speaking = False
        
    def request_stop(self):
        """Request to stop current speech"""
        self.stop_requested = True
        
    def clear_stop_request(self):
        """Clear stop request flag"""
        self.stop_requested = False

# Global conversation state instance
conversation = ConversationState()