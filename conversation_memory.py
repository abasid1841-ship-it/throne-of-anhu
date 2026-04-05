"""Conversation memory management for the Throne of Anhu."""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import uuid

from sqlalchemy.orm import Session

from db_models import ChatThread, ChatMessage


def get_or_create_thread(
    db: Session,
    conversation_id: Optional[str],
    user_id: Optional[str] = None,
) -> Tuple[str, bool]:
    """Get existing thread or create a new one. Returns (thread_id, is_new)."""
    if conversation_id:
        thread = db.query(ChatThread).filter(ChatThread.id == conversation_id).first()
        if thread:
            return thread.id, False
    
    thread_id = conversation_id or str(uuid.uuid4())
    
    if user_id:
        new_thread = ChatThread(
            id=thread_id,
            user_id=user_id,
            title="New Conversation",
        )
        db.add(new_thread)
        db.commit()
        return thread_id, True
    
    return thread_id, True


def save_message(
    db: Session,
    thread_id: str,
    role: str,
    content: str,
    persona: str = "RA",
    mode: str = "outer_court",
) -> None:
    """Save a message to the conversation thread."""
    thread = db.query(ChatThread).filter(ChatThread.id == thread_id).first()
    if not thread:
        return
    
    message = ChatMessage(
        thread_id=thread_id,
        role=role,
        content=content,
        persona=persona,
        mode=mode,
    )
    db.add(message)
    
    thread.updated_at = datetime.utcnow()
    db.commit()


def get_conversation_history(
    db: Session,
    thread_id: str,
    max_turns: int = 6,
) -> List[Dict[str, str]]:
    """Get recent conversation history for context."""
    thread = db.query(ChatThread).filter(ChatThread.id == thread_id).first()
    if not thread:
        return []
    
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.thread_id == thread_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(max_turns * 2)
        .all()
    )
    
    messages.reverse()
    
    history = []
    for msg in messages:
        history.append({
            "role": msg.role,
            "content": msg.content,
        })
    
    return history


def format_conversation_context(history: List[Dict[str, str]]) -> str:
    """Format conversation history into a context string for the AI."""
    if not history:
        return ""
    
    lines = ["PREVIOUS CONVERSATION:"]
    for msg in history:
        role_label = "User" if msg["role"] == "user" else "Throne"
        content = msg["content"]
        if len(content) > 300:
            content = content[:300] + "..."
        lines.append(f"{role_label}: {content}")
    
    return "\n".join(lines)


_anonymous_memory: Dict[str, List[Dict[str, str]]] = {}
_pending_topics: Dict[str, str] = {}


def get_pending_topic(conversation_id: str) -> Optional[str]:
    """Get the pending topic for a conversation (what the Throne offered to teach)."""
    return _pending_topics.get(conversation_id)


def set_pending_topic(conversation_id: str, topic: str) -> None:
    """Store what topic the Throne offered to teach about."""
    _pending_topics[conversation_id] = topic
    if len(_pending_topics) > 1000:
        oldest_keys = list(_pending_topics.keys())[:100]
        for key in oldest_keys:
            del _pending_topics[key]


def clear_pending_topic(conversation_id: str) -> None:
    """Clear the pending topic after it's been fulfilled."""
    if conversation_id in _pending_topics:
        del _pending_topics[conversation_id]


def get_anonymous_history(conversation_id: str, max_turns: int = 6) -> List[Dict[str, str]]:
    """Get conversation history for anonymous users (in-memory)."""
    if conversation_id not in _anonymous_memory:
        return []
    
    history = _anonymous_memory[conversation_id]
    return history[-(max_turns * 2):]


def save_anonymous_message(
    conversation_id: str,
    role: str,
    content: str,
) -> None:
    """Save message for anonymous user (in-memory)."""
    if conversation_id not in _anonymous_memory:
        _anonymous_memory[conversation_id] = []
    
    _anonymous_memory[conversation_id].append({
        "role": role,
        "content": content,
    })
    
    if len(_anonymous_memory[conversation_id]) > 20:
        _anonymous_memory[conversation_id] = _anonymous_memory[conversation_id][-20:]
    
    if len(_anonymous_memory) > 1000:
        oldest_keys = list(_anonymous_memory.keys())[:100]
        for key in oldest_keys:
            del _anonymous_memory[key]


def create_conversation_id() -> str:
    """Generate a new conversation ID."""
    return str(uuid.uuid4())
