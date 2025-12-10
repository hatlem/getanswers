"""Conversation model for email threads."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON

from .base import Base


class Conversation(Base):
    """Conversation model representing an email thread."""

    __tablename__ = "conversations"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign key
    objective_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("objectives.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Gmail thread ID
    gmail_thread_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Participants (array of email addresses)
    participants: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    objective: Mapped["Objective"] = relationship("Objective", back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.sent_at"
    )
    agent_actions: Mapped[list["AgentAction"]] = relationship(
        "AgentAction",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, gmail_thread_id={self.gmail_thread_id})>"
