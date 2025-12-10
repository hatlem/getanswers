"""Agent action model for audit logging of AI actions."""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base


class ActionType(str, Enum):
    """Type of agent action."""
    DRAFT = "draft"
    SEND = "send"
    FILE = "file"
    SCHEDULE = "schedule"
    TRIAGE = "triage"


class RiskLevel(str, Enum):
    """Risk level of an action."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionStatus(str, Enum):
    """Status of an agent action."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"


class AgentAction(Base):
    """Agent action model for audit logging."""

    __tablename__ = "agent_actions"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign key
    conversation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Action details
    action_type: Mapped[ActionType] = mapped_column(String(50), nullable=False)
    proposed_content: Mapped[str] = mapped_column(Text, nullable=False)

    # Risk assessment
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(String(20), nullable=False)
    priority_score: Mapped[int] = mapped_column(default=50, nullable=False)

    # Status and user feedback
    status: Mapped[ActionStatus] = mapped_column(
        String(20),
        default=ActionStatus.PENDING,
        nullable=False
    )
    user_edit: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    override_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    escalation_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="agent_actions")

    def __repr__(self) -> str:
        return f"<AgentAction(id={self.id}, action_type={self.action_type}, status={self.status})>"
