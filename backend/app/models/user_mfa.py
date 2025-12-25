"""User MFA model for multi-factor authentication."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import String, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON

from .base import Base


class MFAMethod(str, Enum):
    """Supported MFA methods."""
    TOTP = "totp"  # Time-based One-Time Password (Google Authenticator, Authy)
    EMAIL = "email"  # Email-based verification
    SMS = "sms"  # SMS-based verification (future)
    WEBAUTHN = "webauthn"  # Hardware keys (future)


class UserMFA(Base):
    """
    User MFA configuration model.

    Supports TOTP (Time-based One-Time Password) authentication
    compatible with Google Authenticator, Authy, and other TOTP apps.

    Security features:
    - Encrypted TOTP secret storage
    - Backup codes for account recovery
    - Rate limiting for verification attempts
    """

    __tablename__ = "user_mfa"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # User relationship (one-to-one)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # TOTP configuration
    totp_secret: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)  # Encrypted
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    totp_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Backup codes (hashed, JSON array)
    backup_codes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    backup_codes_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    backup_codes_remaining: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Email MFA (as fallback or primary)
    email_mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Rate limiting for failed attempts
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_failed_attempt: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Usage tracking
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_verifications: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="mfa")

    def __repr__(self) -> str:
        return f"<UserMFA(id={self.id}, user_id={self.user_id}, totp_enabled={self.totp_enabled})>"

    @property
    def is_enabled(self) -> bool:
        """Check if any MFA method is enabled."""
        return self.totp_enabled or self.email_mfa_enabled

    @property
    def is_locked(self) -> bool:
        """Check if MFA is currently locked due to failed attempts."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until

    def record_failed_attempt(self) -> None:
        """Record a failed MFA verification attempt."""
        self.failed_attempts += 1
        self.last_failed_attempt = datetime.utcnow()

        # Lock after 5 failed attempts for 15 minutes
        if self.failed_attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)

    def record_successful_verification(self) -> None:
        """Record a successful MFA verification."""
        self.failed_attempts = 0
        self.last_failed_attempt = None
        self.locked_until = None
        self.last_used = datetime.utcnow()
        self.total_verifications += 1

    def use_backup_code(self, code_index: int) -> None:
        """Mark a backup code as used."""
        if self.backup_codes and "codes" in self.backup_codes:
            if 0 <= code_index < len(self.backup_codes["codes"]):
                self.backup_codes["codes"][code_index]["used"] = True
                self.backup_codes["codes"][code_index]["used_at"] = datetime.utcnow().isoformat()
                self.backup_codes_remaining = max(0, self.backup_codes_remaining - 1)
