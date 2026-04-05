"""Stripe client for Throne of Anhu - uses environment secrets for live keys."""

import os
from typing import Optional
import stripe


async def get_credentials() -> dict:
    """Get Stripe credentials from environment secrets."""
    publishable = os.environ.get("STRIPE_PUBLISHABLE_KEY")
    secret = os.environ.get("STRIPE_SECRET_KEY")
    
    if not publishable or not secret:
        raise ValueError("Stripe keys not configured. Please set STRIPE_PUBLISHABLE_KEY and STRIPE_SECRET_KEY secrets.")
    
    return {
        "publishable_key": publishable,
        "secret_key": secret,
    }


async def get_stripe_client():
    """Get a configured Stripe client."""
    credentials = await get_credentials()
    stripe.api_key = credentials["secret_key"]
    return stripe


async def get_stripe_publishable_key() -> str:
    """Get the Stripe publishable key for frontend use."""
    credentials = await get_credentials()
    return credentials["publishable_key"]


async def get_stripe_secret_key() -> str:
    """Get the Stripe secret key for backend operations."""
    credentials = await get_credentials()
    return credentials["secret_key"]
