"""Seed script to create Stripe products and prices."""

import asyncio
import stripe
from stripe_client import get_credentials


async def create_products():
    """Create the Seeker subscription product in Stripe."""
    credentials = await get_credentials()
    stripe.api_key = credentials["secret_key"]
    
    existing = stripe.Product.search(query="name:'Seeker Subscription'")
    if existing.data:
        print(f"Product already exists: {existing.data[0].id}")
        prices = stripe.Price.list(product=existing.data[0].id, active=True)
        if prices.data:
            print(f"Price ID: {prices.data[0].id}")
            print("Use this price ID in your subscription.py SUBSCRIPTION_TIERS")
        return
    
    product = stripe.Product.create(
        name="Seeker Subscription",
        description="20 questions per day, full scroll library access, chat history saved",
        metadata={
            "tier": "seeker",
            "daily_limit": "100",
        },
    )
    print(f"Created product: {product.id}")
    
    price = stripe.Price.create(
        product=product.id,
        unit_amount=1000,
        currency="usd",
        recurring={"interval": "month"},
        metadata={
            "tier": "seeker",
        },
    )
    print(f"Created price: {price.id}")
    print(f"\nUpdate SUBSCRIPTION_TIERS['seeker']['stripe_price_id'] to: {price.id}")


if __name__ == "__main__":
    asyncio.run(create_products())
