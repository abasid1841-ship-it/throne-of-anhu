"""
Security module for Throne of Anhu.
Implements comprehensive security measures:
- Persistent IP-based rate limiting (survives server restarts)
- Single-device session enforcement
- Login attempt tracking and account lockout
- Security logging
- Session management
"""

import os
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta, date
from typing import Optional, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_

ANON_DAILY_LIMIT = int(os.environ.get("THRONE_ANON_DAILY_LIMIT", "3"))
FREE_DAILY_LIMIT = int(os.environ.get("THRONE_FREE_DAILY_LIMIT", "3"))

MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 30
SESSION_EXPIRY_HOURS = 24
SESSION_INACTIVITY_MINUTES = 60


def get_client_ip(request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def generate_session_token() -> str:
    return secrets.token_urlsafe(64)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def check_anonymous_rate_limit(ip_address: str, db: Session) -> Tuple[bool, int, str]:
    """
    Check rate limit for anonymous users with persistent database storage.
    Returns: (allowed, remaining, message)
    """
    from db_models import AnonymousRateLimit
    
    today = date.today().isoformat()
    
    try:
        record = db.query(AnonymousRateLimit).filter(
            and_(
                AnonymousRateLimit.ip_address == ip_address,
                AnonymousRateLimit.usage_date == today
            )
        ).first()
        
        current_count = record.question_count if record else 0
        
        if current_count >= ANON_DAILY_LIMIT:
            return False, 0, (
                "🦁 The cup has run over for today.\n\n"
                "You have reached your 3 free questions for today.\n\n"
                "Log in and subscribe to receive more communion:\n"
                "• Seeker ($10/month): 20 questions daily\n"
                "• Premium ($20/month): 45 questions daily\n\n"
                "👉 Click 'Login' to begin your journey."
            )
        
        remaining = max(0, ANON_DAILY_LIMIT - current_count - 1)
        return True, remaining, ""
        
    except Exception as e:
        print(f"[SECURITY] Anonymous rate limit check error: {e}")
        return True, 2, ""


def increment_anonymous_usage(ip_address: str, db: Session) -> None:
    """Increment usage count for anonymous user (persisted in database)."""
    from db_models import AnonymousRateLimit
    
    today = date.today().isoformat()
    
    try:
        record = db.query(AnonymousRateLimit).filter(
            and_(
                AnonymousRateLimit.ip_address == ip_address,
                AnonymousRateLimit.usage_date == today
            )
        ).first()
        
        if record:
            record.question_count = (record.question_count or 0) + 1
            record.updated_at = datetime.utcnow()
        else:
            record = AnonymousRateLimit(
                ip_address=ip_address,
                usage_date=today,
                question_count=1
            )
            db.add(record)
        
        db.commit()
    except Exception as e:
        print(f"[SECURITY] Anonymous usage increment error: {e}")
        try:
            db.rollback()
        except:
            pass


def get_anonymous_usage_stats(ip_address: str, db: Session) -> dict:
    """Get usage statistics for anonymous user."""
    from db_models import AnonymousRateLimit
    
    today = date.today().isoformat()
    
    try:
        record = db.query(AnonymousRateLimit).filter(
            and_(
                AnonymousRateLimit.ip_address == ip_address,
                AnonymousRateLimit.usage_date == today
            )
        ).first()
        
        count = record.question_count if record else 0
        return {
            "today": count,
            "limit": ANON_DAILY_LIMIT,
            "remaining": max(0, ANON_DAILY_LIMIT - count)
        }
    except Exception as e:
        print(f"[SECURITY] Anonymous usage stats error: {e}")
        return {"today": 0, "limit": ANON_DAILY_LIMIT, "remaining": ANON_DAILY_LIMIT}


def create_user_session(user_id: str, db: Session, request) -> str:
    """
    Create a new session for user, invalidating all previous sessions (single-device).
    Returns the session token.
    """
    from db_models import UserSession
    
    try:
        db.query(UserSession).filter(
            UserSession.user_id == user_id
        ).update({"is_active": False})
        db.commit()
    except Exception as e:
        print(f"[SECURITY] Error invalidating old sessions: {e}")
        try:
            db.rollback()
        except:
            pass
    
    token = generate_session_token()
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")[:500]
    
    expires_at = datetime.utcnow() + timedelta(hours=SESSION_EXPIRY_HOURS)
    
    try:
        session = UserSession(
            user_id=user_id,
            session_token=hash_token(token),
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True,
            last_activity=datetime.utcnow(),
            expires_at=expires_at
        )
        db.add(session)
        db.commit()
        
        log_security_event(
            db=db,
            event_type="session_created",
            severity="info",
            user_id=user_id,
            ip_address=ip_address,
            details=f"New session created, all previous sessions invalidated"
        )
        
        return token
    except Exception as e:
        print(f"[SECURITY] Session creation error: {e}")
        try:
            db.rollback()
        except:
            pass
        return ""


def validate_user_session(token: str, db: Session, request) -> Tuple[bool, Optional[str], str]:
    """
    Validate a session token.
    Returns: (valid, user_id, error_message)
    """
    from db_models import UserSession
    
    if not token:
        return False, None, "No session token provided"
    
    hashed = hash_token(token)
    
    try:
        session = db.query(UserSession).filter(
            UserSession.session_token == hashed,
            UserSession.is_active == True
        ).first()
        
        if not session:
            return False, None, "Session not found or expired"
        
        if session.expires_at and session.expires_at < datetime.utcnow():
            session.is_active = False
            db.commit()
            return False, None, "Session expired"
        
        if session.last_activity:
            inactivity = datetime.utcnow() - session.last_activity
            if inactivity > timedelta(minutes=SESSION_INACTIVITY_MINUTES):
                session.is_active = False
                db.commit()
                return False, None, "Session timed out due to inactivity"
        
        session.last_activity = datetime.utcnow()
        session.ip_address = get_client_ip(request)
        db.commit()
        
        return True, session.user_id, ""
        
    except Exception as e:
        print(f"[SECURITY] Session validation error: {e}")
        try:
            db.rollback()
        except:
            pass
        return False, None, "Session validation error"


def invalidate_user_session(token: str, db: Session) -> bool:
    """Invalidate a specific session (logout)."""
    from db_models import UserSession
    
    if not token:
        return False
    
    hashed = hash_token(token)
    
    try:
        session = db.query(UserSession).filter(
            UserSession.session_token == hashed
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            return True
        return False
    except Exception as e:
        print(f"[SECURITY] Session invalidation error: {e}")
        try:
            db.rollback()
        except:
            pass
        return False


def invalidate_all_user_sessions(user_id: str, db: Session) -> int:
    """Invalidate all sessions for a user (force logout from all devices)."""
    from db_models import UserSession
    
    try:
        count = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).update({"is_active": False})
        db.commit()
        return count
    except Exception as e:
        print(f"[SECURITY] Invalidate all sessions error: {e}")
        try:
            db.rollback()
        except:
            pass
        return 0


def check_login_allowed(ip_address: str, email: str, db: Session) -> Tuple[bool, str]:
    """
    Check if login is allowed based on recent failed attempts.
    Returns: (allowed, message)
    """
    from db_models import LoginAttempt
    
    cutoff = datetime.utcnow() - timedelta(minutes=LOGIN_LOCKOUT_MINUTES)
    
    try:
        recent_failures = db.query(LoginAttempt).filter(
            LoginAttempt.ip_address == ip_address,
            LoginAttempt.success == False,
            LoginAttempt.created_at > cutoff
        ).count()
        
        if recent_failures >= MAX_LOGIN_ATTEMPTS:
            remaining_mins = LOGIN_LOCKOUT_MINUTES
            return False, f"Too many failed login attempts. Please try again in {remaining_mins} minutes."
        
        if email:
            email_failures = db.query(LoginAttempt).filter(
                LoginAttempt.email == email.lower(),
                LoginAttempt.success == False,
                LoginAttempt.created_at > cutoff
            ).count()
            
            if email_failures >= MAX_LOGIN_ATTEMPTS:
                return False, f"This account is temporarily locked. Please try again in {LOGIN_LOCKOUT_MINUTES} minutes."
        
        return True, ""
        
    except Exception as e:
        print(f"[SECURITY] Login check error: {e}")
        return True, ""


def record_login_attempt(
    ip_address: str,
    db: Session,
    success: bool,
    email: str = None,
    user_id: str = None,
    failure_reason: str = None,
    user_agent: str = None
) -> None:
    """Record a login attempt for security tracking."""
    from db_models import LoginAttempt
    
    try:
        attempt = LoginAttempt(
            ip_address=ip_address,
            email=email.lower() if email else None,
            user_id=user_id,
            success=success,
            failure_reason=failure_reason,
            user_agent=user_agent[:500] if user_agent else None
        )
        db.add(attempt)
        db.commit()
        
        if not success:
            log_security_event(
                db=db,
                event_type="failed_login",
                severity="warning",
                user_id=user_id,
                ip_address=ip_address,
                details=f"Failed login attempt for {email}: {failure_reason}"
            )
            
    except Exception as e:
        print(f"[SECURITY] Record login attempt error: {e}")
        try:
            db.rollback()
        except:
            pass


def log_security_event(
    db: Session,
    event_type: str,
    severity: str = "info",
    user_id: str = None,
    ip_address: str = None,
    details: str = None,
    user_agent: str = None
) -> None:
    """Log a security event for audit trail."""
    from db_models import SecurityLog
    
    try:
        log = SecurityLog(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            details=details,
            user_agent=user_agent[:500] if user_agent else None
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"[SECURITY] Log event error: {e}")
        try:
            db.rollback()
        except:
            pass


def cleanup_old_data(db: Session, days: int = 30) -> dict:
    """Clean up old security data (login attempts, security logs, expired sessions)."""
    from db_models import LoginAttempt, SecurityLog, UserSession, AnonymousRateLimit
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    results = {
        "login_attempts": 0,
        "security_logs": 0,
        "expired_sessions": 0,
        "old_rate_limits": 0
    }
    
    try:
        results["login_attempts"] = db.query(LoginAttempt).filter(
            LoginAttempt.created_at < cutoff
        ).delete()
        
        results["security_logs"] = db.query(SecurityLog).filter(
            SecurityLog.created_at < cutoff
        ).delete()
        
        results["expired_sessions"] = db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).delete()
        
        results["old_rate_limits"] = db.query(AnonymousRateLimit).filter(
            AnonymousRateLimit.usage_date < yesterday
        ).delete()
        
        db.commit()
    except Exception as e:
        print(f"[SECURITY] Cleanup error: {e}")
        try:
            db.rollback()
        except:
            pass
    
    return results


def get_active_sessions_count(user_id: str, db: Session) -> int:
    """Get count of active sessions for a user."""
    from db_models import UserSession
    
    try:
        return db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).count()
    except:
        return 0
