"""User-scoped memory saver for LangGraph"""
from typing import Dict, Optional, Any
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.base import CheckpointTuple, CheckpointMetadata
from collections import defaultdict
import uuid


class UserScopedMemorySaver(MemorySaver):
    """Memory saver that isolates data by user_id"""
    
    def __init__(self):
        super().__init__()
        # Override the storage to be user-scoped
        # Structure: {user_id: {thread_id: checkpoints}}
        self.user_storage: Dict[str, Dict[str, Any]] = defaultdict(lambda: defaultdict(dict))
    
    def get_tuple(self, config: Dict[str, Any]) -> Optional[CheckpointTuple]:
        """Get checkpoint tuple with user scoping"""
        user_id = self._get_user_id(config)
        if not user_id:
            # Fallback to default behavior if no user context
            return super().get_tuple(config)
        
        # Get thread_id from config
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return None
        
        # Check if we have data for this user and thread
        if thread_id in self.user_storage[user_id]:
            checkpoint_data = self.user_storage[user_id][thread_id]
            if checkpoint_data:
                # Get the latest checkpoint
                latest_key = max(checkpoint_data.keys())
                checkpoint = checkpoint_data[latest_key]
                # Ensure it's a CheckpointTuple, not a dict
                if isinstance(checkpoint, dict) and "checkpoint" in checkpoint:
                    return checkpoint["checkpoint"]
                return checkpoint
        
        return None
    
    def put(self, config: Dict[str, Any], checkpoint: CheckpointTuple, metadata: CheckpointMetadata, new_versions: Dict[str, Any]) -> Dict[str, Any]:
        """Put checkpoint with user scoping"""
        user_id = self._get_user_id(config)
        if not user_id:
            # Fallback to default behavior if no user context
            return super().put(config, checkpoint, metadata, new_versions)
        
        # Get or create thread_id
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            thread_id = str(uuid.uuid4())
            config.setdefault("configurable", {})["thread_id"] = thread_id
        
        # Store the checkpoint under user scope
        checkpoint_id = checkpoint["id"] if isinstance(checkpoint, dict) else str(uuid.uuid4())
        self.user_storage[user_id][thread_id][checkpoint_id] = checkpoint
        
        return {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}}
    
    def _get_user_id(self, config: Dict[str, Any]) -> Optional[str]:
        """Extract user_id from config"""
        # Check for user_id in configurable
        user_id = config.get("configurable", {}).get("user_id")
        if user_id:
            return user_id
        
        # Check for user context in config
        user_context = config.get("user_context")
        if user_context and hasattr(user_context, "user_id"):
            return user_context.user_id
        
        return None
    
    def list(self, config: Optional[Dict[str, Any]] = None) -> list:
        """List checkpoints for a user"""
        if not config:
            return []
        
        user_id = self._get_user_id(config)
        if not user_id:
            return super().list(config)
        
        # List all threads for the user
        user_checkpoints = []
        for thread_id, thread_checkpoints in self.user_storage.get(user_id, {}).items():
            for checkpoint_id, checkpoint in thread_checkpoints.items():
                user_checkpoints.append({
                    "thread_id": thread_id,
                    "checkpoint_id": checkpoint_id,
                    "checkpoint": checkpoint
                })
        
        return user_checkpoints
    
    def get_user_threads(self, user_id: str) -> list:
        """Get all thread IDs for a specific user"""
        return list(self.user_storage.get(user_id, {}).keys())
    
    def delete_user_thread(self, user_id: str, thread_id: str) -> bool:
        """Delete a specific thread for a user"""
        if user_id in self.user_storage and thread_id in self.user_storage[user_id]:
            del self.user_storage[user_id][thread_id]
            return True
        return False
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete all data for a specific user"""
        if user_id in self.user_storage:
            del self.user_storage[user_id]
            return True
        return False