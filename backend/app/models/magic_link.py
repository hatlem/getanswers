"""Magic link model for passwordless authentication."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base


class MagicLink(Base):
    """Magic link for passwordless authentication."""

    __tablename__ = "magic_links"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign key (nullable for new signups)
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True
    )

    # Email for signup/login
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    # Token (unique and indexed for fast lookups)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # Expiration and usage
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="magic_links")

    def __repr__(self) -> str:
        return f"<MagicLink(id={self.id}, email={self.email}, expires_at={self.expires_at})>"

    @property
    def is_expired(self) -> bool:
        """Check if the magic link has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_used(self) -> bool:
        """Check if the magic link has been used."""
        return self.used_at is not None
