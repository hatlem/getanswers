"""Objective model representing user missions/goals."""
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base


class ObjectiveStatus(str, Enum):
    """Status of an objective."""
    WAITING_ON_YOU = "waiting_on_you"
    WAITING_ON_OTHERS = "waiting_on_others"
    HANDLED = "handled"
    SCHEDULED = "scheduled"
    MUTED = "muted"


class Objective(Base):
    """Objective (mission) model."""

    __tablename__ = "objectives"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign key
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Content
    title: Mapped[str] = mapped_column(String(512), nullable=False)

    # Status
    status: Mapped[ObjectiveStatus] = mapped_column(
        String(50),
        default=ObjectiveStatus.WAITING_ON_YOU,
        nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="objectives")
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="objective",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Objective(id={self.id}, title={self.title}, status={self.status})>"
