"""
Admin routes for RUSHANGA panel - subscription and user management.
Only accessible to admin users (abasid1841@gmail.com, sydneymusiyiwa221@gmail.com).
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_db
from auth import get_optional_user
from usage_tracker import get_user_usage, get_all_users_usage, get_total_usage
from db_models import User

router = APIRouter(prefix="/api/admin", tags=["admin"])

ADMIN_EMAILS = ["sydneymusiyiwa221@gmail.com", "abasid1841@gmail.com"]
ADMIN_IDS = ["39546572", "abasid1841"]

def require_admin(request: Request, db: Session = Depends(get_db)):
    """Check if current user is an admin."""
    from auth import get_optional_user
    user = get_optional_user(request, db)
    
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    
    user_email_lower = (user.email or "").lower()
    is_admin = (
        str(user.id) in ADMIN_IDS or
        user_email_lower in [e.lower() for e in ADMIN_EMAILS] or
        getattr(user, 'is_admin', False)
    )
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user


class GrantAccessRequest(BaseModel):
    email: str
    duration: str  # "1_week", "1_month", "1_year", "unlimited"
    note: Optional[str] = None


class UpdateSubscriberRequest(BaseModel):
    email: str
    action: str  # "suspend", "unsuspend", "remove", "set_tier"
    tier: Optional[str] = None
    daily_limit: Optional[int] = None


@router.get("/usage/total")
async def admin_total_usage(
    days: int = 30,
    user = Depends(require_admin)
):
    """Get total platform usage statistics."""
    return get_total_usage(days)

@router.get("/usage/users")
async def admin_all_users_usage(
    days: int = 30,
    user = Depends(require_admin)
):
    """Get usage breakdown by user."""
    users = get_all_users_usage(days)
    total = get_total_usage(days)
    return {
        "period_days": days,
        "summary": total,
        "users": users
    }

@router.get("/usage/user/{user_id}")
async def admin_user_usage(
    user_id: str,
    days: int = 30,
    user = Depends(require_admin)
):
    """Get detailed usage for a specific user."""
    return get_user_usage(user_id, days)

@router.get("/health")
async def admin_health(user = Depends(require_admin)):
    """Admin health check - confirms admin access works."""
    return {"status": "ok", "admin": True}


@router.get("/subscribers")
async def get_all_subscribers(
    db: Session = Depends(get_db),
    user = Depends(require_admin)
):
    """Get all subscribers for RUSHANGA panel."""
    users = db.query(User).all()
    
    # Calculate stats
    today = datetime.utcnow().date()
    total_subscribers = len(users)
    new_today = sum(1 for u in users if u.created_at and u.created_at.date() == today)
    active_paid = sum(1 for u in users if u.is_subscriber and u.subscription_tier in ["seeker", "premium"])
    
    subscribers = []
    for u in users:
        is_admin_user = (u.email or "").lower() in [e.lower() for e in ADMIN_EMAILS]
        
        # Check if access has expired
        access_status = "active"
        if u.is_suspended:
            access_status = "suspended"
        elif u.access_expires_at and u.access_expires_at < datetime.utcnow():
            access_status = "expired"
        elif not u.is_subscriber and u.subscription_tier == "free":
            access_status = "free"
        
        subscribers.append({
            "id": u.id,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "profile_image_url": u.profile_image_url,
            "subscription_tier": "admin" if is_admin_user else u.subscription_tier,
            "is_subscriber": True if is_admin_user else u.is_subscriber,
            "daily_limit": u.daily_limit,
            "is_admin": is_admin_user,
            "access_expires_at": u.access_expires_at.isoformat() if u.access_expires_at else None,
            "access_granted_by": u.access_granted_by,
            "access_note": u.access_note,
            "is_suspended": u.is_suspended,
            "access_status": access_status,
            "stripe_customer_id": u.stripe_customer_id,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })
    
    return {
        "subscribers": subscribers,
        "stats": {
            "total": total_subscribers,
            "new_today": new_today,
            "active_paid": active_paid,
        }
    }


@router.post("/grant-access")
async def grant_access(
    request: GrantAccessRequest,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    """Grant time-limited access to a user by email."""
    email_input = request.email.strip()
    
    # Find user with case-insensitive comparison (preserve original casing)
    from sqlalchemy import func
    user = db.query(User).filter(func.lower(User.email) == email_input.lower()).first()
    
    if not user:
        # Create new user with this email (preserve original casing)
        import uuid
        user = User(
            id=str(uuid.uuid4()),
            email=email_input,  # Keep original email casing
            subscription_tier="seeker",
            is_subscriber=True,
            daily_limit=20,
        )
        db.add(user)
    
    # Calculate expiration
    now = datetime.utcnow()
    if request.duration == "1_week":
        expires_at = now + timedelta(weeks=1)
        duration_text = "1 week"
    elif request.duration == "1_month":
        expires_at = now + timedelta(days=30)
        duration_text = "1 month"
    elif request.duration == "1_year":
        expires_at = now + timedelta(days=365)
        duration_text = "1 year"
    else:  # unlimited
        expires_at = None
        duration_text = "unlimited"
    
    # Update user
    user.subscription_tier = "seeker"
    user.is_subscriber = True
    user.daily_limit = 20
    user.access_expires_at = expires_at
    user.access_granted_by = admin.email
    user.access_note = request.note or f"Access granted by {admin.email}"
    user.is_suspended = False
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Granted {duration_text} access to {user.email}",
        "user": {
            "id": user.id,
            "email": user.email,
            "subscription_tier": user.subscription_tier,
            "access_expires_at": user.access_expires_at.isoformat() if user.access_expires_at else None,
        }
    }


@router.post("/update-subscriber")
async def update_subscriber(
    request: UpdateSubscriberRequest,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    """Update subscriber status (suspend, unsuspend, remove, set tier)."""
    email_input = request.email.strip()
    from sqlalchemy import func
    user = db.query(User).filter(func.lower(User.email) == email_input.lower()).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent modifying other admins
    if (user.email or "").lower() in [e.lower() for e in ADMIN_EMAILS]:
        raise HTTPException(status_code=403, detail="Cannot modify admin accounts")
    
    if request.action == "suspend":
        user.is_suspended = True
        message = f"Suspended {user.email}"
    
    elif request.action == "unsuspend":
        user.is_suspended = False
        message = f"Unsuspended {user.email}"
    
    elif request.action == "remove":
        user.is_subscriber = False
        user.subscription_tier = "free"
        user.daily_limit = 3
        user.access_expires_at = None
        user.access_granted_by = None
        user.access_note = None
        message = f"Removed subscription from {user.email}"
    
    elif request.action == "set_tier":
        if request.tier:
            user.subscription_tier = request.tier
        if request.daily_limit is not None:
            user.daily_limit = request.daily_limit
        if request.tier in ["seeker", "manual", "unlimited"]:
            user.is_subscriber = True
        message = f"Updated {user.email} to tier {request.tier}"
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
    
    db.commit()
    
    return {"success": True, "message": message}


@router.get("/check-expired")
async def check_expired_access(
    db: Session = Depends(get_db),
    user = Depends(require_admin)
):
    """Check and update expired access."""
    now = datetime.utcnow()
    
    expired_users = db.query(User).filter(
        User.access_expires_at != None,
        User.access_expires_at < now,
        User.is_subscriber == True
    ).all()
    
    expired_list = []
    for u in expired_users:
        u.is_subscriber = False
        u.subscription_tier = "free"
        u.daily_limit = 3
        expired_list.append(u.email)
    
    db.commit()
    
    return {
        "expired_count": len(expired_list),
        "expired_users": expired_list
    }
