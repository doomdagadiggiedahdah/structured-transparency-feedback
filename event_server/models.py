"""Data models for session state management."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SessionState:
    """Represents the state of a transparency session."""
    
    session_id: str
    questions: list[str] = field(default_factory=list)
    is_collecting: bool = True
    expire_time: datetime | None = None
    feedback: list[dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert session state to dictionary."""
        return {
            "session_id": self.session_id,
            "questions": self.questions,
            "is_collecting": self.is_collecting,
            "expire_time": self.expire_time.isoformat() if self.expire_time else None,
            "feedback": self.feedback,
        }
    
    def add_feedback(self, answers: list[str]) -> None:
        """Add feedback responses for current questions."""
        for question, answer in zip(self.questions, answers):
            if question and answer:
                self.feedback.append({
                    "question": question,
                    "answer": answer,
                    "timestamp": datetime.now().isoformat(),
                })
