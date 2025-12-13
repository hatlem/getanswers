"""Feature flag models for controlling feature access."""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base


class FeatureName(str, Enum):
    """Available feature flags."""
    # AI Features
    AI_AUTO_REPLY = "ai_auto_reply"
    AI_TRIAGE = "ai_triage"
    AI_SUMMARY = "ai_summary"

    # Email Features
    EMAIL_SCHEDULING = "email_scheduling"
    EMAIL_TEMPLATES = "email_templates"
    EMAIL_TRACKING = "email_tracking"

    # Collaboration
    TEAM_SHARING = "team_sharing"
    DELEGATED_ACCESS = "delegated_access"

    # Advanced
    CUSTOM_POLICIES = "custom_policies"
    API_ACCESS = "api_access"
    WEBHOOKS = "webhooks"
    ANALYTICS = "analytics"

    # Experimental
    BETA_FEATURES = "beta_features"


class FeatureFlag(Base):
    """Feature flag configuration per user."""

    __tablename__ = "feature_flags"

    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # User relationship (nullable for global flags)
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Feature identification
    feature: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # State
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Override info
    override_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    overridden_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="feature_flags")

    def __repr__(self) -> str:
        return f"<FeatureFlag(id={self.id}, feature={self.feature}, enabled={self.enabled}, user_id={self.user_id})>"


# Default feature availability per plan
PLAN_FEATURES = {
    "free": {
        FeatureName.AI_TRIAGE: True,
        FeatureName.AI_SUMMARY: True,
        FeatureName.AI_AUTO_REPLY: False,
        FeatureName.EMAIL_SCHEDULING: False,
        FeatureName.EMAIL_TEMPLATES: False,
        FeatureName.EMAIL_TRACKING: False,
        FeatureName.TEAM_SHARING: False,
        FeatureName.DELEGATED_ACCESS: False,
        FeatureName.CUSTOM_POLICIES: False,
        FeatureName.API_ACCESS: False,
        FeatureName.WEBHOOKS: False,
        FeatureName.ANALYTICS: False,
        FeatureName.BETA_FEATURES: False,
    },
    "starter": {
        FeatureName.AI_TRIAGE: True,
        FeatureName.AI_SUMMARY: True,
        FeatureName.AI_AUTO_REPLY: True,
        FeatureName.EMAIL_SCHEDULING: True,
        FeatureName.EMAIL_TEMPLATES: True,
        FeatureName.EMAIL_TRACKING: False,
        FeatureName.TEAM_SHARING: False,
        FeatureName.DELEGATED_ACCESS: False,
        FeatureName.CUSTOM_POLICIES: True,
        FeatureName.API_ACCESS: False,
        FeatureName.WEBHOOKS: False,
        FeatureName.ANALYTICS: True,
        FeatureName.BETA_FEATURES: False,
    },
    "pro": {
        FeatureName.AI_TRIAGE: True,
        FeatureName.AI_SUMMARY: True,
        FeatureName.AI_AUTO_REPLY: True,
        FeatureName.EMAIL_SCHEDULING: True,
        FeatureName.EMAIL_TEMPLATES: True,
        FeatureName.EMAIL_TRACKING: True,
        FeatureName.TEAM_SHARING: True,
        FeatureName.DELEGATED_ACCESS: True,
        FeatureName.CUSTOM_POLICIES: True,
        FeatureName.API_ACCESS: True,
        FeatureName.WEBHOOKS: True,
        FeatureName.ANALYTICS: True,
        FeatureName.BETA_FEATURES: False,
    },
    "enterprise": {
        FeatureName.AI_TRIAGE: True,
        FeatureName.AI_SUMMARY: True,
        FeatureName.AI_AUTO_REPLY: True,
        FeatureName.EMAIL_SCHEDULING: True,
        FeatureName.EMAIL_TEMPLATES: True,
        FeatureName.EMAIL_TRACKING: True,
        FeatureName.TEAM_SHARING: True,
        FeatureName.DELEGATED_ACCESS: True,
        FeatureName.CUSTOM_POLICIES: True,
        FeatureName.API_ACCESS: True,
        FeatureName.WEBHOOKS: True,
        FeatureName.ANALYTICS: True,
        FeatureName.BETA_FEATURES: True,
    },
}


def get_default_feature_state(plan: str, feature: FeatureName) -> bool:
    """Get the default state of a feature for a given plan."""
    plan_features = PLAN_FEATURES.get(plan, PLAN_FEATURES["free"])
    return plan_features.get(feature, False)
