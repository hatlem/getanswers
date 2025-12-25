"""User session model for session management and device tracking."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Boolean, ForeignKey, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON

from .base import Base


class UserSession(Base):
    """
    User session model for tracking active sessions and devices.

    This model enables:
    - Limiting concurrent sessions per user
    - Tracking device fingerprints and IP addresses
    - Detecting suspicious login patterns
    - Server-side session invalidation
    """

    __tablename__ = "user_sessions"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # User relationship
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # JWT identification
    token_jti: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    # Device information
    device_fingerprint: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    device_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # desktop, mobile, tablet
    browser: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Location information
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv6 compatible
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)

    # Session status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revoked_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Metadata
    is_new_device: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_new_location: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trust_score: Mapped[Optional[float]] = mapped_column(nullable=True)  # 0.0-1.0

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    __table_args__ = (
        Index('ix_user_sessions_user_active', 'user_id', 'is_active'),
        Index('ix_user_sessions_expires', 'expires_at'),
        Index('ix_user_sessions_ip', 'ip_address'),
    )

    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id}, ip={self.ip_address}, active={self.is_active})>"

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if session is both active and not expired."""
        return self.is_active and not self.is_expired

    def revoke(self, reason: str = "manual_revoke") -> None:
        """Revoke this session."""
        self.is_active = False
        self.revoked_at = datetime.utcnow()
        self.revoked_reason = reason

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
