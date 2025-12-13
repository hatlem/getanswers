"""User model for authentication and user management."""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON

from .base import Base


class AutonomyLevel(str, Enum):
    """User autonomy level for agent actions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class User(Base):
    """User model with authentication and preferences."""

    __tablename__ = "users"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Profile
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Preferences
    autonomy_level: Mapped[AutonomyLevel] = mapped_column(
        String(20),
        default=AutonomyLevel.MEDIUM,
        nullable=False
    )

    # Gmail OAuth credentials (encrypted)
    gmail_credentials: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    magic_links: Mapped[list["MagicLink"]] = relationship(
        "MagicLink",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    objectives: Mapped[list["Objective"]] = relationship(
        "Objective",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    policies: Mapped[list["Policy"]] = relationship(
        "Policy",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    feature_flags: Mapped[list["FeatureFlag"]] = relationship(
        "FeatureFlag",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
