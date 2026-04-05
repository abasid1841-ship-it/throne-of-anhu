"""SQLAlchemy models for users, chat history, and Wisdom Cards."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, Integer
from sqlalchemy.orm import relationship

from database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    """User account from Replit Auth."""
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)

    is_subscriber = Column(Boolean, default=False)
    subscription_tier = Column(String, default="free")
    daily_limit = Column(Integer, default=3)  # Free tier default

    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)

    # Admin-granted access
    access_expires_at = Column(DateTime, nullable=True)
    access_granted_by = Column(String, nullable=True)
    access_note = Column(String, nullable=True)
    is_suspended = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    threads = relationship("ChatThread", back_populates="user", cascade="all, delete-orphan")


class ChatThread(Base):
    """A conversation thread."""
    __tablename__ = "chat_threads"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    title = Column(String, default="New Chat")
    persona = Column(String, default="RA")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="threads")
    messages = relationship(
        "ChatMessage",
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    """A single message in a chat thread."""
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    thread_id = Column(String, ForeignKey("chat_threads.id"), nullable=False)

    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    persona = Column(String, default="RA")
    mode = Column(String, default="outer_court")

    created_at = Column(DateTime, default=datetime.utcnow)

    thread = relationship("ChatThread", back_populates="messages")


class WisdomCard(Base):
    """
    DB-backed instant answers (“Wisdom Cards”).
    Evaluated BEFORE local storehouse and BEFORE the engine.
    """
    __tablename__ = "wisdom_cards"

    id = Column(String, primary_key=True, default=generate_uuid)

    title = Column(String, nullable=False, default="Untitled")
    language = Column(String, nullable=False, default="ENGLISH")  # ENGLISH/SHONA/etc

    # JSON string: ["regex1", "regex2", ...]
    patterns_json = Column(Text, nullable=False, default="[]")

    answer = Column(Text, nullable=False)

    persona = Column(String, nullable=False, default="RA")
    mode = Column(String, nullable=False, default="outer_court")

    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=100)  # lower = matched earlier

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GalleryItem(Base):
    """Media items in the Sacred Gallery (videos, music, images)."""
    __tablename__ = "gallery_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    item_type = Column(String, nullable=False)  # video, music, image
    file_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    
    duration = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    
    is_downloadable = Column(Boolean, default=True)
    subscribers_only = Column(Boolean, default=False)
    
    category = Column(String, nullable=True)
    tags = Column(Text, nullable=True)
    
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FellowshipThread(Base):
    """Discussion threads in the Fellowship Hall."""
    __tablename__ = "fellowship_threads"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    
    category = Column(String, nullable=True)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    
    reply_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")
    replies = relationship("FellowshipReply", back_populates="thread", cascade="all, delete-orphan")


class FellowshipReply(Base):
    """Replies to discussion threads."""
    __tablename__ = "fellowship_replies"

    id = Column(String, primary_key=True, default=generate_uuid)
    thread_id = Column(String, ForeignKey("fellowship_threads.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    
    like_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    thread = relationship("FellowshipThread", back_populates="replies")
    user = relationship("User")


class MasoweChatMessage(Base):
    """Live chat messages in Masowe Fellowship."""
    __tablename__ = "masowe_chat_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=True)
    message_type = Column(String, default="text")  # text, voice, system
    voice_url = Column(String, nullable=True)
    voice_duration = Column(Integer, nullable=True)
    
    is_from_panel = Column(Boolean, default=False)
    is_announcement = Column(Boolean, default=False)
    
    reply_to_id = Column(String, nullable=True)
    reply_to_author = Column(String, nullable=True)
    reply_to_preview = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")


class MasoweUserRole(Base):
    """User roles and status in Masowe Fellowship."""
    __tablename__ = "masowe_user_roles"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    
    role = Column(String, default="member")  # admin, panel, member
    is_muted = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    
    muted_at = Column(DateTime, nullable=True)
    muted_by = Column(String, nullable=True)
    blocked_at = Column(DateTime, nullable=True)
    blocked_by = Column(String, nullable=True)
    
    panel_position = Column(Integer, nullable=True)  # 1-12 for panel members
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")


class MasoweSettings(Base):
    """Global settings for Masowe Fellowship."""
    __tablename__ = "masowe_settings"

    id = Column(String, primary_key=True, default="global")
    
    service_mode = Column(Boolean, default=False)
    service_started_at = Column(DateTime, nullable=True)
    
    welcome_message = Column(Text, default="Welcome to Masowe Fellowship! Peace be unto you.")
    tiktok_live_url = Column(String, nullable=True)
    
    global_mute = Column(Boolean, default=False)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AnonymousRateLimit(Base):
    """Persistent rate limiting for anonymous users (survives server restarts)."""
    __tablename__ = "anonymous_rate_limits"

    id = Column(String, primary_key=True, default=generate_uuid)
    ip_address = Column(String, nullable=False, index=True)
    usage_date = Column(String, nullable=False)
    question_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSession(Base):
    """Active user sessions for single-device enforcement."""
    __tablename__ = "user_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    session_token = Column(String, nullable=False, unique=True, index=True)
    device_fingerprint = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    user = relationship("User")


class LoginAttempt(Base):
    """Track login attempts for brute force protection."""
    __tablename__ = "login_attempts"

    id = Column(String, primary_key=True, default=generate_uuid)
    
    ip_address = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True, index=True)
    user_id = Column(String, nullable=True)
    
    success = Column(Boolean, default=False)
    failure_reason = Column(String, nullable=True)
    
    user_agent = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class SecurityLog(Base):
    """Security event logging for suspicious activity detection."""
    __tablename__ = "security_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    
    event_type = Column(String, nullable=False, index=True)
    severity = Column(String, default="info")
    
    user_id = Column(String, nullable=True, index=True)
    ip_address = Column(String, nullable=True, index=True)
    
    details = Column(Text, nullable=True)
    user_agent = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class DeviceAuthChallenge(Base):
    """Pending device authorization challenges requiring email confirmation."""
    __tablename__ = "device_auth_challenges"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    challenge_token = Column(String, nullable=False, unique=True, index=True)
    
    status = Column(String, default="pending")  # pending, approved, denied, expired
    
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    device_info = Column(Text, nullable=True)
    
    pending_session_token = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    user = relationship("User")


class SocialLink(Base):
    """Links external platform accounts (Telegram, WhatsApp) to web accounts."""
    __tablename__ = "social_links"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    platform = Column(String, nullable=False)  # telegram, whatsapp
    external_id = Column(String, nullable=False)  # telegram user ID or phone number
    
    linked_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User")


class TelegramLinkCode(Base):
    """Short-lived codes for linking Telegram accounts to web accounts."""
    __tablename__ = "telegram_link_codes"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    code = Column(String, nullable=False, unique=True, index=True)  # 6-char alphanumeric
    
    is_used = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # 10 minutes from creation
    used_at = Column(DateTime, nullable=True)
    
    user = relationship("User")


class WhatsAppLinkCode(Base):
    """Short-lived codes for linking WhatsApp numbers to web accounts."""
    __tablename__ = "whatsapp_link_codes"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    code = Column(String, nullable=False, unique=True, index=True)  # 6-char alphanumeric
    wa_phone = Column(String, nullable=True)  # WhatsApp phone number (set when consumed)

    is_used = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # 15 minutes from creation
    used_at = Column(DateTime, nullable=True)

    user = relationship("User")
