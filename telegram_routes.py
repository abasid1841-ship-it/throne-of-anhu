"""Telegram integration routes for account linking."""

import os
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel

from database import get_db
from db_models import User, SocialLink, TelegramLinkCode
from auth import get_current_user

router = APIRouter(prefix="/api/telegram", tags=["telegram"])


def generate_link_code() -> str:
    """Generate a 6-character alphanumeric link code."""
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
    return ''.join(secrets.choice(chars) for _ in range(6))


class LinkCodeResponse(BaseModel):
    code: str
    expires_at: str
    expires_in_minutes: int = 10


class TelegramLinkRequest(BaseModel):
    telegram_user_id: str
    code: str


class TelegramLinkResponse(BaseModel):
    success: bool
    message: str
    user_email: Optional[str] = None
    subscription_tier: Optional[str] = None
    daily_limit: Optional[int] = None


@router.post("/generate-link-code", response_model=LinkCodeResponse)
async def generate_telegram_link_code(
    request: Request,
    db: Session = Depends(get_db),
):
    """Generate a link code for connecting Telegram to web account."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    
    existing_link = db.query(SocialLink).filter(
        and_(
            SocialLink.user_id == user.id,
            SocialLink.platform == "telegram",
            SocialLink.is_active == True
        )
    ).first()
    
    if existing_link:
        raise HTTPException(
            status_code=400,
            detail=f"Telegram already linked (ID: {existing_link.external_id}). Unlink first to connect a different account."
        )
    
    db.query(TelegramLinkCode).filter(
        and_(
            TelegramLinkCode.user_id == user.id,
            TelegramLinkCode.is_used == False
        )
    ).delete()
    db.commit()
    
    code = generate_link_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    link_code = TelegramLinkCode(
        user_id=user.id,
        code=code,
        expires_at=expires_at
    )
    db.add(link_code)
    db.commit()
    
    print(f"[TELEGRAM] Generated link code {code} for user {user.email}")
    
    return LinkCodeResponse(
        code=code,
        expires_at=expires_at.isoformat(),
        expires_in_minutes=10
    )


@router.post("/link", response_model=TelegramLinkResponse)
async def link_telegram_account(
    data: TelegramLinkRequest,
    db: Session = Depends(get_db),
):
    """Link a Telegram account using a code. Called from the Telegram bot."""
    code = data.code.upper().strip()
    telegram_user_id = data.telegram_user_id.strip()
    
    if not code or not telegram_user_id:
        return TelegramLinkResponse(
            success=False,
            message="Missing code or Telegram user ID"
        )
    
    link_code = db.query(TelegramLinkCode).filter(
        and_(
            TelegramLinkCode.code == code,
            TelegramLinkCode.is_used == False,
            TelegramLinkCode.expires_at > datetime.utcnow()
        )
    ).first()
    
    if not link_code:
        return TelegramLinkResponse(
            success=False,
            message="Invalid or expired code. Please generate a new one from the web app."
        )
    
    existing_link = db.query(SocialLink).filter(
        and_(
            SocialLink.platform == "telegram",
            SocialLink.external_id == telegram_user_id,
            SocialLink.is_active == True
        )
    ).first()
    
    if existing_link:
        if existing_link.user_id == link_code.user_id:
            return TelegramLinkResponse(
                success=False,
                message="This Telegram account is already linked to your web account."
            )
        else:
            return TelegramLinkResponse(
                success=False,
                message="This Telegram account is already linked to a different web account."
            )
    
    link_code.is_used = True
    link_code.used_at = datetime.utcnow()
    
    new_link = SocialLink(
        user_id=link_code.user_id,
        platform="telegram",
        external_id=telegram_user_id,
        linked_at=datetime.utcnow()
    )
    db.add(new_link)
    db.commit()
    
    user = db.query(User).filter(User.id == link_code.user_id).first()
    
    print(f"[TELEGRAM] Linked telegram:{telegram_user_id} to user {user.email if user else 'unknown'}")
    
    return TelegramLinkResponse(
        success=True,
        message="Successfully linked! Your Telegram now shares your web subscription limits.",
        user_email=user.email if user else None,
        subscription_tier=user.subscription_tier if user else "free",
        daily_limit=user.daily_limit if user else 3
    )


@router.delete("/unlink")
async def unlink_telegram(
    request: Request,
    db: Session = Depends(get_db),
):
    """Unlink Telegram account from web account."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    
    link = db.query(SocialLink).filter(
        and_(
            SocialLink.user_id == user.id,
            SocialLink.platform == "telegram",
            SocialLink.is_active == True
        )
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="No Telegram account linked")
    
    link.is_active = False
    db.commit()
    
    print(f"[TELEGRAM] Unlinked telegram:{link.external_id} from user {user.email}")
    
    return {"success": True, "message": "Telegram account unlinked"}


@router.get("/status")
async def get_telegram_link_status(
    request: Request,
    db: Session = Depends(get_db),
):
    """Get the current Telegram link status for the logged-in user."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    
    link = db.query(SocialLink).filter(
        and_(
            SocialLink.user_id == user.id,
            SocialLink.platform == "telegram",
            SocialLink.is_active == True
        )
    ).first()
    
    if link:
        return {
            "linked": True,
            "telegram_id": link.external_id,
            "linked_at": link.linked_at.isoformat() if link.linked_at else None,
            "last_seen": link.last_seen.isoformat() if link.last_seen else None
        }
    else:
        return {
            "linked": False,
            "telegram_id": None,
            "linked_at": None,
            "last_seen": None
        }


def resolve_telegram_to_user(telegram_user_id: str, db: Session) -> Optional[User]:
    """Resolve a Telegram user ID to a linked web user. Used by rate limiting."""
    link = db.query(SocialLink).filter(
        and_(
            SocialLink.platform == "telegram",
            SocialLink.external_id == telegram_user_id,
            SocialLink.is_active == True
        )
    ).first()
    
    if link:
        link.last_seen = datetime.utcnow()
        db.commit()
        return db.query(User).filter(User.id == link.user_id).first()
    
    return None
