"""Organization model for multi-tenant support."""
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String, Text, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .subscription import Subscription


class OrganizationRole(str, Enum):
    """Roles within an organization."""
    OWNER = "owner"       # Full control, can delete org
    ADMIN = "admin"       # Manage members, settings
    MANAGER = "manager"   # Manage content, limited settings
    MEMBER = "member"     # Regular access
    GUEST = "guest"       # Read-only access


class Organization(Base):
    """Organization model for multi-tenancy."""

    __tablename__ = "organizations"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Organization details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Settings
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

    # Branding
    logo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_personal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    members: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription",
        back_populates="organization",
        uselist=False,
        foreign_keys="Subscription.organization_id"
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"


class OrganizationMember(Base):
    """Junction table for user-organization membership with roles."""

    __tablename__ = "organization_members"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign keys
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Role
    role: Mapped[OrganizationRole] = mapped_column(
        String(20),
        default=OrganizationRole.MEMBER,
        nullable=False
    )

    # Permissions override (for fine-grained control)
    permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Invitation tracking
    invited_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    invited_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="members"
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="organization_memberships",
        foreign_keys=[user_id]
    )
    invited_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[invited_by_id]
    )

    # Indexes
    __table_args__ = (
        Index("ix_org_member_org_user", "organization_id", "user_id", unique=True),
        Index("ix_org_member_user", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<OrganizationMember(org={self.organization_id}, user={self.user_id}, role={self.role})>"

    def has_permission(self, permission: str) -> bool:
        """Check if member has a specific permission."""
        # Check override permissions first
        if self.permissions and permission in self.permissions:
            return self.permissions[permission]

        # Fall back to role-based permissions
        role_permissions = {
            OrganizationRole.OWNER: ["*"],  # All permissions
            OrganizationRole.ADMIN: [
                "manage_members", "manage_settings", "manage_billing",
                "view_analytics", "manage_content", "view_content"
            ],
            OrganizationRole.MANAGER: [
                "manage_content", "view_content", "view_analytics"
            ],
            OrganizationRole.MEMBER: ["view_content", "create_content"],
            OrganizationRole.GUEST: ["view_content"],
        }

        perms = role_permissions.get(self.role, [])
        return "*" in perms or permission in perms


class OrganizationInvite(Base):
    """Pending organization invitations."""

    __tablename__ = "organization_invites"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign key
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )

    # Invite details
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[OrganizationRole] = mapped_column(
        String(20),
        default=OrganizationRole.MEMBER,
        nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # Who invited
    invited_by_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Status
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    invited_by: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<OrganizationInvite(org={self.organization_id}, email={self.email})>"

    @property
    def is_expired(self) -> bool:
        """Check if invite has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_accepted(self) -> bool:
        """Check if invite has been accepted."""
        return self.accepted_at is not None
