"""Stripe integration service with dual-mode (test/live) support.

Fetches the current mode from get-platform (Mission Control) and uses
the appropriate Stripe API keys.
"""
import time
import logging
from datetime import datetime, timezone
from typing import Optional, Any
from uuid import UUID

import stripe
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.subscription import Subscription, SubscriptionStatus, PlanTier

logger = logging.getLogger(__name__)

# Dual-mode Stripe configuration
PLATFORM_SLUG = 'getanswers'
_stripe_mode_cache: dict[str, Any] = {"mode": "test", "fetched_at": 0}
CACHE_TTL = 300  # 5 minutes


def _fetch_stripe_mode() -> str:
    """Fetch stripe mode from get-platform with caching."""
    global _stripe_mode_cache

    if time.time() - _stripe_mode_cache["fetched_at"] < CACHE_TTL:
        return _stripe_mode_cache["mode"]

    api_url = settings.GET_PLATFORM_API_URL
    api_key = settings.GET_PLATFORM_API_KEY

    if not api_key:
        logger.warning('GET_PLATFORM_API_KEY not set, defaulting to test mode')
        return 'test'

    try:
        with httpx.Client(timeout=5.0) as client:
            res = client.get(
                f"{api_url}/api/platforms/{PLATFORM_SLUG}/stripe-mode",
                headers={'X-Admin-API-Key': api_key}
            )
            if res.status_code == 200:
                data = res.json()
                _stripe_mode_cache = {"mode": data.get("mode", "test"), "fetched_at": time.time()}
                return _stripe_mode_cache["mode"]
    except Exception as e:
        logger.error(f"Failed to fetch stripe mode: {e}")

    return _stripe_mode_cache.get("mode", "test")


def get_stripe_mode() -> str:
    """Get current stripe mode."""
    return _fetch_stripe_mode()


def invalidate_stripe_mode_cache():
    """Invalidate the stripe mode cache (call from webhook handler)."""
    global _stripe_mode_cache
    _stripe_mode_cache = {"mode": "test", "fetched_at": 0}


def get_stripe_client() -> Optional[stripe.StripeClient]:
    """Get the Stripe client configured for the current mode."""
    mode = _fetch_stripe_mode()

    if mode == 'live' and settings.STRIPE_LIVE_SECRET_KEY:
        return stripe.StripeClient(settings.STRIPE_LIVE_SECRET_KEY)
    elif settings.STRIPE_SECRET_KEY:
        return stripe.StripeClient(settings.STRIPE_SECRET_KEY)

    logger.warning("No Stripe API key configured")
    return None


def _configure_stripe():
    """Configure stripe.api_key for the current mode."""
    mode = _fetch_stripe_mode()
    if mode == 'live' and settings.STRIPE_LIVE_SECRET_KEY:
        stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    elif settings.STRIPE_SECRET_KEY:
        stripe.api_key = settings.STRIPE_SECRET_KEY


def get_publishable_key() -> str:
    """Get the publishable key for the current mode."""
    mode = _fetch_stripe_mode()
    if mode == 'live' and settings.STRIPE_LIVE_PUBLISHABLE_KEY:
        return settings.STRIPE_LIVE_PUBLISHABLE_KEY
    return settings.STRIPE_PUBLISHABLE_KEY or ""


class StripeService:
    """Service for Stripe billing operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        _configure_stripe()

    async def get_or_create_customer(self, user_id: UUID, email: str, name: str) -> str:
        """Get existing Stripe customer or create a new one."""
        # Check if user already has a subscription with customer ID
        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()

        if subscription and subscription.stripe_customer_id:
            return subscription.stripe_customer_id

        # Create new customer
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"user_id": str(user_id), "platform": "getanswers"}
        )

        logger.info(f"Created Stripe customer {customer.id} for user {user_id}")
        return customer.id

    async def create_checkout_session(
        self,
        user_id: UUID,
        email: str,
        name: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        trial_days: int = 0,
    ) -> stripe.checkout.Session:
        """Create a Stripe checkout session for subscription."""
        customer_id = await self.get_or_create_customer(user_id, email, name)

        session_params = {
            "customer": customer_id,
            "mode": "subscription",
            "payment_method_types": ["card"],
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "user_id": str(user_id),
                "platform": "getanswers",
            },
        }

        if trial_days > 0:
            session_params["subscription_data"] = {
                "trial_period_days": trial_days,
            }

        session = stripe.checkout.Session.create(**session_params)
        logger.info(f"Created checkout session {session.id} for user {user_id}")
        return session

    async def create_billing_portal_session(
        self,
        user_id: UUID,
        return_url: str,
    ) -> Optional[stripe.billing_portal.Session]:
        """Create a Stripe billing portal session."""
        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()

        if not subscription or not subscription.stripe_customer_id:
            return None

        session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url=return_url,
        )

        logger.info(f"Created billing portal session for user {user_id}")
        return session

    async def get_subscription(self, user_id: UUID) -> Optional[Subscription]:
        """Get user's subscription."""
        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_or_update_subscription(
        self,
        user_id: UUID,
        stripe_customer_id: str,
        stripe_subscription_id: str,
        stripe_price_id: str,
        status: str,
        current_period_start: Optional[int] = None,
        current_period_end: Optional[int] = None,
        trial_start: Optional[int] = None,
        trial_end: Optional[int] = None,
    ) -> Subscription:
        """Create or update subscription from Stripe webhook data."""
        # Map price_id to plan (this would be configured in get-platform)
        plan = self._price_id_to_plan(stripe_price_id)

        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.stripe_customer_id = stripe_customer_id
            subscription.stripe_subscription_id = stripe_subscription_id
            subscription.stripe_price_id = stripe_price_id
            subscription.status = SubscriptionStatus(status) if status in SubscriptionStatus.__members__.values() else SubscriptionStatus.ACTIVE
            subscription.plan = plan
            if current_period_start:
                subscription.current_period_start = datetime.fromtimestamp(current_period_start, tz=timezone.utc)
            if current_period_end:
                subscription.current_period_end = datetime.fromtimestamp(current_period_end, tz=timezone.utc)
            if trial_start:
                subscription.trial_start = datetime.fromtimestamp(trial_start, tz=timezone.utc)
            if trial_end:
                subscription.trial_end = datetime.fromtimestamp(trial_end, tz=timezone.utc)
        else:
            subscription = Subscription(
                user_id=user_id,
                stripe_customer_id=stripe_customer_id,
                stripe_subscription_id=stripe_subscription_id,
                stripe_price_id=stripe_price_id,
                status=SubscriptionStatus(status) if status in SubscriptionStatus.__members__.values() else SubscriptionStatus.ACTIVE,
                plan=plan,
                current_period_start=datetime.fromtimestamp(current_period_start, tz=timezone.utc) if current_period_start else None,
                current_period_end=datetime.fromtimestamp(current_period_end, tz=timezone.utc) if current_period_end else None,
                trial_start=datetime.fromtimestamp(trial_start, tz=timezone.utc) if trial_start else None,
                trial_end=datetime.fromtimestamp(trial_end, tz=timezone.utc) if trial_end else None,
            )
            self.db.add(subscription)

        await self.db.commit()
        await self.db.refresh(subscription)

        logger.info(f"Updated subscription for user {user_id}: plan={plan}, status={status}")
        return subscription

    async def cancel_subscription(self, stripe_subscription_id: str) -> Optional[Subscription]:
        """Mark subscription as canceled."""
        result = await self.db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == stripe_subscription_id)
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.CANCELED
            subscription.canceled_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(subscription)
            logger.info(f"Canceled subscription {stripe_subscription_id}")

        return subscription

    def _price_id_to_plan(self, price_id: str) -> PlanTier:
        """Map Stripe price ID to plan tier.

        In production, this would be fetched from get-platform's price configuration.
        """
        # These would be configured via environment or get-platform
        price_mapping = {
            # Test mode
            "price_starter_test": PlanTier.STARTER,
            "price_pro_test": PlanTier.PRO,
            "price_enterprise_test": PlanTier.ENTERPRISE,
            # Live mode
            "price_starter_live": PlanTier.STARTER,
            "price_pro_live": PlanTier.PRO,
            "price_enterprise_live": PlanTier.ENTERPRISE,
        }

        return price_mapping.get(price_id, PlanTier.STARTER)
