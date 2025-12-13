"""Feature flag service for controlling feature access."""
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.subscription import Subscription, PlanTier
from app.models.feature_flag import FeatureFlag, FeatureName, get_default_feature_state

logger = logging.getLogger(__name__)


class FeatureService:
    """Service for checking feature flag states."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_feature_enabled(self, user_id: UUID, feature: FeatureName) -> bool:
        """Check if a feature is enabled for a user.

        Priority:
        1. User-specific override (FeatureFlag record)
        2. Plan-based default (from PLAN_FEATURES)
        """
        # Check for user-specific override
        result = await self.db.execute(
            select(FeatureFlag).where(
                FeatureFlag.user_id == user_id,
                FeatureFlag.feature == feature.value
            )
        )
        flag = result.scalar_one_or_none()

        if flag is not None:
            return flag.enabled

        # Fall back to plan-based default
        plan = await self._get_user_plan(user_id)
        return get_default_feature_state(plan.value, feature)

    async def get_all_features(self, user_id: UUID) -> dict[str, bool]:
        """Get all feature states for a user."""
        plan = await self._get_user_plan(user_id)

        # Start with plan defaults
        features = {
            feature.value: get_default_feature_state(plan.value, feature)
            for feature in FeatureName
        }

        # Apply user-specific overrides
        result = await self.db.execute(
            select(FeatureFlag).where(FeatureFlag.user_id == user_id)
        )
        overrides = result.scalars().all()

        for override in overrides:
            if override.feature in features:
                features[override.feature] = override.enabled

        return features

    async def set_feature_override(
        self,
        user_id: UUID,
        feature: FeatureName,
        enabled: bool,
        reason: Optional[str] = None,
        overridden_by: Optional[str] = None,
    ) -> FeatureFlag:
        """Set a user-specific feature override."""
        result = await self.db.execute(
            select(FeatureFlag).where(
                FeatureFlag.user_id == user_id,
                FeatureFlag.feature == feature.value
            )
        )
        flag = result.scalar_one_or_none()

        if flag:
            flag.enabled = enabled
            flag.override_reason = reason
            flag.overridden_by = overridden_by
        else:
            flag = FeatureFlag(
                user_id=user_id,
                feature=feature.value,
                enabled=enabled,
                override_reason=reason,
                overridden_by=overridden_by,
            )
            self.db.add(flag)

        await self.db.commit()
        await self.db.refresh(flag)

        logger.info(f"Set feature override for user {user_id}: {feature.value}={enabled}")
        return flag

    async def remove_feature_override(self, user_id: UUID, feature: FeatureName) -> bool:
        """Remove a user-specific feature override."""
        result = await self.db.execute(
            select(FeatureFlag).where(
                FeatureFlag.user_id == user_id,
                FeatureFlag.feature == feature.value
            )
        )
        flag = result.scalar_one_or_none()

        if flag:
            await self.db.delete(flag)
            await self.db.commit()
            logger.info(f"Removed feature override for user {user_id}: {feature.value}")
            return True

        return False

    async def _get_user_plan(self, user_id: UUID) -> PlanTier:
        """Get user's current plan tier."""
        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()

        if subscription and subscription.is_active:
            return subscription.plan

        return PlanTier.FREE
