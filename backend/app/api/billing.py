"""Billing and subscription API endpoints."""
import json
import hashlib
import hmac
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger
from app.api.deps import get_current_user
from app.models import User, Subscription, PlanTier, SubscriptionStatus, FeatureName
from app.services.stripe import StripeService, get_publishable_key, invalidate_stripe_mode_cache, get_stripe_mode
from app.services.features import FeatureService

router = APIRouter()


# Request/Response Models
class CreateCheckoutRequest(BaseModel):
    """Request to create a checkout session."""
    price_id: str = Field(..., description="Stripe price ID")
    success_url: str = Field(..., description="URL to redirect on success")
    cancel_url: str = Field(..., description="URL to redirect on cancel")


class CheckoutResponse(BaseModel):
    """Checkout session response."""
    checkout_url: str
    session_id: str


class BillingPortalResponse(BaseModel):
    """Billing portal session response."""
    portal_url: str


class SubscriptionResponse(BaseModel):
    """Subscription details response."""
    plan: str
    status: str
    is_active: bool
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    stripe_mode: str


class FeaturesResponse(BaseModel):
    """User features response."""
    features: dict[str, bool]
    plan: str


class ConfigResponse(BaseModel):
    """Stripe configuration response."""
    publishable_key: str
    mode: str


# Endpoints
@router.get("/config", response_model=ConfigResponse)
async def get_stripe_config():
    """Get Stripe configuration for the frontend."""
    return ConfigResponse(
        publishable_key=get_publishable_key(),
        mode=get_stripe_mode(),
    )


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's subscription details."""
    service = StripeService(db)
    subscription = await service.get_subscription(current_user.id)

    if not subscription:
        return SubscriptionResponse(
            plan=PlanTier.FREE.value,
            status="active",
            is_active=True,
            current_period_end=None,
            cancel_at_period_end=False,
            stripe_mode=get_stripe_mode(),
        )

    return SubscriptionResponse(
        plan=subscription.plan.value,
        status=subscription.status.value,
        is_active=subscription.is_active,
        current_period_end=subscription.current_period_end,
        cancel_at_period_end=subscription.cancel_at_period_end,
        stripe_mode=get_stripe_mode(),
    )


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CreateCheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe checkout session for subscription."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured",
        )

    service = StripeService(db)
    try:
        session = await service.create_checkout_session(
            user_id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            price_id=request.price_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            trial_days=14,  # 14-day trial for new subscribers
        )

        return CheckoutResponse(
            checkout_url=session.url,
            session_id=session.id,
        )
    except stripe.StripeError as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/portal", response_model=BillingPortalResponse)
async def create_billing_portal(
    return_url: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe billing portal session."""
    service = StripeService(db)
    session = await service.create_billing_portal_session(
        user_id=current_user.id,
        return_url=return_url,
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found",
        )

    return BillingPortalResponse(portal_url=session.url)


@router.get("/features", response_model=FeaturesResponse)
async def get_features(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all feature flags for the current user."""
    feature_service = FeatureService(db)
    stripe_service = StripeService(db)

    features = await feature_service.get_all_features(current_user.id)
    subscription = await stripe_service.get_subscription(current_user.id)

    plan = subscription.plan.value if subscription else PlanTier.FREE.value

    return FeaturesResponse(
        features=features,
        plan=plan,
    )


@router.get("/features/{feature_name}")
async def check_feature(
    feature_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if a specific feature is enabled for the current user."""
    try:
        feature = FeatureName(feature_name)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown feature: {feature_name}",
        )

    service = FeatureService(db)
    enabled = await service.is_feature_enabled(current_user.id, feature)

    return {"feature": feature_name, "enabled": enabled}


# Webhook Endpoints
@router.post("/webhooks/stripe")
async def handle_stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhook events."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe webhook secret not configured",
        )

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid Stripe webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.SignatureVerificationError as e:
        logger.error(f"Invalid Stripe webhook signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    service = StripeService(db)
    event_type = event["type"]
    event_data = event["data"]["object"]

    try:
        if event_type == "checkout.session.completed":
            await handle_checkout_completed(event_data, service)
        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(event_data, service)
        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(event_data, service)
        elif event_type == "invoice.payment_succeeded":
            await handle_invoice_paid(event_data, service)
        elif event_type == "invoice.payment_failed":
            await handle_invoice_failed(event_data, service)
        else:
            logger.debug(f"Unhandled Stripe event: {event_type}")

    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

    return {"received": True}


@router.post("/webhooks/stripe-mode")
async def handle_stripe_mode_webhook(request: Request):
    """Handle stripe mode change webhook from get-platform."""
    body = await request.body()
    signature = request.headers.get("x-webhook-signature")
    timestamp = request.headers.get("x-webhook-timestamp")

    # Verify webhook secret if configured
    webhook_secret = settings.GET_PLATFORM_WEBHOOK_SECRET
    if webhook_secret and signature and timestamp:
        # Verify signature: HMAC-SHA256(timestamp + "." + body)
        expected_signature = hmac.new(
            webhook_secret.encode(),
            f"{timestamp}.{body.decode()}".encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            logger.error("stripe_mode_webhook_invalid_signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

        # Check timestamp is within 5 minutes
        try:
            timestamp_ms = int(timestamp)
            current_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
            if abs(current_ms - timestamp_ms) > 300000:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Webhook timestamp expired",
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid timestamp format",
            )
    elif not webhook_secret:
        logger.warning("GET_PLATFORM_WEBHOOK_SECRET not configured")

    try:
        payload = json.loads(body)

        if payload.get("event") == "stripe_mode_changed":
            invalidate_stripe_mode_cache()
            logger.info(f"Stripe mode cache invalidated, new mode: {payload.get('mode')}")

        return {"status": "success"}

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in stripe-mode webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )


# Webhook Handlers
async def handle_checkout_completed(session_data: dict, service: StripeService):
    """Handle checkout.session.completed event."""
    metadata = session_data.get("metadata", {})
    user_id = metadata.get("user_id")

    if not user_id:
        logger.warning(f"Checkout completed without user_id: {session_data['id']}")
        return

    subscription_id = session_data.get("subscription")
    customer_id = session_data.get("customer")

    if subscription_id and customer_id:
        # Fetch full subscription details from Stripe
        subscription = stripe.Subscription.retrieve(subscription_id)

        await service.create_or_update_subscription(
            user_id=UUID(user_id),
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            stripe_price_id=subscription["items"]["data"][0]["price"]["id"],
            status=subscription["status"],
            current_period_start=subscription.get("current_period_start"),
            current_period_end=subscription.get("current_period_end"),
            trial_start=subscription.get("trial_start"),
            trial_end=subscription.get("trial_end"),
        )

        logger.info(f"Subscription created for user {user_id}")


async def handle_subscription_updated(subscription_data: dict, service: StripeService):
    """Handle customer.subscription.updated event."""
    subscription_id = subscription_data["id"]
    customer_id = subscription_data["customer"]
    price_id = subscription_data["items"]["data"][0]["price"]["id"]

    # Find user by subscription ID
    from sqlalchemy import select
    result = await service.db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        await service.create_or_update_subscription(
            user_id=existing.user_id,
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            stripe_price_id=price_id,
            status=subscription_data["status"],
            current_period_start=subscription_data.get("current_period_start"),
            current_period_end=subscription_data.get("current_period_end"),
        )

        logger.info(f"Subscription updated: {subscription_id}")


async def handle_subscription_deleted(subscription_data: dict, service: StripeService):
    """Handle customer.subscription.deleted event."""
    subscription_id = subscription_data["id"]
    await service.cancel_subscription(subscription_id)
    logger.info(f"Subscription canceled: {subscription_id}")


async def handle_invoice_paid(invoice_data: dict, service: StripeService):
    """Handle invoice.payment_succeeded event."""
    subscription_id = invoice_data.get("subscription")
    if subscription_id:
        logger.info(f"Invoice paid for subscription: {subscription_id}")


async def handle_invoice_failed(invoice_data: dict, service: StripeService):
    """Handle invoice.payment_failed event."""
    subscription_id = invoice_data.get("subscription")
    if subscription_id:
        from sqlalchemy import select
        result = await service.db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.status = SubscriptionStatus.PAST_DUE
            await service.db.commit()
            logger.warning(f"Invoice failed, subscription past_due: {subscription_id}")
