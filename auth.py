"""Google OAuth Authentication for Throne of Anhu."""

import os
import secrets
import httpx
from typing import Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from database import get_db
from db_models import User
from security import (
    create_user_session,
    invalidate_all_user_sessions,
    record_login_attempt,
    log_security_event,
    get_client_ip,
)


router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
SESSION_SECRET = os.environ.get("SESSION_SECRET", secrets.token_hex(32))

# Public base URL for OAuth redirects - use custom domain in production
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_redirect_uri(request: Request) -> str:
    """Get the callback URL for this deployment."""
    # Always use PUBLIC_BASE_URL if set (for production with custom domain)
    if PUBLIC_BASE_URL:
        redirect_uri = f"{PUBLIC_BASE_URL}/auth/callback"
        print(f"[AUTH] Using PUBLIC_BASE_URL: {redirect_uri}")
        return redirect_uri
    
    # Fallback to header detection for development
    host = request.headers.get("x-forwarded-host", "") or request.headers.get("host", "")
    scheme = "https" if is_secure_context(request) else request.url.scheme
    
    # Force www for thecollegeofanhu.com domain
    if host == "thecollegeofanhu.com":
        host = "www.thecollegeofanhu.com"
        print(f"[AUTH] Forcing www prefix for OAuth callback")
    
    redirect_uri = f"{scheme}://{host}/auth/callback"
    print(f"[AUTH] Using header-based redirect_uri: {redirect_uri}")
    return redirect_uri


def is_secure_context(request: Request) -> bool:
    """Check if we're in a secure context (HTTPS)."""
    host = request.headers.get("host", "")
    forwarded_proto = request.headers.get("x-forwarded-proto", "")
    return (
        "replit" in host or 
        host.endswith(".dev") or 
        host.endswith(".com") or
        forwarded_proto == "https" or
        request.url.scheme == "https"
    )


@router.get("/login")
async def login(request: Request):
    """Redirect to Google for authentication."""
    if not GOOGLE_CLIENT_ID:
        return JSONResponse(
            {"error": "Google OAuth not configured"},
            status_code=500
        )
    
    redirect_uri = get_redirect_uri(request)
    print(f"[AUTH] Login attempt - redirect_uri: {redirect_uri}")
    state = secrets.token_urlsafe(32)
    
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    
    response = RedirectResponse(url=f"{GOOGLE_AUTH_URL}?{urlencode(params)}")
    secure = is_secure_context(request)
    response.set_cookie(
        key="auth_state",
        value=state,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=600,
    )
    return response


@router.get("/callback")
async def callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db),
):
    """Handle OAuth callback from Google."""
    from db_models import UserSession, DeviceAuthChallenge
    from email_service import send_device_auth_email
    from security import hash_token
    
    if error:
        print(f"[AUTH] OAuth error: {error}")
        return RedirectResponse(url="/?error=auth_failed")
    
    if not code:
        return RedirectResponse(url="/?error=no_code")
    
    stored_state = request.cookies.get("auth_state")
    if not stored_state or stored_state != state:
        return RedirectResponse(url="/?error=invalid_state")
    
    redirect_uri = get_redirect_uri(request)
    
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
            },
        )
        
        if token_resp.status_code != 200:
            print(f"[AUTH] Token exchange failed: {token_resp.text}")
            return RedirectResponse(url="/?error=token_failed")
        
        tokens = token_resp.json()
        access_token = tokens.get("access_token")
        
        if not access_token:
            return RedirectResponse(url="/?error=no_access_token")
        
        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if userinfo_resp.status_code != 200:
            print(f"[AUTH] Userinfo fetch failed: {userinfo_resp.text}")
            return RedirectResponse(url="/?error=userinfo_failed")
        
        userinfo = userinfo_resp.json()
    
    google_id = userinfo.get("id")
    email = userinfo.get("email")
    first_name = userinfo.get("given_name", userinfo.get("name", "").split()[0] if userinfo.get("name") else None)
    last_name = userinfo.get("family_name")
    profile_image = userinfo.get("picture")
    
    if not google_id or not email:
        return RedirectResponse(url="/?error=missing_user_info")
    
    user = db.query(User).filter(User.email == email).first()
    is_new_user = user is None
    
    if not user:
        user = User(
            id=int(google_id) if google_id.isdigit() else hash(google_id) % (10**9),
            email=email,
            first_name=first_name,
            last_name=last_name,
            profile_image_url=profile_image,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.first_name = first_name or user.first_name
        user.last_name = last_name or user.last_name
        user.profile_image_url = profile_image or user.profile_image_url
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    
    invalidate_all_user_sessions(str(user.id), db)
    
    db_session_token = create_user_session(str(user.id), db, request)
    
    session_hash = hash_token(db_session_token) if db_session_token else None
    
    session_token = jwt.encode(
        {
            "sub": user.id,
            "email": user.email,
            "session_hash": session_hash,
            "exp": datetime.utcnow() + timedelta(days=7),
        },
        SESSION_SECRET,
        algorithm="HS256",
    )
    
    record_login_attempt(
        ip_address=get_client_ip(request),
        db=db,
        success=True,
        email=email,
        user_id=str(user.id),
        user_agent=request.headers.get("user-agent", "")
    )
    
    log_security_event(
        db=db,
        event_type="login_success",
        severity="info",
        user_id=str(user.id),
        ip_address=get_client_ip(request),
        details=f"User {email} logged in successfully. {'First login.' if is_new_user else 'All previous sessions invalidated.'}"
    )
    
    response = RedirectResponse(url="/?login=success")
    response.delete_cookie("auth_state")
    secure = is_secure_context(request)
    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    return response


@router.get("/device/approve/{challenge_token}")
async def approve_device(
    challenge_token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Approve a new device login from email link.
    
    This only marks the challenge as approved. The actual session creation
    happens when the new device polls the status endpoint (one-time consumption).
    """
    from db_models import DeviceAuthChallenge
    
    challenge = db.query(DeviceAuthChallenge).filter(
        DeviceAuthChallenge.challenge_token == challenge_token,
        DeviceAuthChallenge.status == "pending"
    ).first()
    
    if not challenge:
        return RedirectResponse(url="/?error=invalid_or_expired_challenge")
    
    if challenge.expires_at < datetime.utcnow():
        challenge.status = "expired"
        challenge.resolved_at = datetime.utcnow()
        db.commit()
        return RedirectResponse(url="/?error=challenge_expired")
    
    user = db.query(User).filter(User.id == challenge.user_id).first()
    if not user:
        return RedirectResponse(url="/?error=user_not_found")
    
    challenge.status = "approved"
    challenge.resolved_at = datetime.utcnow()
    db.commit()
    
    log_security_event(
        db=db,
        event_type="device_auth_approved",
        severity="info",
        user_id=str(user.id),
        ip_address=get_client_ip(request),
        details=f"New device approved for {user.email}. Waiting for new device to claim session."
    )
    
    return RedirectResponse(url="/?device_approved=true&message=The+new+device+can+now+log+in")


@router.get("/device/deny/{challenge_token}")
async def deny_device(
    challenge_token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Deny a new device login from email link."""
    from db_models import DeviceAuthChallenge
    
    challenge = db.query(DeviceAuthChallenge).filter(
        DeviceAuthChallenge.challenge_token == challenge_token,
        DeviceAuthChallenge.status == "pending"
    ).first()
    
    if not challenge:
        return RedirectResponse(url="/?error=invalid_or_expired_challenge")
    
    challenge.status = "denied"
    challenge.resolved_at = datetime.utcnow()
    db.commit()
    
    log_security_event(
        db=db,
        event_type="device_auth_denied",
        severity="warning",
        user_id=challenge.user_id,
        ip_address=get_client_ip(request),
        details=f"New device login DENIED. Original IP: {challenge.ip_address}"
    )
    
    return RedirectResponse(url="/?device_denied=true")


@router.get("/device/status/{challenge_token}")
async def check_device_status(
    challenge_token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Check status of a pending device authorization.
    
    Security: Only the device with the matching device_secret cookie can claim the session.
    """
    from db_models import DeviceAuthChallenge
    from security import hash_token
    
    challenge = db.query(DeviceAuthChallenge).filter(
        DeviceAuthChallenge.challenge_token == challenge_token
    ).first()
    
    if not challenge:
        return JSONResponse({"status": "not_found"})
    
    if challenge.expires_at < datetime.utcnow() and challenge.status == "pending":
        challenge.status = "expired"
        challenge.resolved_at = datetime.utcnow()
        db.commit()
    
    if challenge.status == "approved":
        if challenge.pending_session_token:
            device_secret = request.cookies.get("device_secret")
            if not device_secret:
                return JSONResponse({"status": "missing_device_secret"})
            
            if hash_token(device_secret) != challenge.pending_session_token:
                log_security_event(
                    db=db,
                    event_type="device_auth_secret_mismatch",
                    severity="warning",
                    user_id=challenge.user_id,
                    ip_address=get_client_ip(request),
                    details="Device secret mismatch - possible hijack attempt"
                )
                return JSONResponse({"status": "invalid_device_secret"})
            
            user = db.query(User).filter(User.id == challenge.user_id).first()
            if user:
                invalidate_all_user_sessions(str(user.id), db)
                
                db_session_token = create_user_session(str(user.id), db, request)
                session_hash = hash_token(db_session_token) if db_session_token else None
                
                session_token = jwt.encode(
                    {
                        "sub": user.id,
                        "email": user.email,
                        "session_hash": session_hash,
                        "exp": datetime.utcnow() + timedelta(days=7),
                    },
                    SESSION_SECRET,
                    algorithm="HS256",
                )
                
                challenge.pending_session_token = None
                challenge.status = "consumed"
                db.commit()
                
                response = JSONResponse({"status": "approved"})
                secure = is_secure_context(request)
                response.set_cookie(
                    key="session",
                    value=session_token,
                    httponly=True,
                    secure=secure,
                    samesite="lax",
                    max_age=60 * 60 * 24 * 7,
                )
                response.delete_cookie("device_secret")
                response.delete_cookie("pending_challenge")
                return response
        
        return JSONResponse({"status": "already_consumed"})
    
    if challenge.status == "consumed":
        return JSONResponse({"status": "already_consumed"})
    
    return JSONResponse({
        "status": challenge.status,
        "expires_in": max(0, int((challenge.expires_at - datetime.utcnow()).total_seconds())) if challenge.status == "pending" else 0
    })


@router.get("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    """Clear the session cookie and invalidate all user sessions."""
    user = get_optional_user(request, db)
    
    if user:
        invalidate_all_user_sessions(str(user.id), db)
        log_security_event(
            db=db,
            event_type="logout",
            severity="info",
            user_id=str(user.id),
            ip_address=get_client_ip(request),
            details=f"User {user.email} logged out. All sessions invalidated."
        )
    
    response = RedirectResponse(url="/")
    response.delete_cookie("session")
    response.delete_cookie("pending_challenge")
    return response


@router.get("/me")
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get the currently logged in user."""
    session_token = request.cookies.get("session")
    if not session_token:
        return JSONResponse({"user": None})
    
    try:
        payload = jwt.decode(session_token, SESSION_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            return JSONResponse({"user": None})
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse({"user": None})
        
        admin_emails_env = os.environ.get("THRONE_ADMIN_EMAILS", "sydneymusiyiwa221@gmail.com,abasid1841@gmail.com")
        ADMIN_EMAILS = [e.strip().lower() for e in admin_emails_env.split(",") if e.strip()]
        user_email_lower = (user.email or "").lower()
        is_admin = user_email_lower in ADMIN_EMAILS
        
        print(f"[AUTH] Checking user: email={user.email}, tier={user.subscription_tier}, is_subscriber={user.is_subscriber}, is_admin={is_admin}")
        
        if is_admin:
            user.subscription_tier = "admin"
            user.is_subscriber = True
            user.daily_limit = 10_000_000
            db.commit()
            db.refresh(user)
            print(f"[AUTH] Set admin privileges for {user.email}, daily_limit=10000000")
        
        return JSONResponse({
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_image_url": user.profile_image_url,
                "is_subscriber": True if is_admin else user.is_subscriber,
                "subscription_tier": "admin" if is_admin else user.subscription_tier,
                "is_admin": is_admin,
            }
        })
    except JWTError:
        return JSONResponse({"user": None})


def get_optional_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Dependency to get the current user if logged in."""
    from db_models import UserSession
    from datetime import timedelta
    
    session_token = request.cookies.get("session")
    if not session_token:
        return None
    
    try:
        payload = jwt.decode(session_token, SESSION_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        session_hash = payload.get("session_hash")
        
        if not user_id:
            return None
        
        if session_hash:
            try:
                active_session = db.query(UserSession).filter(
                    UserSession.user_id == str(user_id),
                    UserSession.session_token == session_hash,
                    UserSession.is_active == True
                ).first()
                
                if not active_session:
                    return None
                
                if active_session.expires_at and active_session.expires_at < datetime.utcnow():
                    active_session.is_active = False
                    db.commit()
                    return None
                
                if active_session.last_activity:
                    inactivity = datetime.utcnow() - active_session.last_activity
                    if inactivity > timedelta(hours=24):
                        active_session.is_active = False
                        db.commit()
                        return None
                
                active_session.last_activity = datetime.utcnow()
                db.commit()
            except Exception as e:
                print(f"[AUTH] Session validation error (non-fatal): {e}")
                try:
                    db.rollback()
                except:
                    pass
        
        return db.query(User).filter(User.id == user_id).first()
    except JWTError:
        return None


def require_login(request: Request, db: Session = Depends(get_db)) -> User:
    """Dependency that requires a logged in user."""
    user = get_optional_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return user
