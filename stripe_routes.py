"""Stripe routes for subscription management."""

import os
from fastapi import APIRouter, Request, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from db_models import User
from auth import get_optional_user
from stripe_client import get_stripe_client, get_stripe_publishable_key, get_stripe_secret_key
from subscription import SUBSCRIPTION_TIERS

router = APIRouter(prefix="/api/stripe", tags=["stripe"])

STRIPE_PREMIUM_PRICE_ID = os.environ.get("STRIPE_PREMIUM_PRICE_ID", "")
STRIPE_SEEKER_PRICE_ID = os.environ.get("STRIPE_SEEKER_PRICE_ID", "")

def get_tier_from_price_id(price_id: str) -> tuple:
    """Determine subscription tier and daily limit from Stripe price ID."""
    if STRIPE_PREMIUM_PRICE_ID and price_id == STRIPE_PREMIUM_PRICE_ID:
        return "premium", 60
    return "seeker", 25


class CheckoutRequest(BaseModel):
    price_id: str
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


@router.get("/config")
async def get_stripe_config():
    """Get Stripe publishable key for frontend."""
    try:
        publishable_key = await get_stripe_publishable_key()
        return {"publishable_key": publishable_key}
    except Exception as e:
        print(f"[STRIPE] Config error: {e}")
        return {"publishable_key": None, "error": "Stripe not configured"}


@router.post("/create-checkout-session")
async def create_checkout_session(
    req: CheckoutRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Create a Stripe checkout session for subscription."""
    user = get_optional_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Login required to subscribe")
    
    try:
        stripe_mod = await get_stripe_client()
        
        base_url = os.environ.get("PUBLIC_BASE_URL", str(request.base_url).rstrip("/"))
        success_url = req.success_url or f"{base_url}/?subscription=success"
        cancel_url = req.cancel_url or f"{base_url}/?subscription=cancelled"
        
        customer_id = user.stripe_customer_id
        if not customer_id:
            customer = stripe_mod.Customer.create(
                email=user.email or f"user_{user.id}@throne.anhu",
                metadata={"user_id": user.id},
            )
            customer_id = customer.id
            user.stripe_customer_id = customer_id
            db.commit()
        
        session = stripe_mod.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": req.price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": user.id},
        )
        
        return {"url": session.url, "session_id": session.id}
    
    except Exception as e:
        print(f"[STRIPE] Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-subscription")
async def sync_subscription(
    request: Request,
    db: Session = Depends(get_db),
):
    """Sync subscription status from Stripe for users who paid but webhook missed."""
    user = get_optional_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    
    try:
        stripe_mod = await get_stripe_client()
        customer_id = user.stripe_customer_id
        
        # Try stored customer_id first, then fall back to email search
        if not customer_id:
            customers = stripe_mod.Customer.search(
                query=f"email:'{user.email}'"
            )
            if customers.data:
                customer_id = customers.data[0].id
                user.stripe_customer_id = customer_id
        
        if customer_id:
            subscriptions = stripe_mod.Subscription.list(
                customer=customer_id,
                status="active",
                limit=1
            )
            
            if subscriptions.data:
                sub = subscriptions.data[0]
                user.stripe_subscription_id = sub.id
                user.is_subscriber = True
                # Get tier from subscription items
                items = sub.get("items", {}).get("data", [])
                price_id = items[0].get("price", {}).get("id", "") if items else ""
                tier, daily_limit = get_tier_from_price_id(price_id)
                user.subscription_tier = tier
                user.daily_limit = daily_limit
                db.commit()
                print(f"[STRIPE SYNC] User {user.id} synced to {tier} tier")
                return {"status": "synced", "tier": tier, "is_subscriber": True, "daily_limit": daily_limit}
        
        db.commit()
        return {"status": "no_subscription", "tier": user.subscription_tier}
    
    except Exception as e:
        print(f"[STRIPE SYNC] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-portal-session")
async def create_portal_session(
    request: Request,
    db: Session = Depends(get_db),
):
    """Create a Stripe billing portal session for managing subscription."""
    user = get_optional_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    
    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No active subscription found")
    
    try:
        stripe_mod = await get_stripe_client()
        base_url = str(request.base_url).rstrip("/")
        
        session = stripe_mod.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=base_url,
        )
        
        return {"url": session.url}
    
    except Exception as e:
        print(f"[STRIPE] Portal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db),
):
    """Handle Stripe webhook events."""
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        print("[STRIPE WEBHOOK] WARNING: STRIPE_WEBHOOK_SECRET not set. Webhook verification disabled.")
        raise HTTPException(status_code=500, detail="Webhook not configured")
    
    try:
        payload = await request.body()
        secret_key = await get_stripe_secret_key()
        
        import stripe
        stripe.api_key = secret_key
        
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
        
        event_type = event.type
        data = event.data.object
        
        print(f"[STRIPE WEBHOOK] Received event: {event_type}")
        
        if event_type == "checkout.session.completed":
            await handle_checkout_completed(data, db)
        elif event_type == "customer.subscription.created":
            await handle_subscription_created(data, db)
        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(data, db)
        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(data, db)
        elif event_type == "invoice.payment_succeeded":
            await handle_payment_succeeded(data, db)
        elif event_type == "invoice.payment_failed":
            await handle_payment_failed(data, db)
        
        return {"received": True}
    
    except Exception as e:
        print(f"[STRIPE WEBHOOK] Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


async def handle_checkout_completed(session: dict, db: Session):
    """Handle successful checkout."""
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    user_id = session.get("metadata", {}).get("user_id")
    
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.stripe_subscription_id = subscription_id
            user.is_subscriber = True
            
            # Determine tier from subscription items (stripe.api_key already set by webhook handler)
            try:
                import stripe
                sub = stripe.Subscription.retrieve(subscription_id)
                price_id = sub['items']['data'][0]['price']['id'] if sub.get('items', {}).get('data') else ""
                tier, daily_limit = get_tier_from_price_id(price_id)
                user.subscription_tier = tier
                user.daily_limit = daily_limit
            except Exception as e:
                print(f"[STRIPE] Could not determine tier from subscription: {e}")
                user.subscription_tier = "seeker"
                user.daily_limit = 25
            
            db.commit()
            print(f"[STRIPE] User {user_id} checkout completed, tier: {user.subscription_tier}")


async def handle_subscription_created(subscription: dict, db: Session):
    """Handle new subscription created."""
    customer_id = subscription.get("customer")
    subscription_id = subscription.get("id")
    status = subscription.get("status")
    
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        user.stripe_subscription_id = subscription_id
        if status == "active":
            user.is_subscriber = True
            # Get tier from subscription items
            items = subscription.get("items", {}).get("data", [])
            price_id = items[0].get("price", {}).get("id", "") if items else ""
            tier, daily_limit = get_tier_from_price_id(price_id)
            user.subscription_tier = tier
            user.daily_limit = daily_limit
        db.commit()
        print(f"[STRIPE] Subscription created for user {user.id}: tier={user.subscription_tier}")


async def handle_subscription_updated(subscription: dict, db: Session):
    """Handle subscription update."""
    customer_id = subscription.get("customer")
    subscription_id = subscription.get("id")
    status = subscription.get("status")
    
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        user.stripe_subscription_id = subscription_id
        if status == "active":
            user.is_subscriber = True
            # Get tier from subscription items
            items = subscription.get("items", {}).get("data", [])
            price_id = items[0].get("price", {}).get("id", "") if items else ""
            tier, daily_limit = get_tier_from_price_id(price_id)
            user.subscription_tier = tier
            user.daily_limit = daily_limit
        elif status in ("canceled", "unpaid", "past_due"):
            user.is_subscriber = False
            user.subscription_tier = "free"
            user.daily_limit = 3
        db.commit()
        print(f"[STRIPE] Subscription updated for user {user.id}: tier={user.subscription_tier}, status={status}")


async def handle_subscription_deleted(subscription: dict, db: Session):
    """Handle subscription cancellation."""
    customer_id = subscription.get("customer")
    
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        user.is_subscriber = False
        user.subscription_tier = "free"
        user.daily_limit = 3
        user.stripe_subscription_id = None
        db.commit()
        print(f"[STRIPE] Subscription deleted for user {user.id}, reset to free tier")


async def handle_payment_succeeded(invoice: dict, db: Session):
    """Handle successful payment."""
    customer_id = invoice.get("customer")
    subscription_id = invoice.get("subscription")
    
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user and subscription_id:
        user.is_subscriber = True
        # Get tier from invoice lines
        lines = invoice.get("lines", {}).get("data", [])
        price_id = lines[0].get("price", {}).get("id", "") if lines else ""
        tier, daily_limit = get_tier_from_price_id(price_id)
        user.subscription_tier = tier
        user.daily_limit = daily_limit
        db.commit()
        print(f"[STRIPE] Payment succeeded for user {user.id}, tier={tier}")


async def handle_payment_failed(invoice: dict, db: Session):
    """Handle failed payment."""
    customer_id = invoice.get("customer")
    
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        print(f"[STRIPE] Payment failed for user {user.id}")
