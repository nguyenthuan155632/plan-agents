"""
Core message model and utilities for the dual AI collaboration framework.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Role(str, Enum):
    """Message sender role."""
    AGENT_A = "AgentA"
    AGENT_B = "AgentB"
    HUMAN = "Human"


class Signal(str, Enum):
    """Communication signal types."""
    CONTINUE = "continue"  # Agent finished, next agent can respond
    STOP = "stop"          # End the conversation session
    HANDOVER = "handover"  # Transfer control to human moderator


class Message(BaseModel):
    """Message schema for agent communication."""
    
    id: Optional[int] = None
    session_id: str
    role: Role
    content: str
    signal: Signal
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role.value,
            "content": self.content,
            "signal": self.signal.value,
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_markdown(self) -> str:
        """Convert message to markdown format."""
        return f"""
## {self.role.value} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

**Signal:** `{self.signal.value}`

{self.content}

---
"""

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Create message from dictionary."""
        return cls(
            id=data.get("id"),
            session_id=data["session_id"],
            role=Role(data["role"]),
            content=data["content"],
            signal=Signal(data["signal"]),
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class Session(BaseModel):
    """Conversation session."""
    
    id: str
    topic: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    status: str = "active"  # active, paused, completed
    
    def to_dict(self) -> dict:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "topic": self.topic,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "status": self.status
        }

