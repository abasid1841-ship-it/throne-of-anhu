"""Masowe Fellowship Live Chat - API Routes and WebSocket Handler."""

import json
import asyncio
from datetime import datetime
from typing import Dict, Set, Optional, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import get_db
from db_models import User, MasoweChatMessage, MasoweUserRole, MasoweSettings

router = APIRouter(prefix="/api/masowe", tags=["masowe"])

ADMIN_USER_IDS = {"39546572", "abasid1841", "sydneymusiyiwa221@gmail.com", "abasid1841@gmail.com"}
ADMIN_DISPLAY_NAME = "ABASID 1841 RA"
ADMIN_PROFILE_IMAGE = "/static/icon_ra.png"

connected_clients: Dict[str, WebSocket] = {}
online_users: Dict[str, dict] = {}


def is_admin_user(user: User) -> bool:
    """Check if user is an admin by ID or email."""
    user_email_lower = (user.email or "").lower()
    return (
        user.id in ADMIN_USER_IDS or 
        user_email_lower in ADMIN_USER_IDS
    )


def get_user_display_name(user: User) -> str:
    if is_admin_user(user):
        return ADMIN_DISPLAY_NAME
    if user.first_name:
        return f"{user.first_name} {user.last_name or ''}".strip()
    return user.email or user.id[:8]


def get_user_profile_image(user: User) -> str:
    """Get user's profile image URL, using admin icon for admins."""
    if is_admin_user(user):
        return ADMIN_PROFILE_IMAGE
    return user.profile_image_url or ""


def is_admin(user_id: str) -> bool:
    """Check if user ID is in admin list (legacy - use is_admin_user for User objects)."""
    return user_id in ADMIN_USER_IDS


async def broadcast_message(message: dict, exclude_user_id: str = None):
    disconnected = []
    for user_id, ws in connected_clients.items():
        if exclude_user_id and user_id == exclude_user_id:
            continue
        try:
            await ws.send_json(message)
        except:
            disconnected.append(user_id)
    for uid in disconnected:
        connected_clients.pop(uid, None)
        online_users.pop(uid, None)


async def send_to_user(user_id: str, message: dict):
    ws = connected_clients.get(user_id)
    if ws:
        try:
            await ws.send_json(message)
        except:
            connected_clients.pop(user_id, None)
            online_users.pop(user_id, None)


def get_or_create_user_role(db: Session, user_id: str, user: User = None) -> MasoweUserRole:
    """Get or create user role, properly detecting admin status from User object."""
    role = db.query(MasoweUserRole).filter(MasoweUserRole.user_id == user_id).first()
    
    is_user_admin = False
    if user:
        is_user_admin = is_admin_user(user)
    else:
        is_user_admin = is_admin(user_id)
    
    if not role:
        role = MasoweUserRole(user_id=user_id, role="admin" if is_user_admin else "member")
        db.add(role)
        db.commit()
        db.refresh(role)
    elif is_user_admin and role.role != "admin":
        role.role = "admin"
        db.commit()
        db.refresh(role)
    
    return role


def get_settings(db: Session) -> MasoweSettings:
    settings = db.query(MasoweSettings).filter(MasoweSettings.id == "global").first()
    if not settings:
        settings = MasoweSettings(id="global")
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.websocket("/ws/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: str, db: Session = Depends(get_db)):
    print(f"[MASOWE WS] Connection attempt from user_id: {user_id}")
    try:
        await websocket.accept()
        print(f"[MASOWE WS] Connection accepted for user_id: {user_id}")
    except Exception as e:
        print(f"[MASOWE WS] Error accepting connection: {e}")
        return
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"[MASOWE WS] User not found: {user_id}")
        await websocket.close(code=4001, reason="User not found")
        return
    
    print(f"[MASOWE WS] User found: {user.email}")
    
    user_role = get_or_create_user_role(db, user_id, user)
    
    if user_role.is_blocked:
        await websocket.close(code=4003, reason="You are blocked from this chat")
        return
    
    connected_clients[user_id] = websocket
    online_users[user_id] = {
        "id": user_id,
        "name": get_user_display_name(user),
        "role": user_role.role,
        "is_panel": user_role.panel_position is not None
    }
    
    await broadcast_message({
        "type": "user_joined",
        "user": online_users[user_id],
        "online_count": len(online_users)
    })
    
    settings = get_settings(db)
    await websocket.send_json({
        "type": "init",
        "user_role": user_role.role,
        "is_muted": user_role.is_muted,
        "is_panel": user_role.panel_position is not None,
        "service_mode": settings.service_mode,
        "global_mute": settings.global_mute,
        "welcome_message": settings.welcome_message,
        "tiktok_url": settings.tiktok_live_url,
        "online_users": list(online_users.values())
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            await handle_message(data, user_id, user, user_role, db)
    except WebSocketDisconnect:
        pass
    finally:
        connected_clients.pop(user_id, None)
        online_users.pop(user_id, None)
        await broadcast_message({
            "type": "user_left",
            "user_id": user_id,
            "online_count": len(online_users)
        })


async def handle_message(data: dict, user_id: str, user: User, user_role: MasoweUserRole, db: Session):
    msg_type = data.get("type")
    
    if msg_type == "chat":
        db.refresh(user_role)
        settings = get_settings(db)
        
        can_speak = (
            user_role.role in ("admin", "panel") or
            (not user_role.is_muted and not settings.global_mute and not settings.service_mode)
        )
        
        if not can_speak:
            await send_to_user(user_id, {"type": "error", "message": "You are currently muted"})
            return
        
        content = data.get("content", "").strip()
        voice_url = data.get("voice_url")
        message_type = "voice" if voice_url else "text"
        
        if not content and not voice_url:
            return
        
        reply_to_id = data.get("reply_to_id")
        reply_to_author = None
        reply_to_preview = None
        
        if reply_to_id:
            original_msg = db.query(MasoweChatMessage).filter(MasoweChatMessage.id == reply_to_id).first()
            if original_msg:
                original_user = db.query(User).filter(User.id == original_msg.user_id).first()
                reply_to_author = get_user_display_name(original_user) if original_user else "Unknown"
                reply_to_preview = (original_msg.content or "")[:100]
            else:
                reply_to_id = None
        
        msg = MasoweChatMessage(
            user_id=user_id,
            content=content,
            message_type=message_type,
            voice_url=voice_url,
            voice_duration=data.get("voice_duration"),
            is_from_panel=user_role.panel_position is not None,
            reply_to_id=reply_to_id,
            reply_to_author=reply_to_author,
            reply_to_preview=reply_to_preview
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        
        await broadcast_message({
            "type": "chat",
            "id": msg.id,
            "user_id": user_id,
            "user_name": get_user_display_name(user),
            "user_image": get_user_profile_image(user),
            "user_role": user_role.role,
            "is_panel": user_role.panel_position is not None,
            "content": content,
            "message_type": message_type,
            "voice_url": voice_url,
            "voice_duration": data.get("voice_duration"),
            "reply_to_id": reply_to_id,
            "reply_to_author": reply_to_author,
            "reply_to_preview": reply_to_preview,
            "created_at": msg.created_at.isoformat()
        })
    
    elif msg_type == "admin_action" and user_role.role == "admin":
        await handle_admin_action(data, user_id, db)


async def handle_admin_action(data: dict, admin_id: str, db: Session):
    action = data.get("action")
    target_id = data.get("target_user_id")
    
    if action == "mute_user" and target_id:
        role = get_or_create_user_role(db, target_id)
        role.is_muted = True
        role.muted_at = datetime.utcnow()
        role.muted_by = admin_id
        db.commit()
        await send_to_user(target_id, {"type": "muted", "message": "You have been muted by admin"})
        await broadcast_message({"type": "user_muted", "user_id": target_id})
    
    elif action == "unmute_user" and target_id:
        role = get_or_create_user_role(db, target_id)
        role.is_muted = False
        db.commit()
        await send_to_user(target_id, {"type": "unmuted", "message": "You have been unmuted"})
        await broadcast_message({"type": "user_unmuted", "user_id": target_id})
    
    elif action == "block_user" and target_id:
        role = get_or_create_user_role(db, target_id)
        role.is_blocked = True
        role.blocked_at = datetime.utcnow()
        role.blocked_by = admin_id
        db.commit()
        ws = connected_clients.get(target_id)
        if ws:
            await ws.close(code=4003, reason="You have been blocked")
        await broadcast_message({"type": "user_blocked", "user_id": target_id})
    
    elif action == "unblock_user" and target_id:
        role = get_or_create_user_role(db, target_id)
        role.is_blocked = False
        db.commit()
    
    elif action == "set_panel" and target_id:
        position = data.get("position", 1)
        role = get_or_create_user_role(db, target_id)
        role.role = "panel"
        role.panel_position = position
        db.commit()
        await send_to_user(target_id, {"type": "promoted", "message": f"You are now Panel Member #{position}"})
        await broadcast_message({"type": "panel_updated"})
    
    elif action == "remove_panel" and target_id:
        role = get_or_create_user_role(db, target_id)
        role.role = "member"
        role.panel_position = None
        db.commit()
        await send_to_user(target_id, {"type": "demoted", "message": "You have been removed from the panel"})
        await broadcast_message({"type": "panel_updated"})
    
    elif action == "start_service":
        settings = get_settings(db)
        settings.service_mode = True
        settings.global_mute = True
        settings.service_started_at = datetime.utcnow()
        db.commit()
        await broadcast_message({
            "type": "service_started",
            "message": "Service has begun. All members are muted."
        })
    
    elif action == "end_service":
        settings = get_settings(db)
        settings.service_mode = False
        settings.global_mute = False
        db.commit()
        await broadcast_message({
            "type": "service_ended",
            "message": "Service has ended. Chat is now open."
        })
    
    elif action == "mute_all":
        settings = get_settings(db)
        settings.global_mute = True
        db.commit()
        await broadcast_message({"type": "global_mute", "muted": True})
    
    elif action == "unmute_all":
        settings = get_settings(db)
        settings.global_mute = False
        db.commit()
        await broadcast_message({"type": "global_mute", "muted": False})
    
    elif action == "clear_panel":
        panel_members = db.query(MasoweUserRole).filter(MasoweUserRole.panel_position != None).all()
        for role in panel_members:
            role.panel_position = None
            if role.role == "panel":
                role.role = "member"
        db.commit()
        await broadcast_message({"type": "panel_cleared", "message": "All panel members have been removed"})
        await broadcast_message({"type": "panel_updated"})
    
    elif action == "announcement":
        content = data.get("content", "")
        if content:
            msg = MasoweChatMessage(
                user_id=admin_id,
                content=content,
                message_type="system",
                is_announcement=True
            )
            db.add(msg)
            db.commit()
            await broadcast_message({
                "type": "announcement",
                "content": content,
                "created_at": msg.created_at.isoformat()
            })
    
    elif action == "set_tiktok_url":
        url = data.get("url", "")
        settings = get_settings(db)
        settings.tiktok_live_url = url
        db.commit()
        await broadcast_message({"type": "tiktok_updated", "url": url})
    
    elif action == "set_welcome":
        message = data.get("message", "")
        settings = get_settings(db)
        settings.welcome_message = message
        db.commit()


@router.get("/messages")
async def get_recent_messages(limit: int = Query(50, le=200), db: Session = Depends(get_db)):
    messages = db.query(MasoweChatMessage).order_by(desc(MasoweChatMessage.created_at)).limit(limit).all()
    
    result = []
    for msg in reversed(messages):
        user = db.query(User).filter(User.id == msg.user_id).first()
        role = db.query(MasoweUserRole).filter(MasoweUserRole.user_id == msg.user_id).first()
        result.append({
            "id": msg.id,
            "user_id": msg.user_id,
            "user_name": get_user_display_name(user) if user else "Unknown",
            "user_image": get_user_profile_image(user) if user else "",
            "user_role": role.role if role else "member",
            "is_panel": role.panel_position is not None if role else False,
            "content": msg.content,
            "message_type": msg.message_type,
            "voice_url": msg.voice_url,
            "voice_duration": msg.voice_duration,
            "is_announcement": msg.is_announcement,
            "reply_to_id": getattr(msg, 'reply_to_id', None),
            "reply_to_author": getattr(msg, 'reply_to_author', None),
            "reply_to_preview": getattr(msg, 'reply_to_preview', None),
            "created_at": msg.created_at.isoformat()
        })
    return result


@router.get("/settings")
async def get_masowe_settings(db: Session = Depends(get_db)):
    settings = get_settings(db)
    return {
        "service_mode": settings.service_mode,
        "global_mute": settings.global_mute,
        "welcome_message": settings.welcome_message,
        "tiktok_url": settings.tiktok_live_url
    }


@router.get("/panel")
async def get_panel_members(db: Session = Depends(get_db)):
    panel = db.query(MasoweUserRole).filter(
        MasoweUserRole.panel_position != None
    ).order_by(MasoweUserRole.panel_position).all()
    
    result = []
    for role in panel:
        user = db.query(User).filter(User.id == role.user_id).first()
        result.append({
            "user_id": role.user_id,
            "name": get_user_display_name(user) if user else "Unknown",
            "position": role.panel_position
        })
    return result


@router.get("/online")
async def get_online_users():
    return {"count": len(online_users), "users": list(online_users.values())}
