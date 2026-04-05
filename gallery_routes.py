"""API routes for Gallery and Fellowship features."""

import os
import re
import uuid
import shutil
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from db_models import GalleryItem, FellowshipThread, FellowshipReply, User
from auth import get_optional_user, require_login


def extract_youtube_thumbnail(url: Optional[str]) -> Optional[str]:
    """Extract YouTube thumbnail URL from a YouTube video URL."""
    if not url:
        return None
    
    youtube_patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in youtube_patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    
    return None


def extract_google_drive_thumbnail(url: Optional[str]) -> Optional[str]:
    """Extract Google Drive thumbnail URL from a Drive video/file URL."""
    if not url:
        return None
    
    drive_patterns = [
        r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
        r'drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
        r'drive\.google\.com/uc\?id=([a-zA-Z0-9_-]+)',
        r'docs\.google\.com/file/d/([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in drive_patterns:
        match = re.search(pattern, url)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/thumbnail?id={file_id}&sz=w400"
    
    return None


def get_auto_thumbnail(item) -> Optional[str]:
    """Get thumbnail for an item, auto-generating for video/PDF URLs if needed."""
    if item.thumbnail_url:
        return item.thumbnail_url
    
    if item.item_type == "video" and item.file_url:
        drive_thumb = extract_google_drive_thumbnail(item.file_url)
        if drive_thumb:
            return drive_thumb
        
        youtube_thumb = extract_youtube_thumbnail(item.file_url)
        if youtube_thumb:
            return youtube_thumb
    
    if item.item_type == "pdf" and item.file_url:
        drive_thumb = extract_google_drive_thumbnail(item.file_url)
        if drive_thumb:
            return drive_thumb
    
    return None


VIDEO_LANGUAGE_CATEGORIES = ["ENGLISH", "SHONA", "KISWAHILI", "ZULU_NDEBELE"]


UPLOAD_DIR = "uploads/gallery"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/mp3", "audio/wav", "audio/m4a", "audio/x-m4a", "audio/aac"}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit


router = APIRouter(prefix="/api", tags=["gallery", "fellowship"])


class GalleryItemResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    item_type: str
    file_url: Optional[str]
    thumbnail_url: Optional[str]
    duration: Optional[str]
    category: Optional[str]
    view_count: int
    is_downloadable: bool
    subscribers_only: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GalleryItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    item_type: str
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[str] = None
    category: Optional[str] = None
    is_downloadable: bool = True
    subscribers_only: bool = False


class ThreadResponse(BaseModel):
    id: str
    title: str
    body: str
    category: Optional[str]
    reply_count: int
    like_count: int
    is_pinned: bool
    author_name: str
    author_avatar: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ThreadCreate(BaseModel):
    title: str
    body: str
    category: Optional[str] = None


class ReplyResponse(BaseModel):
    id: str
    content: str
    like_count: int
    author_name: str
    author_avatar: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ReplyCreate(BaseModel):
    content: str


@router.get("/gallery", response_model=List[GalleryItemResponse])
async def get_gallery_items(
    item_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Get gallery items, optionally filtered by type."""
    query = db.query(GalleryItem)
    
    if item_type:
        type_map = {"videos": "video", "images": "image", "pdfs": "pdf"}
        normalized_type = type_map.get(item_type, item_type)
        query = query.filter(GalleryItem.item_type == normalized_type)
    
    if category:
        query = query.filter(GalleryItem.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (GalleryItem.title.ilike(search_term)) |
            (GalleryItem.description.ilike(search_term))
        )
    
    is_subscriber = user and user.is_subscriber if user else False
    if not is_subscriber:
        query = query.filter(GalleryItem.subscribers_only == False)
    
    items = query.order_by(GalleryItem.created_at.desc()).all()
    
    result = []
    for item in items:
        auto_thumb = get_auto_thumbnail(item)
        result.append(GalleryItemResponse(
            id=item.id,
            title=item.title,
            description=item.description,
            item_type=item.item_type,
            file_url=item.file_url,
            thumbnail_url=auto_thumb,
            duration=item.duration,
            category=item.category,
            view_count=item.view_count,
            is_downloadable=item.is_downloadable,
            subscribers_only=item.subscribers_only,
            created_at=item.created_at,
        ))
    return result


@router.get("/gallery/{item_id}", response_model=GalleryItemResponse)
async def get_gallery_item(
    item_id: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Get a single gallery item with full details."""
    item = db.query(GalleryItem).filter(GalleryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item.subscribers_only:
        if not user or not user.is_subscriber:
            raise HTTPException(status_code=403, detail="Subscribers only")
    
    item.view_count += 1
    db.commit()
    
    auto_thumb = get_auto_thumbnail(item)
    return GalleryItemResponse(
        id=item.id,
        title=item.title,
        description=item.description,
        item_type=item.item_type,
        file_url=item.file_url,
        thumbnail_url=auto_thumb,
        duration=item.duration,
        category=item.category,
        view_count=item.view_count,
        is_downloadable=item.is_downloadable,
        subscribers_only=item.subscribers_only,
        created_at=item.created_at,
    )


ADMIN_USER_IDS = ["admin", "owner", "sydneymusiyiwa221@gmail.com", "abasid1841@gmail.com"]

def is_admin_user(user: User) -> bool:
    """Check if user has admin privileges."""
    if getattr(user, 'is_admin', False):
        return True
    if user.id in ADMIN_USER_IDS:
        return True
    if getattr(user, 'email', None) in ADMIN_USER_IDS:
        return True
    return False

@router.post("/gallery", response_model=GalleryItemResponse)
async def create_gallery_item(
    item: GalleryItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_login),
):
    """Create a new gallery item (admin only)."""
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    new_item = GalleryItem(
        title=item.title,
        description=item.description,
        item_type=item.item_type,
        file_url=item.file_url,
        thumbnail_url=item.thumbnail_url,
        duration=item.duration,
        category=item.category,
        is_downloadable=item.is_downloadable,
        subscribers_only=item.subscribers_only,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.post("/gallery/upload", response_model=GalleryItemResponse)
async def upload_gallery_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    item_type: str = Form(...),
    description: Optional[str] = Form(None),
    duration: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    is_downloadable: bool = Form(True),
    subscribers_only: bool = Form(False),
    db: Session = Depends(get_db),
    user: User = Depends(require_login),
):
    """Upload a file directly to the gallery (admin only)."""
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    content_type = file.content_type or ""
    
    if item_type == "video" and content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid video format. Allowed: MP4, WebM, MOV, AVI"
        )
    elif item_type == "music" and content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid audio format. Allowed: MP3, WAV, M4A, AAC"
        )
    elif item_type == "image" and content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid image format. Allowed: JPG, PNG, WebP, GIF"
        )
    
    file_ext = os.path.splitext(file.filename or "file")[1].lower()
    if not file_ext:
        ext_map = {
            "video/mp4": ".mp4", "video/webm": ".webm", "video/quicktime": ".mov",
            "audio/mpeg": ".mp3", "audio/mp3": ".mp3", "audio/wav": ".wav",
            "audio/m4a": ".m4a", "audio/x-m4a": ".m4a",
            "image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"
        }
        file_ext = ext_map.get(content_type, ".bin")
    
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="File too large. Maximum 100MB.")
    
    file_url = f"/uploads/gallery/{unique_filename}"
    
    new_item = GalleryItem(
        title=title,
        description=description,
        item_type=item_type,
        file_url=file_url,
        duration=duration,
        category=category,
        is_downloadable=is_downloadable,
        subscribers_only=subscribers_only,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    print(f"[GALLERY] Uploaded {item_type}: {title} -> {file_path} ({file_size} bytes)")
    return new_item


class GalleryItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[str] = None
    category: Optional[str] = None
    is_downloadable: Optional[bool] = None
    subscribers_only: Optional[bool] = None


@router.put("/gallery/{item_id}", response_model=GalleryItemResponse)
async def update_gallery_item(
    item_id: str,
    updates: GalleryItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_login),
):
    """Update a gallery item (admin only)."""
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    item = db.query(GalleryItem).filter(GalleryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if updates.title is not None:
        item.title = updates.title
    if updates.description is not None:
        item.description = updates.description
    if updates.file_url is not None:
        item.file_url = updates.file_url
    if updates.thumbnail_url is not None:
        item.thumbnail_url = updates.thumbnail_url
    if updates.duration is not None:
        item.duration = updates.duration
    if updates.category is not None:
        item.category = updates.category
    if updates.is_downloadable is not None:
        item.is_downloadable = updates.is_downloadable
    if updates.subscribers_only is not None:
        item.subscribers_only = updates.subscribers_only
    
    db.commit()
    db.refresh(item)
    print(f"[GALLERY] Updated item: {item.title} (id={item_id})")
    return item


@router.delete("/gallery/{item_id}")
async def delete_gallery_item(
    item_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_login),
):
    """Delete a gallery item (admin only)."""
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    item = db.query(GalleryItem).filter(GalleryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    title = item.title
    
    if item.file_url and item.file_url.startswith("/uploads/gallery/"):
        local_path = item.file_url.lstrip("/")
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
                print(f"[GALLERY] Deleted local file: {local_path}")
            except Exception as e:
                print(f"[GALLERY] Error deleting file: {e}")
    
    db.delete(item)
    db.commit()
    print(f"[GALLERY] Deleted item: {title} (id={item_id})")
    return {"message": f"Item '{title}' deleted successfully"}


@router.get("/gallery/{item_id}/download")
async def download_gallery_item(
    item_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_login),
):
    """Get download URL for a gallery item (subscribers only)."""
    item = db.query(GalleryItem).filter(GalleryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if not item.is_downloadable:
        raise HTTPException(status_code=403, detail="Item not downloadable")
    
    if item.subscribers_only and not user.is_subscriber:
        raise HTTPException(status_code=403, detail="Subscribers only")
    
    if not user.is_subscriber:
        raise HTTPException(status_code=403, detail="Subscribe to download")
    
    item.download_count += 1
    db.commit()
    
    return {"download_url": item.file_url}


@router.get("/fellowship/threads", response_model=List[ThreadResponse])
async def get_threads(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Get all discussion threads."""
    query = db.query(FellowshipThread)
    
    if category:
        query = query.filter(FellowshipThread.category == category)
    
    threads = query.order_by(
        FellowshipThread.is_pinned.desc(),
        FellowshipThread.created_at.desc()
    ).limit(50).all()
    
    result = []
    for t in threads:
        result.append({
            "id": t.id,
            "title": t.title,
            "body": t.body[:200] + "..." if len(t.body) > 200 else t.body,
            "category": t.category,
            "reply_count": t.reply_count,
            "like_count": t.like_count,
            "is_pinned": t.is_pinned,
            "author_name": t.user.first_name or "Seeker" if t.user else "Seeker",
            "author_avatar": t.user.profile_image_url if t.user else None,
            "created_at": t.created_at,
        })
    
    return result


@router.get("/fellowship/threads/{thread_id}")
async def get_thread(
    thread_id: str,
    db: Session = Depends(get_db),
):
    """Get a single thread with replies."""
    thread = db.query(FellowshipThread).filter(FellowshipThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    replies = db.query(FellowshipReply).filter(
        FellowshipReply.thread_id == thread_id
    ).order_by(FellowshipReply.created_at.asc()).all()
    
    return {
        "id": thread.id,
        "title": thread.title,
        "body": thread.body,
        "category": thread.category,
        "reply_count": thread.reply_count,
        "like_count": thread.like_count,
        "is_pinned": thread.is_pinned,
        "is_locked": thread.is_locked,
        "author_name": thread.user.first_name or "Seeker" if thread.user else "Seeker",
        "author_avatar": thread.user.profile_image_url if thread.user else None,
        "created_at": thread.created_at,
        "replies": [
            {
                "id": r.id,
                "content": r.content,
                "like_count": r.like_count,
                "author_name": r.user.first_name or "Seeker" if r.user else "Seeker",
                "author_avatar": r.user.profile_image_url if r.user else None,
                "created_at": r.created_at,
            }
            for r in replies
        ],
    }


@router.post("/fellowship/threads", response_model=ThreadResponse)
async def create_thread(
    thread: ThreadCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_login),
):
    """Create a new discussion thread (subscribers only)."""
    if not user.is_subscriber:
        raise HTTPException(status_code=403, detail="Subscribe to join the Fellowship")
    
    new_thread = FellowshipThread(
        user_id=user.id,
        title=thread.title[:200],
        body=thread.body[:3000],
        category=thread.category,
    )
    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)
    
    return {
        "id": new_thread.id,
        "title": new_thread.title,
        "body": new_thread.body,
        "category": new_thread.category,
        "reply_count": 0,
        "like_count": 0,
        "is_pinned": False,
        "author_name": user.first_name or "Seeker",
        "author_avatar": user.profile_image_url,
        "created_at": new_thread.created_at,
    }


@router.post("/fellowship/threads/{thread_id}/replies", response_model=ReplyResponse)
async def create_reply(
    thread_id: str,
    reply: ReplyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_login),
):
    """Add a reply to a thread (subscribers only)."""
    if not user.is_subscriber:
        raise HTTPException(status_code=403, detail="Subscribe to join the Fellowship")
    
    thread = db.query(FellowshipThread).filter(FellowshipThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if thread.is_locked:
        raise HTTPException(status_code=403, detail="Thread is locked")
    
    new_reply = FellowshipReply(
        thread_id=thread_id,
        user_id=user.id,
        content=reply.content[:2000],
    )
    db.add(new_reply)
    
    thread.reply_count += 1
    thread.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_reply)
    
    return {
        "id": new_reply.id,
        "content": new_reply.content,
        "like_count": 0,
        "author_name": user.first_name or "Seeker",
        "author_avatar": user.profile_image_url,
        "created_at": new_reply.created_at,
    }
