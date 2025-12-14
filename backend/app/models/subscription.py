"""Subscription and billing models."""
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base

if TYPE_CHECKING:
    from .organization import Organization


class SubscriptionStatus(str, Enum):
    """Subscription status values."""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    UNPAID = "unpaid"


class PlanTier(str, Enum):
    """Available plan tiers."""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Subscription(Base):
    """User or Organization subscription model."""

    __tablename__ = "subscriptions"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # User relationship (for personal subscriptions)
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Organization relationship (for team subscriptions)
    organization_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Plan details
    plan: Mapped[PlanTier] = mapped_column(
        String(50),
        default=PlanTier.FREE,
        nullable=False
    )

    # Stripe IDs
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Status
    status: Mapped[SubscriptionStatus] = mapped_column(
        String(50),
        default=SubscriptionStatus.ACTIVE,
        nullable=False
    )

    # Billing period
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Trial
    trial_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    trial_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Cancellation
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    canceled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscription")
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization",
        back_populates="subscription",
        foreign_keys=[organization_id]
    )

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan={self.plan}, status={self.status})>"

    @property
    def is_active(self) -> bool:
        """Check if subscription is in an active state."""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]

    @property
    def is_paid(self) -> bool:
        """Check if this is a paid subscription."""
        return self.plan != PlanTier.FREE


# Plan limits configuration
PLAN_LIMITS = {
    PlanTier.FREE: {
        "emails_per_month": 50,
        "ai_responses_per_month": 20,
        "policies": 3,
        "objectives": 5,
    },
    PlanTier.STARTER: {
        "emails_per_month": 500,
        "ai_responses_per_month": 200,
        "policies": 10,
        "objectives": 25,
    },
    PlanTier.PRO: {
        "emails_per_month": 5000,
        "ai_responses_per_month": 2000,
        "policies": -1,  # Unlimited
        "objectives": -1,  # Unlimited
    },
    PlanTier.ENTERPRISE: {
        "emails_per_month": -1,  # Unlimited
        "ai_responses_per_month": -1,  # Unlimited
        "policies": -1,  # Unlimited
        "objectives": -1,  # Unlimited
    },
}


def get_plan_limit(plan: PlanTier, limit_name: str) -> int:
    """Get a specific limit for a plan. Returns -1 for unlimited."""
    return PLAN_LIMITS.get(plan, PLAN_LIMITS[PlanTier.FREE]).get(limit_name, 0)
