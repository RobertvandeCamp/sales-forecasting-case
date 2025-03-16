import os
import json
from typing import List, Dict, Any
from app.models.schema import ChatHistory, ChatMessage
from app.utils.logger import get_logger

logger = get_logger()

class ConversationStorage:
    def __init__(self, storage_dir="conversations"):
        """
        Initialize conversation storage.
        
        Args:
            storage_dir (str): Directory to store conversation files
        """
        # Create storage directory if it doesn't exist
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        logger.info(f"Conversation storage initialized at {self.storage_dir}")
        
    def get_available_users(self) -> List[str]:
        """
        Get list of users with saved conversations.
        
        Returns:
            List[str]: List of usernames
        """
        users = []
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    username = filename.replace('.json', '')
                    users.append(username)
            return users
        except Exception as e:
            logger.error(f"Error getting available users: {str(e)}")
            return []
    
    def save_conversation(self, username: str, chat_history: ChatHistory) -> bool:
        """
        Save a user's conversation.
        
        Args:
            username (str): Username
            chat_history (ChatHistory): Chat history to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not username:
            logger.warning("No username provided, conversation not saved")
            return False
            
        try:
            # Convert chat history to dictionary
            history_dict = {
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    } for msg in chat_history.messages
                ]
            }
            
            # Save to file
            filepath = os.path.join(self.storage_dir, f"{username}.json")
            with open(filepath, 'w') as f:
                json.dump(history_dict, f, indent=2)
                
            logger.info(f"Saved conversation for user {username}")
            return True
        except Exception as e:
            logger.error(f"Error saving conversation for user {username}: {str(e)}")
            return False
    
    def load_conversation(self, username: str) -> ChatHistory:
        """
        Load a user's conversation.
        
        Args:
            username (str): Username
            
        Returns:
            ChatHistory: Loaded chat history or empty history if none exists
        """
        if not username:
            logger.warning("No username provided, returning empty conversation")
            return ChatHistory(messages=[])
            
        filepath = os.path.join(self.storage_dir, f"{username}.json")
        
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    history_dict = json.load(f)
                
                # Convert dictionary to ChatHistory
                messages = []
                for msg in history_dict["messages"]:
                    messages.append(ChatMessage(
                        role=msg["role"],
                        content=msg["content"],
                        timestamp=msg["timestamp"]
                    ))
                
                logger.info(f"Loaded conversation for user {username}")
                return ChatHistory(messages=messages)
            else:
                logger.info(f"No existing conversation for user {username}")
                return ChatHistory(messages=[])
        except Exception as e:
            logger.error(f"Error loading conversation for user {username}: {str(e)}")
            return ChatHistory(messages=[]) 