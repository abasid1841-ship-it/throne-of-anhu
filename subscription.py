"""Subscription tiers and rate limiting for Throne of Anhu."""

import os
from datetime import date
from typing import Dict, Tuple, Optional

from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Integer, Date
from database import Base

# ----------------------------
# STRIPE
# ----------------------------
STRIPE_SEEKER_PRICE_ID = os.environ.get("STRIPE_SEEKER_PRICE_ID", "")

# ----------------------------
# MANUAL ACCESS (YOU CONTROL)
# Replit Secrets:
# THRONE_MANUAL_EMAILS="a@b.com,c@d.com"
# THRONE_MANUAL_USER_IDS="uuid1,uuid2"
# ----------------------------
MANUAL_EMAILS = {
    x.strip().lower()
    for x in (os.environ.get("THRONE_MANUAL_EMAILS", "") or "").split(",")
    if x.strip()
}
MANUAL_USER_IDS = {
    x.strip()
    for x in (os.environ.get("THRONE_MANUAL_USER_IDS", "") or "").split(",")
    if x.strip()
}

ANON_DAILY_LIMIT = int(os.environ.get("THRONE_ANON_DAILY_LIMIT", "3"))
FREE_DAILY_LIMIT = int(os.environ.get("THRONE_FREE_DAILY_LIMIT", "3"))

# ----------------------------
# TIERS
# ----------------------------
SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Free",
        "price_usd": 0,
        "daily_limit": FREE_DAILY_LIMIT,
        "features": [
            f"{FREE_DAILY_LIMIT} questions per day",
            "Basic scroll access",
            "All three courts (RA, DZI, MA)",
        ],
    },
    "seeker": {
        "name": "Seeker",
        "price_usd": 10,
        "stripe_price_id": STRIPE_SEEKER_PRICE_ID,
        "daily_limit": 20,
        "features": [
            "20 questions per day",
            "Full scroll library access",
            "Chat history saved",
            "Priority response",
        ],
    },
    "premium": {
        "name": "Premium",
        "price_usd": 20,
        "stripe_price_id": os.environ.get("STRIPE_PREMIUM_PRICE_ID", ""),
        "daily_limit": 45,
        "features": [
            "45 questions per day",
            "Full scroll library access",
            "Chat history saved",
            "Priority response",
            "Extended communion time",
        ],
    },
    "manual": {
        "name": "Manual",
        "price_usd": 0,
        "daily_limit": 200,
        "features": [
            "Manual access granted by ABASID 1841",
            "Extended daily communion",
        ],
    },
    "unlimited": {
        "name": "Unlimited",
        "price_usd": 0,
        "daily_limit": 10_000_000,
        "features": ["Unlimited communion"],
    },
    "admin": {
        "name": "Admin",
        "price_usd": 0,
        "daily_limit": 10_000_000,
        "features": [
            "Unlimited questions",
            "Full admin access",
            "Gallery upload rights",
            "Masowe Fellowship controls",
            "All premium features",
        ],
    },
}


class DailyUsage(Base):
    """Track daily usage per user for rate limiting."""
    __tablename__ = "daily_usage"

    user_id = Column(String, primary_key=True)
    usage_date = Column(Date, primary_key=True)
    question_count = Column(Integer, default=0)


def _is_manual_user(user) -> bool:
    if not user:
        return False
    uid = str(getattr(user, "id", "") or "")
    email = (getattr(user, "email", "") or "").strip().lower()
    return (uid and uid in MANUAL_USER_IDS) or (email and email in MANUAL_EMAILS)


def get_user_tier(user) -> dict:
    """Get the subscription tier for a user."""
    # Anonymous tier object (not in SUBSCRIPTION_TIERS)
    if not user:
        return {
            "name": "Anonymous",
            "daily_limit": ANON_DAILY_LIMIT,
            "features": [f"{ANON_DAILY_LIMIT} questions per day"],
        }

    # Manual overrides everything
    if _is_manual_user(user):
        tier = dict(SUBSCRIPTION_TIERS["manual"])
    else:
        tier_key = (getattr(user, "subscription_tier", None) or "free").strip().lower()
        tier = dict(SUBSCRIPTION_TIERS.get(tier_key, SUBSCRIPTION_TIERS["free"]))

    # DB custom daily limit overrides tier (if present)
    try:
        custom = int(getattr(user, "daily_limit", 0) or 0)
        if custom > 0:
            tier["daily_limit"] = custom
    except Exception:
        pass

    return tier


def get_daily_limit(user) -> int:
    return int(get_user_tier(user).get("daily_limit", FREE_DAILY_LIMIT))


# Memory fallback if DB fails
_memory_rate_limits: Dict[str, Dict] = {}


def _limit_message(user_id: str, daily_limit: int) -> str:
    is_whatsapp = user_id.startswith("whatsapp_") if user_id else False
    is_anonymous = user_id == "anonymous" or user_id.startswith("anon_") or user_id.startswith("telegram_") or is_whatsapp

    if is_whatsapp:
        base_url = os.environ.get("PUBLIC_BASE_URL", "https://www.thecollegeofanhu.com")
        return (
            "☀️ *The cup has run over for today.*\n\n"
            f"You have reached your {ANON_DAILY_LIMIT} free questions.\n\n"
            "*To continue seeking wisdom:*\n"
            f"👉 Visit: {base_url}\n\n"
            "Subscribe there, then type *LINK* here to connect your account and unlock:\n"
            "• *Seeker* ($10/mo): 20 questions/day\n"
            "• *Premium* ($20/mo): 45 questions/day\n\n"
            f"Return tomorrow for {ANON_DAILY_LIMIT} more free questions. ☀️"
        )
    if is_anonymous:
        return (
            "🦁 The cup has run over for today.\n\n"
            f"You have reached your {ANON_DAILY_LIMIT} free questions for today.\n\n"
            "Log in and subscribe to receive more communion:\n"
            "• Seeker ($10/month): 20 questions daily\n"
            "• Premium ($20/month): 45 questions daily\n\n"
            "👉 Click 'Login' to begin your journey."
        )
    if daily_limit <= FREE_DAILY_LIMIT:
        return (
            "🦁 The cup has run over for today.\n\n"
            "You have reached your daily portion.\n\n"
            "Become a Seeker — $10/month for 20 questions daily."
        )
    return (
        "🦁 The cup has run over for today.\n\n"
        "Return when the sun rises anew.\n\n"
        "Peace until the morrow."
    )


def _resolve_linked_user(user_id: str, db: Session):
    """Resolve Telegram/WhatsApp user to linked web account if exists."""
    if not db:
        return None, None
    
    platform = None
    external_id = None
    
    if user_id.startswith("telegram_"):
        platform = "telegram"
        external_id = user_id.replace("telegram_", "")
    elif user_id.startswith("whatsapp_"):
        platform = "whatsapp"
        external_id = user_id.replace("whatsapp_", "")
    
    if not platform:
        return None, None
    
    try:
        from db_models import SocialLink, User
        from sqlalchemy import and_
        
        link = db.query(SocialLink).filter(
            and_(
                SocialLink.platform == platform,
                SocialLink.external_id == external_id,
                SocialLink.is_active == True
            )
        ).first()
        
        if link:
            from datetime import datetime as dt
            link.last_seen = dt.utcnow()
            user = db.query(User).filter(User.id == link.user_id).first()
            if user:
                print(f"[RATE LIMIT] Resolved {platform}:{external_id} -> {user.email}")
                return user.id, user
        
        db.commit()
    except Exception as e:
        print(f"[RATE LIMIT] Error resolving linked user: {e}")
        try:
            db.rollback()
        except:
            pass
    
    return None, None


def check_rate_limit(user_id: Optional[str], db: Session = None) -> Tuple[bool, int, str]:
    """
    Returns: (allowed, remaining, message)
    """
    import os as _os

    # Admin WhatsApp/Telegram numbers get unlimited access
    if user_id and user_id.startswith("whatsapp_"):
        _phone = user_id[len("whatsapp_"):]
        _admin_nums = [n.strip() for n in _os.environ.get("ADMIN_WA_NUMBERS", "").split(",") if n.strip()]
        if _phone in _admin_nums or f"+{_phone}" in _admin_nums:
            return True, 9999, ""

    today = date.today()
    today_str = today.isoformat()
    
    original_user_id = user_id
    resolved_user = None

    # Check if Telegram/WhatsApp user is linked to a web account
    if db and user_id and (user_id.startswith("telegram_") or user_id.startswith("whatsapp_")):
        resolved_id, resolved_user = _resolve_linked_user(user_id, db)
        if resolved_id:
            user_id = resolved_id

    # Anonymous (anon_*), unlinked Telegram/WhatsApp - all get ANON_DAILY_LIMIT (3)
    is_anonymous = not user_id or user_id.startswith("anon_") or user_id.startswith("telegram_") or user_id.startswith("whatsapp_")
    
    if not user_id:
        user_id = "anonymous"
        daily_limit = ANON_DAILY_LIMIT
    elif is_anonymous:
        daily_limit = ANON_DAILY_LIMIT
    else:
        daily_limit = FREE_DAILY_LIMIT

    # Use persistent database tracking for anonymous users (survives server restarts)
    if db and is_anonymous and user_id.startswith("anon_"):
        try:
            from security import check_anonymous_rate_limit
            ip_address = user_id.replace("anon_", "")
            return check_anonymous_rate_limit(ip_address, db)
        except Exception as e:
            print(f"[RATE LIMIT] Persistent anon check failed, fallback to memory: {e}")

    # DB path (for logged-in web users only - not anonymous)
    if db and not is_anonymous:
        try:
            from db_models import User
            from datetime import datetime as dt
            user = db.query(User).filter(User.id == user_id).first()
            
            # Check if user is suspended
            if user and getattr(user, 'is_suspended', False):
                return False, 0, "🦁 Your access has been suspended. Please contact support."
            
            # Check if admin-granted access has expired
            access_expires = getattr(user, 'access_expires_at', None)
            if user and access_expires and access_expires < dt.utcnow():
                # Access expired - downgrade to free
                user.is_subscriber = False
                user.subscription_tier = "free"
                user.daily_limit = FREE_DAILY_LIMIT
                try:
                    db.commit()
                except:
                    db.rollback()
            
            daily_limit = get_daily_limit(user)

            usage = db.query(DailyUsage).filter(
                DailyUsage.user_id == user_id,
                DailyUsage.usage_date == today
            ).first()

            current = int(usage.question_count or 0) if usage else 0

            if current >= daily_limit:
                return False, 0, _limit_message(user_id, daily_limit)

            remaining = max(0, daily_limit - current - 1)
            return True, remaining, ""
        except Exception as e:
            print(f"[RATE LIMIT] DB error, fallback to memory: {e}")
            try:
                db.rollback()
            except Exception:
                pass

    # Memory fallback
    info = _memory_rate_limits.get(user_id)
    if not info or info.get("date") != today_str:
        info = {"date": today_str, "count": 0}
        _memory_rate_limits[user_id] = info

    if info["count"] >= daily_limit:
        return False, 0, _limit_message(user_id, daily_limit)

    remaining = max(0, daily_limit - info["count"] - 1)
    return True, remaining, ""


def increment_usage(user_id: Optional[str], db: Session = None) -> None:
    today = date.today()
    today_str = today.isoformat()

    if not user_id:
        user_id = "anonymous"

    # Check if Telegram/WhatsApp user is linked to a web account
    if db and user_id and (user_id.startswith("telegram_") or user_id.startswith("whatsapp_")):
        resolved_id, resolved_user = _resolve_linked_user(user_id, db)
        if resolved_id:
            user_id = resolved_id

    is_anonymous = user_id == "anonymous" or user_id.startswith("anon_") or user_id.startswith("telegram_") or user_id.startswith("whatsapp_")

    # Use persistent database tracking for anonymous users (survives server restarts)
    if db and is_anonymous and user_id.startswith("anon_"):
        try:
            from security import increment_anonymous_usage
            ip_address = user_id.replace("anon_", "")
            increment_anonymous_usage(ip_address, db)
            return
        except Exception as e:
            print(f"[RATE LIMIT] Persistent anon increment failed, fallback to memory: {e}")

    if db and not is_anonymous:
        try:
            usage = db.query(DailyUsage).filter(
                DailyUsage.user_id == user_id,
                DailyUsage.usage_date == today
            ).first()

            if not usage:
                usage = DailyUsage(user_id=user_id, usage_date=today, question_count=1)
                db.add(usage)
            else:
                usage.question_count = int(usage.question_count or 0) + 1

            db.commit()
            return
        except Exception as e:
            print(f"[RATE LIMIT] DB increment error: {e}")
            try:
                db.rollback()
            except Exception:
                pass

    info = _memory_rate_limits.get(user_id)
    if not info or info.get("date") != today_str:
        info = {"date": today_str, "count": 0}
        _memory_rate_limits[user_id] = info
    info["count"] += 1


def get_usage_stats(user_id: Optional[str], db: Session = None) -> dict:
    today = date.today()
    today_str = today.isoformat()

    uid = user_id or "anonymous"
    count = 0

    is_anonymous = uid == "anonymous" or uid.startswith("anon_") or uid.startswith("telegram_") or uid.startswith("whatsapp_")

    if is_anonymous:
        limit = ANON_DAILY_LIMIT
    else:
        limit = FREE_DAILY_LIMIT

    if db and not is_anonymous:
        try:
            from db_models import User
            user = db.query(User).filter(User.id == uid).first()
            limit = get_daily_limit(user)

            usage = db.query(DailyUsage).filter(
                DailyUsage.user_id == uid,
                DailyUsage.usage_date == today
            ).first()
            count = int(usage.question_count or 0) if usage else 0
        except Exception as e:
            print(f"[RATE LIMIT] DB stats error, fallback: {e}")
            try:
                db.rollback()
            except Exception:
                pass

    # Use persistent database tracking for anonymous users
    if is_anonymous and uid.startswith("anon_") and db:
        try:
            from security import get_anonymous_usage_stats
            ip_address = uid.replace("anon_", "")
            return get_anonymous_usage_stats(ip_address, db)
        except Exception as e:
            print(f"[RATE LIMIT] Persistent anon stats failed, fallback: {e}")

    if is_anonymous or not db:
        info = _memory_rate_limits.get(uid)
        if info and info.get("date") == today_str:
            count = int(info.get("count", 0))

    return {
        "today": int(count),
        "limit": int(limit),
        "remaining": max(0, int(limit) - int(count)),
    }