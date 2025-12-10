"""Message model for individual emails in a conversation."""
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base


class MessageDirection(str, Enum):
    """Direction of a message."""
    INCOMING = "incoming"
    OUTGOING = "outgoing"


class Message(Base):
    """Message model representing an individual email."""

    __tablename__ = "messages"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign key
    conversation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Gmail message ID
    gmail_message_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    # Sender information
    sender_email: Mapped[str] = mapped_column(String(255), nullable=False)
    sender_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Content
    subject: Mapped[str] = mapped_column(String(512), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    body_html: Mapped[str] = mapped_column(Text, nullable=False)

    # Direction
    direction: Mapped[MessageDirection] = mapped_column(String(20), nullable=False)

    # Timestamps
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, subject={self.subject}, direction={self.direction})>"
