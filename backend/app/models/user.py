"""User model for authentication and user management."""
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON

from .base import Base

if TYPE_CHECKING:
    from .organization import Organization, OrganizationMember
    from .user_session import UserSession
    from .device_history import DeviceHistory
    from .user_mfa import UserMFA
    from .usage_metrics import UsageMetrics


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

    # OAuth provider IDs
    google_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    # Profile
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Super admin flag (platform-wide admin)
    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Current active organization context
    current_organization_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True
    )

    # Preferences
    autonomy_level: Mapped[AutonomyLevel] = mapped_column(
        String(20),
        default=AutonomyLevel.MEDIUM,
        nullable=False
    )

    # Email OAuth credentials (encrypted JSON)
    gmail_credentials: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    outlook_credentials: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    smtp_credentials: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Active email provider: 'gmail', 'outlook', 'smtp', or None
    email_provider: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Onboarding status
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Password setup needed (for users who registered via quick signup with auto-generated password)
    needs_password_setup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

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

    # Organization relationships
    current_organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        foreign_keys=[current_organization_id]
    )
    organization_memberships: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="user",
        foreign_keys="OrganizationMember.user_id",
        cascade="all, delete-orphan"
    )

    # Security and compliance relationships
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    device_history: Mapped[list["DeviceHistory"]] = relationship(
        "DeviceHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    mfa: Mapped[Optional["UserMFA"]] = relationship(
        "UserMFA",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    usage_metrics: Mapped[list["UsageMetrics"]] = relationship(
        "UsageMetrics",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"

    @property
    def is_platform_admin(self) -> bool:
        """Check if user is a platform super admin."""
        return self.is_super_admin
