"""Device history model for tracking user devices and detecting anomalies."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import String, Integer, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON

from .base import Base


class TrustLevel(str, Enum):
    """Trust level for a device."""
    TRUSTED = "trusted"
    UNKNOWN = "unknown"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"


class DeviceHistory(Base):
    """
    Device history model for tracking user devices over time.

    This enables:
    - Detecting new vs known devices
    - Tracking device trust levels
    - Identifying suspicious device patterns
    - Building user device profiles
    """

    __tablename__ = "device_history"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # User relationship
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Device identification
    device_fingerprint: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    device_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    browser: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Device name (user-friendly, can be set by user)
    device_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Location info (last known)
    last_ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    last_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_country_code: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)

    # Geolocation (for impossible travel detection)
    last_latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    last_longitude: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Trust and security
    trust_level: Mapped[str] = mapped_column(
        String(20),
        default=TrustLevel.UNKNOWN,
        nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Usage statistics
    login_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Suspicious activity tracking
    suspicious_activity_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_suspicious_activity: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="device_history")

    __table_args__ = (
        UniqueConstraint('user_id', 'device_fingerprint', name='uq_user_device'),
        Index('ix_device_history_user_trust', 'user_id', 'trust_level'),
        Index('ix_device_history_last_seen', 'last_seen'),
    )

    def __repr__(self) -> str:
        return f"<DeviceHistory(id={self.id}, user_id={self.user_id}, trust={self.trust_level})>"

    def record_login(self, ip_address: str, city: str = None, country: str = None,
                     latitude: float = None, longitude: float = None) -> None:
        """Record a new login from this device."""
        self.login_count += 1
        self.last_seen = datetime.utcnow()
        self.last_ip_address = ip_address
        if city:
            self.last_city = city
        if country:
            self.last_country = country
        if latitude:
            self.last_latitude = latitude
        if longitude:
            self.last_longitude = longitude

    def mark_suspicious(self) -> None:
        """Mark this device as having suspicious activity."""
        self.suspicious_activity_count += 1
        self.last_suspicious_activity = datetime.utcnow()
        if self.suspicious_activity_count >= 3:
            self.trust_level = TrustLevel.SUSPICIOUS

    def mark_trusted(self) -> None:
        """Mark this device as trusted (user verified)."""
        self.trust_level = TrustLevel.TRUSTED
        self.is_verified = True
        self.verified_at = datetime.utcnow()

    def block(self) -> None:
        """Block this device."""
        self.trust_level = TrustLevel.BLOCKED
