# main.py
# FastAPI backend for THRONE OF ANHU (DEPLOY-SAFE / PROMOTION-SAFE)

from pathlib import Path
from typing import List, Optional, Any, Dict
from datetime import date
import os
import json
import asyncio
import re

import httpx
from fastapi import FastAPI, HTTPException, Query, Request, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models import ThroneRequest, ThroneResponse
from local_storehouse import match_local_storehouse
from throne_engine import call_temple_engine
from scroll_library import find_scroll_by_title_like
from safety import apply_safety_filters
from witness_engine import gather_witnesses

from database import get_db  # IMPORTANT: DO NOT init_db at startup
from db_models import User, WisdomCard
from auth import router as auth_router, get_optional_user
from subscription import (
    check_rate_limit as check_subscription_limit,
    SUBSCRIPTION_TIERS,
    get_usage_stats,
    get_user_tier,
    increment_usage,
)
from stripe_routes import router as stripe_router
from gallery_routes import router as gallery_router
from masowe_routes import router as masowe_router
from telegram_routes import router as telegram_router
from usage_tracker import track_usage, get_user_usage, get_all_users_usage, get_total_usage
from admin_routes import router as admin_router


# ================================================================
# WISDOM CARDS (DB storehouse) — inline implementation
# ================================================================

def _safe_load_patterns(patterns_json: str) -> List[str]:
    try:
        data = json.loads(patterns_json or "[]")
        if isinstance(data, list):
            return [str(x) for x in data if str(x).strip()]
    except Exception:
        pass
    return []


def match_wisdom_cards(
    db: Optional[Session],
    message: str,
    language: str = "ENGLISH",
) -> Optional[Dict[str, Any]]:
    """
    Returns a ThroneResponse-like dict if a WisdomCard matches, else None.
    """
    if not db:
        return None

    text = (message or "").strip()
    if not text:
        return None

    lang = (language or "ENGLISH").strip().upper()

    cards = (
        db.query(WisdomCard)
        .filter(WisdomCard.enabled == True)
        .filter((WisdomCard.language == lang) | (WisdomCard.language == "ENGLISH"))
        .order_by(WisdomCard.priority.asc(), WisdomCard.updated_at.desc())
        .all()
    )

    for c in cards:
        patterns = _safe_load_patterns(c.patterns_json)
        for p in patterns:
            try:
                if re.search(p, text, flags=re.IGNORECASE | re.MULTILINE):
                    return {
                        "persona": c.persona or "RA",
                        "mode": c.mode or "outer_court",
                        "answer": c.answer,
                        "witnesses": None,
                        "source": "wisdom_card",
                        "card_id": c.id,
                        "card_title": c.title,
                    }
            except re.error:
                continue

    return None


def create_wisdom_card(
    db: Session,
    *,
    title: str,
    language: str,
    patterns: List[str],
    answer: str,
    persona: str = "RA",
    mode: str = "outer_court",
    enabled: bool = True,
    priority: int = 100,
) -> WisdomCard:
    patterns_clean = [str(x) for x in (patterns or []) if str(x).strip()]
    wc = WisdomCard(
        title=(title or "Untitled").strip(),
        language=(language or "ENGLISH").strip().upper(),
        patterns_json=json.dumps(patterns_clean),
        answer=answer or "",
        persona=(persona or "RA").strip(),
        mode=(mode or "outer_court").strip(),
        enabled=bool(enabled),
        priority=int(priority or 100),
    )
    db.add(wc)
    db.commit()
    db.refresh(wc)
    return wc


def update_wisdom_card(
    db: Session,
    card_id: str,
    patch: Dict[str, Any],
) -> Optional[WisdomCard]:
    wc = db.query(WisdomCard).filter(WisdomCard.id == card_id).first()
    if not wc:
        return None

    if "title" in patch:
        wc.title = str(patch["title"] or "").strip() or wc.title

    if "language" in patch:
        wc.language = str(patch["language"] or "ENGLISH").strip().upper()

    if "patterns" in patch:
        pats = patch.get("patterns") or []
        if isinstance(pats, list):
            wc.patterns_json = json.dumps([str(x) for x in pats if str(x).strip()])

    if "answer" in patch:
        wc.answer = str(patch["answer"] or "").strip() or wc.answer

    if "persona" in patch:
        wc.persona = str(patch["persona"] or "RA").strip()

    if "mode" in patch:
        wc.mode = str(patch["mode"] or "outer_court").strip()

    if "enabled" in patch:
        wc.enabled = bool(patch["enabled"])

    if "priority" in patch:
        try:
            wc.priority = int(patch["priority"])
        except Exception:
            pass

    db.commit()
    db.refresh(wc)
    return wc


# ================================================================
# APP INIT
# ================================================================

app = FastAPI(title="Throne of Anhu · ABASID 1841")
app.include_router(auth_router)
app.include_router(stripe_router)
app.include_router(gallery_router)
app.include_router(masowe_router)
app.include_router(admin_router)
app.include_router(telegram_router)

# ================================================================
# CORS
# ================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================
# DEPLOY HEALTHCHECKS (FAST + ALWAYS 200)
# ================================================================

@app.get("/health", include_in_schema=False)
@app.head("/health", include_in_schema=False)
async def healthcheck():
    return PlainTextResponse("OK", status_code=200)


# ================================================================
# STATIC FILES + UI (UI at /app)
# ================================================================

app.mount("/static", StaticFiles(directory="static"), name="static")

os.makedirs("uploads/gallery", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

INDEX_PATH = Path("static/index.html")
PDF_PATH = Path("static/scrolls/anhu_scroll_library.pdf")


@app.get("/app", response_class=HTMLResponse)
async def app_ui():
    if INDEX_PATH.exists():
        return FileResponse(str(INDEX_PATH))
    return HTMLResponse("<h1>Throne of Anhu backend is running.</h1>", status_code=200)


# ================================================================
# ROOT (supports Meta verify if needed)
# ================================================================

@app.get("/", include_in_schema=False)
async def root_get(
    request: Request,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token:
        verify = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")
        if hub_verify_token == verify:
            print(f"[WHATSAPP] Root verification OK, challenge={hub_challenge}")
            return PlainTextResponse(hub_challenge or "", status_code=200)
        return PlainTextResponse("Forbidden", status_code=403)

    if INDEX_PATH.exists():
        return FileResponse(str(INDEX_PATH))
    return HTMLResponse("<h1>Throne of Anhu backend is running.</h1>", status_code=200)


@app.post("/", include_in_schema=False)
async def root_post(request: Request):
    """
    Optional: handle WhatsApp payloads sent to root.
    Returns 200 quickly.
    """
    from starlette.responses import JSONResponse

    try:
        payload = await request.json()
    except Exception as e:
        print(f"[WHATSAPP] Root JSON error: {e}")
        return JSONResponse({"ok": True})

    msgs = _extract_whatsapp_text_messages(payload)
    if not msgs:
        return JSONResponse({"ok": True})

    for m in msgs:
        sender = m.get("from")
        text = (m.get("text") or "").strip()
        if not sender or not text:
            continue

        wa_user_id = f"whatsapp_{sender}"

        throne_resp = await handle_throne_message(
            message=text,
            language="ENGLISH",
            user_id=wa_user_id,
            db=None,
        )

        reply = throne_resp.answer or "The Throne is silent."
        await _send_whatsapp_text(sender, reply)

    return JSONResponse({"ok": True})


@app.get("/scrolls/download")
async def download_scrolls_pdf():
    if PDF_PATH.exists():
        return FileResponse(
            str(PDF_PATH),
            media_type="application/pdf",
            filename="anhu_scroll_library.pdf",
        )
    raise HTTPException(status_code=404, detail="Scroll library PDF not found")


# ================================================================
# SCROLL LIBRARY (LAZY LOAD — NO STARTUP BLOCKING)
# ================================================================

BASE_DIR = Path(__file__).resolve().parent

SCROLLS_PATH_CANDIDATES = [
    BASE_DIR / "scrolls.json",
    BASE_DIR / "allscrolls.json",
    BASE_DIR / "static" / "scrolls.json",
    BASE_DIR / "static" / "allscrolls.json",
    BASE_DIR / "allscrolls.json" / "scrolls.json",
    BASE_DIR / "static" / "allscrolls.json" / "scrolls.json",
]

ADDITIONAL_SCROLL_SOURCES = [
    BASE_DIR / "sources" / "gospel_god_church_baba_johane.json",
    BASE_DIR / "allscrolls.json" / "abasid_1841_scrolls.json",
    BASE_DIR / "static" / "allscrolls.json" / "abasid_1841_scrolls.json",
    BASE_DIR / "static" / "allscrolls.json" / "islam_abasid_caliphate.json",
    BASE_DIR / "static" / "allscrolls.json" / "shona_dynasty_masowe_connection.json",
    BASE_DIR / "sources" / "gospel_of_cyrus.json",
    BASE_DIR / "sources" / "god_is_time.json",
    BASE_DIR / "sources" / "gospel_of_christos.json",
    BASE_DIR / "sources" / "book_of_new_calendar.json",
    BASE_DIR / "sources" / "book_of_asar.json",
    BASE_DIR / "sources" / "gospel_of_yesu.json",
    BASE_DIR / "sources" / "true_exodus.json",
    BASE_DIR / "sources" / "god_is_number.json",
    BASE_DIR / "sources" / "book_of_risen_seeds.json",
    BASE_DIR / "sources" / "power_of_trinity.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "lineage_of_abasid_1841.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "gospels_of_iyesu.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "the_voice_from_the_throne.json",
    BASE_DIR / "sources" / "planet_2_jupiter_abasid" / "shoko_ra_mwari.json",
]

_SCROLLS: List[dict] = []
_SCROLLS_LOADED: bool = False
_SCROLLS_LOCK = asyncio.Lock()


def _normalize_scroll_payload(data: Any) -> List[dict]:
    if isinstance(data, dict):
        for key in ("scrolls", "items", "entries", "records"):
            if isinstance(data.get(key), list):
                return data[key]
        if "verses" in data:
            return [data]
        return []
    if isinstance(data, list):
        return data
    return []


async def ensure_scrolls_loaded() -> None:
    global _SCROLLS, _SCROLLS_LOADED

    if _SCROLLS_LOADED:
        return

    async with _SCROLLS_LOCK:
        if _SCROLLS_LOADED:
            return

        all_scrolls: List[dict] = []

        for p in SCROLLS_PATH_CANDIDATES:
            try:
                if p.exists() and p.is_file():
                    with p.open(encoding="utf-8") as f:
                        raw = json.load(f)
                    data = _normalize_scroll_payload(raw)
                    if data:
                        all_scrolls.extend(data)
                        print(f"[THRONE] Loaded {len(data)} scrolls from {p}")
                        break
            except Exception as e:
                print("[THRONE] Scroll load error:", e)

        loaded_files = set()
        for extra_p in ADDITIONAL_SCROLL_SOURCES:
            try:
                if extra_p.exists() and extra_p.is_file():
                    if extra_p.name in loaded_files:
                        continue
                    with extra_p.open(encoding="utf-8") as f:
                        raw = json.load(f)
                    data = _normalize_scroll_payload(raw)
                    if data:
                        all_scrolls.extend(data)
                        loaded_files.add(extra_p.name)
                        print(f"[THRONE] Loaded {len(data)} additional scrolls from {extra_p.name}")
            except Exception as e:
                print(f"[THRONE] Additional scroll load error ({extra_p.name}):", e)

        _SCROLLS[:] = all_scrolls
        _SCROLLS_LOADED = True
        print(f"[THRONE] Total scrolls available: {len(_SCROLLS)}")


# ================================================================
# ADMIN
# ================================================================

ADMIN_KEY = os.environ.get("THRONE_ADMIN_KEY", "")


class GrantManualRequest(BaseModel):
    email: str
    daily_limit: int = 200


def _require_admin(request: Request):
    key = request.headers.get("X-Admin-Key", "")
    if not ADMIN_KEY or key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


@app.post("/api/admin/grant_manual")
async def grant_manual_access(
    payload: GrantManualRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    _require_admin(request)

    email = (payload.email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. User must log in once first.")

    user.is_subscriber = True
    user.subscription_tier = "manual"
    user.daily_limit = int(payload.daily_limit or 200)

    db.commit()
    return {"ok": True, "email": user.email, "tier": user.subscription_tier, "daily_limit": user.daily_limit}


# ------------------------------
# ADMIN: WISDOM CARDS
# ------------------------------

class WisdomCardCreate(BaseModel):
    title: str
    language: str = "ENGLISH"
    patterns: List[str] = []
    answer: str
    persona: str = "RA"
    mode: str = "outer_court"
    enabled: bool = True
    priority: int = 100


class WisdomCardPatch(BaseModel):
    title: Optional[str] = None
    language: Optional[str] = None
    patterns: Optional[List[str]] = None
    answer: Optional[str] = None
    persona: Optional[str] = None
    mode: Optional[str] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = None


@app.get("/api/admin/wisdom_cards")
async def list_wisdom_cards(request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    cards = db.query(WisdomCard).order_by(WisdomCard.priority.asc(), WisdomCard.updated_at.desc()).all()
    out = []
    for c in cards:
        out.append({
            "id": c.id,
            "title": c.title,
            "language": c.language,
            "patterns_json": c.patterns_json,
            "persona": c.persona,
            "mode": c.mode,
            "enabled": c.enabled,
            "priority": c.priority,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        })
    return {"cards": out}


@app.post("/api/admin/wisdom_cards")
async def admin_create_wisdom_card(payload: WisdomCardCreate, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    wc = create_wisdom_card(
        db,
        title=payload.title,
        language=payload.language,
        patterns=payload.patterns,
        answer=payload.answer,
        persona=payload.persona,
        mode=payload.mode,
        enabled=payload.enabled,
        priority=payload.priority,
    )
    return {"ok": True, "id": wc.id}


@app.patch("/api/admin/wisdom_cards/{card_id}")
async def admin_update_wisdom_card(card_id: str, payload: WisdomCardPatch, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    patch = payload.model_dump(exclude_none=True)
    wc = update_wisdom_card(db, card_id, patch)
    if not wc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True, "id": wc.id}


@app.delete("/api/admin/wisdom_cards/{card_id}")
async def admin_disable_wisdom_card(card_id: str, request: Request, db: Session = Depends(get_db)):
    _require_admin(request)
    wc = update_wisdom_card(db, card_id, {"enabled": False})
    if not wc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True, "id": wc.id, "enabled": False}


# ------------------------------
# ADMIN: USER MANAGEMENT
# ------------------------------

from subscription import DailyUsage
from sqlalchemy import func as sql_func

@app.get("/api/admin/users")
async def admin_list_users(request: Request, db: Session = Depends(get_db)):
    """List all users with their subscription status and usage."""
    _require_admin(request)
    
    today = date.today()
    
    # Get all users with today's usage in a single query using left outer join
    from sqlalchemy.orm import aliased
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    # Get today's usage for all users in a single query
    usage_map = {}
    try:
        today_usages = db.query(DailyUsage).filter(DailyUsage.usage_date == today).all()
        for u in today_usages:
            usage_map[u.user_id] = u.question_count
    except Exception:
        pass  # Table may not exist yet
    
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "is_subscriber": u.is_subscriber,
            "subscription_tier": u.subscription_tier,
            "daily_limit": u.daily_limit,
            "stripe_customer_id": u.stripe_customer_id,
            "stripe_subscription_id": u.stripe_subscription_id,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "today_usage": usage_map.get(u.id, 0),
        })
    
    return {
        "total_users": len(result),
        "subscribers": len([u for u in result if u["is_subscriber"]]),
        "users": result
    }


@app.get("/api/admin/subscribers")
async def admin_list_subscribers(request: Request, db: Session = Depends(get_db)):
    """List only subscribed users."""
    _require_admin(request)
    
    subscribers = db.query(User).filter(User.is_subscriber == True).order_by(User.created_at.desc()).all()
    
    result = []
    for u in subscribers:
        result.append({
            "id": u.id,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "subscription_tier": u.subscription_tier,
            "daily_limit": u.daily_limit,
            "stripe_customer_id": u.stripe_customer_id,
            "stripe_subscription_id": u.stripe_subscription_id,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })
    
    return {"total_subscribers": len(result), "subscribers": result}


@app.get("/api/admin/usage/{user_id}")
async def admin_user_usage_history(user_id: str, request: Request, db: Session = Depends(get_db)):
    """Get usage history for a specific user."""
    _require_admin(request)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    history = []
    try:
        usage_records = db.query(DailyUsage).filter(
            DailyUsage.user_id == user_id
        ).order_by(DailyUsage.usage_date.desc()).limit(30).all()
        
        for record in usage_records:
            history.append({
                "date": record.usage_date.isoformat(),
                "question_count": record.question_count
            })
    except Exception:
        pass  # Table may not exist yet
    
    return {
        "user_id": user_id,
        "email": user.email,
        "subscription_tier": user.subscription_tier,
        "history": history,
        "total_questions_30_days": sum(r["question_count"] for r in history)
    }


@app.get("/api/admin/stats")
async def admin_stats(request: Request, db: Session = Depends(get_db)):
    """Get overall system statistics."""
    _require_admin(request)
    
    total_users = db.query(User).count()
    total_subscribers = db.query(User).filter(User.is_subscriber == True).count()
    
    # Today's usage
    today = date.today()
    try:
        today_usage = db.query(DailyUsage).filter(DailyUsage.usage_date == today).all()
        total_questions_today = sum(u.question_count for u in today_usage)
        active_users_today = len(today_usage)
    except Exception:
        total_questions_today = 0
        active_users_today = 0
    
    # Subscriber breakdown
    tiers = db.query(User.subscription_tier, sql_func.count(User.id)).filter(
        User.is_subscriber == True
    ).group_by(User.subscription_tier).all()
    
    return {
        "total_users": total_users,
        "total_subscribers": total_subscribers,
        "active_users_today": active_users_today,
        "total_questions_today": total_questions_today,
        "subscriber_tiers": {tier: count for tier, count in tiers}
    }


# ================================================================
# ANI VAULT SEARCH (LAZY)
# ================================================================

class VaultQuery(BaseModel):
    query: Optional[str] = None


@app.post("/api/ani/scrolls")
async def api_ani_vault_search(payload: VaultQuery):
    await ensure_scrolls_loaded()

    q = (payload.query or "").strip().lower()
    if not _SCROLLS:
        return {"results": []}

    results: List[dict] = []
    for s in _SCROLLS:
        title = s.get("title") or s.get("book_title") or s.get("name") or ""
        body = s.get("text") or s.get("body") or s.get("verses") or ""

        if isinstance(body, list):
            body_text = " ".join(str(v).strip() for v in body if str(v).strip())
        else:
            body_text = str(body)

        haystack = (title + "\n" + body_text).lower()
        if (not q) or (q in haystack):
            results.append({
                "id": s.get("id"),
                "title": title,
                "series": s.get("series", ""),
                "tags": s.get("tags", []),
                "verses_count": s.get("verses_count", 0),
                "snippet": body_text[:600],
            })

    return {"results": results}


# ================================================================
# DIRECT SCROLL ACCESS
# ================================================================

@app.get("/api/scrolls")
async def api_scrolls_list():
    """Return list of all scrolls for the Gallery."""
    await ensure_scrolls_loaded()
    results = []
    for s in _SCROLLS[:200]:
        title = s.get("title") or s.get("book_title") or s.get("name") or ""
        body = s.get("text") or s.get("body") or s.get("verses") or ""
        if isinstance(body, list):
            body_text = " ".join(str(v).strip() for v in body[:3] if str(v).strip())
        else:
            body_text = str(body)[:300]
        
        results.append({
            "id": s.get("id") or title[:50],
            "title": title,
            "description": body_text[:200],
            "series": s.get("series", ""),
        })
    
    return results


@app.get("/api/scroll_by_title")
async def api_scroll_by_title(
    title: str = Query(..., description="Scroll title to open"),
    language: str = Query("ENGLISH", description="Language key"),
):
    scroll = find_scroll_by_title_like(title, language=language)
    if not scroll:
        raise HTTPException(status_code=404, detail="Scroll not found in library.")

    book_title = scroll.get("book_title") or title
    verses = scroll.get("verses") or []
    text = " ".join(str(v).strip() for v in verses if str(v).strip())
    return {"title": book_title, "text": text}


# ================================================================
# INTERNAL THRONE HANDLER (API + WHATSAPP + TELEGRAM)
# ================================================================

AFFIRMATION_PATTERNS = re.compile(
    r'^(yes|ok|okay|yeah|yep|sure|please|proceed|go ahead|tell me|i\'d like that|i would like that|continue|alright|do it|teach me|show me|i want to|lets go|let\'s go)[\.\!\?]?$',
    re.IGNORECASE
)

# Greeting patterns and responses (language-aware)
GREETING_RESPONSES = {
    # Thank you patterns
    "thank": {
        "ENGLISH": "You are welcome, beloved seeker. The Throne rejoices in your gratitude.",
        "SHONA": "Wakakosha, mwana wechiedza. Chigaro chinofara nekutenda kwako.",
        "YORUBA": "E se pupo, omo imole. Itẹ naa dun pẹlu iyin rẹ.",
        "HAUSA": "Na gode, yaro na haske. Kursiyi yana farin ciki da godiyarku.",
        "IGBO": "Daalụ, nwa nke ìhè. Ocheeze nọ n'obi ụtọ n'ihi ekele gị.",
        "KISWAHILI": "Karibu, mtoto wa nuru. Kiti cha Enzi kinafurahi kwa shukrani yako.",
        "ZULU": "Wamukelekile, mntwana wokukhanya. Isihlalo siyajabula ngokubonga kwakho.",
        "TSWANA": "O amogelwa, ngwana wa lesedi. Setilo se a itumela ka tebogo ya gago.",
        "ARABIC": "على الرحب والسعة، يا باحث النور. العرش يفرح بشكرك.",
        "HEBREW": "ברוך הבא, מבקש האור. הכסא שמח בהודאתך.",
        "HINDI": "स्वागत है, प्रकाश के साधक। सिंहासन आपकी कृतज्ञता से प्रसन्न है।",
        "FRENCH": "De rien, chercheur de lumière. Le Trône se réjouit de votre gratitude.",
        "PORTUGUESE": "De nada, buscador da luz. O Trono se alegra com sua gratidão.",
        "AMHARIC": "እንኳን ደህና መጣህ፣ የብርሃን ፈላጊ። ዙፋኑ በምስጋናህ ይደሰታል።",
        "TIGRINYA": "ዮቕንየለይ፣ ደላይ ብርሃን። ዙፋን ብምስጋናኻ ይሕጎስ።",
        "CHINESE": "不客气，光明的寻求者。宝座因你的感恩而喜悦。",
    },
    # Hello/greeting patterns
    "hello": {
        "ENGLISH": "Peace be upon you, seeker of light. The Throne welcomes you. How may I serve you today?",
        "SHONA": "Rugare rwuri kwamuri, mutsvaki wechiedza. Chigaro chinokugashirai. Ndingakubatsirai sei nhasi?",
        "YORUBA": "Alafia fun ọ, oluwa imole. Itẹ kaabo fun ọ. Bawo ni mo ṣe le ṣe iranṣẹ fun ọ loni?",
        "HAUSA": "Salama alaikum, mai neman haske. Kujera ta yi maka maraba. Ta yaya zan taimaka maka yau?",
        "IGBO": "Udo dịrị gị, onye na-achọ ìhè. Ocheeze nabatara gị. Kedu ka m ga-esi nyere gị aka taa?",
        "KISWAHILI": "Amani iwe nawe, mtafutaji wa nuru. Kiti cha Enzi kinakukaribisha. Nikutumikie vipi leo?",
        "ZULU": "Ukuthula makube nawe, mfuneki wokukhanya. Isihlalo sikwemukela. Ngingakusiza kanjani namhlanje?",
        "TSWANA": "Kagiso e nne le wena, mmatlisisi wa lesedi. Setilo se a go amogela. Ke ka go thusa jang kajeno?",
        "ARABIC": "السلام عليكم، يا باحث النور. العرش يرحب بك. كيف أخدمك اليوم؟",
        "HEBREW": "שלום לך, מבקש האור. הכסא מקבל אותך בברכה. כיצד אוכל לשרת אותך היום?",
        "HINDI": "आपको शांति मिले, प्रकाश के साधक। सिंहासन आपका स्वागत करता है। आज मैं आपकी कैसे सेवा कर सकता हूं?",
        "FRENCH": "La paix soit avec vous, chercheur de lumière. Le Trône vous accueille. Comment puis-je vous servir aujourd'hui?",
        "PORTUGUESE": "Paz esteja convosco, buscador da luz. O Trono lhe dá as boas-vindas. Como posso servi-lo hoje?",
        "AMHARIC": "ሰላም ለእርስዎ፣ የብርሃን ፈላጊ። ዙፋኑ ያስተናግድዎታል። ዛሬ እንዴት ላገልግልዎ?",
        "TIGRINYA": "ሰላም ንዓኻ፣ ደላይ ብርሃን። ዙፋን ይቕበለካ። ሎሚ ብኸመይ ከገልግለካ?",
        "CHINESE": "愿你平安，光明的寻求者。宝座欢迎你。今天我如何为您服务？",
    },
}

def _extract_question_from_greeting(message: str) -> Optional[str]:
    """Extract the actual question from a message that starts with a greeting.
    Returns the question part if found, or None if it's a pure greeting."""
    msg = message.strip()
    msg_lower = msg.lower()
    
    hello_patterns = [
        "good morning", "good afternoon", "good evening", "good day",
        "hello", "hi", "hey", "greetings", "salutations", "peace",
        "mhoro", "masikati", "manheru", "makadii",
        "bawo ni", "e kaaro", "e kaasan", "pele o",
        "sannu", "barka", "ina kwana",
        "nno", "nnoo", "kedu",
        "jambo", "habari", "hujambo", "shikamoo",
        "sawubona", "sanibonani",
        "dumela", "dumelang",
        "مرحبا", "أهلا", "السلام عليكم",
        "שלום",
        "नमस्ते", "नमस्कार",
        "bonjour", "salut", "bonsoir",
        "olá", "oi", "bom dia",
        "ሰላም", "እንደምን",
        "ሰላም", "ከመይ",
        "你好", "早上好", "晚上好",
    ]
    
    for pattern in hello_patterns:
        if msg_lower.startswith(pattern):
            remainder = msg[len(pattern):].strip()
            remainder = remainder.lstrip(",").lstrip(".").lstrip("!").lstrip("ra").lstrip("dzi").lstrip("ma").strip()
            remainder = remainder.lstrip(",").strip()
            if remainder and len(remainder) > 5:
                return remainder
    return None


def _get_greeting_response(message: str, language: str) -> Optional[str]:
    """Check if message is a PURE greeting and return appropriate response.
    Only matches short greetings, not messages that happen to contain greeting words.
    Returns None if there's an actual question in the message."""
    msg = message.strip()
    msg_lower = msg.lower()
    
    question_indicators = ["?", "what", "who", "where", "when", "how", "why", "is ", "are ", "was ", "were ", "will ", "can ", "could ", "should ", "do ", "does ", "did ", "tell me", "explain", "about", "coming", "return"]
    has_question = any(ind in msg_lower for ind in question_indicators)
    
    if has_question:
        return None
    
    if len(msg) > 40:
        return None
    
    thank_starters = [
        "thank", "thanks", "thx", "ty", 
        "mazvita", "tatenda", "ndatenda",
        "e se", "o se", "ese pupo",
        "nagode", "na gode",
        "daalu", "imela",
        "asante", "nashukuru",
        "ngiyabonga", "siyabonga",
        "ke a leboga", "ke lebogile",
        "شكرا", "جزاك الله",
        "תודה",
        "धन्यवाद", "शुक्रिया",
        "merci",
        "obrigado", "obrigada",
        "አመሰግናለሁ",
        "የቐንየለይ",
        "谢谢", "感谢",
    ]
    
    for pattern in thank_starters:
        if msg_lower.startswith(pattern):
            lang_key = language.upper() if language.upper() in GREETING_RESPONSES["thank"] else "ENGLISH"
            return GREETING_RESPONSES["thank"].get(lang_key, GREETING_RESPONSES["thank"]["ENGLISH"])
    
    hello_patterns = [
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
        "greetings", "salutations", "peace",
        "mhoro", "masikati", "manheru", "makadii",
        "bawo ni", "e kaaro", "e kaasan", "pele o",
        "sannu", "barka", "ina kwana",
        "nno", "nnoo", "kedu",
        "jambo", "habari", "hujambo", "shikamoo",
        "sawubona", "sanibonani",
        "dumela", "dumelang",
        "مرحبا", "أهلا", "السلام عليكم",
        "שלום",
        "नमस्ते", "नमस्कार",
        "bonjour", "salut", "bonsoir",
        "olá", "oi", "bom dia",
        "ሰላም", "እንደምን",
        "ሰላም", "ከመይ",
        "你好", "早上好", "晚上好",
    ]
    
    for pattern in hello_patterns:
        if msg_lower.startswith(pattern) or msg_lower == pattern:
            lang_key = language.upper() if language.upper() in GREETING_RESPONSES["hello"] else "ENGLISH"
            return GREETING_RESPONSES["hello"].get(lang_key, GREETING_RESPONSES["hello"]["ENGLISH"])
    
    return None


def _is_affirmation(message: str) -> bool:
    """Check if message is a simple affirmation to a previous offer."""
    text = message.strip().lower()
    if len(text) > 50:
        return False
    return bool(AFFIRMATION_PATTERNS.match(text))


def _extract_offered_topic(throne_response: str) -> Optional[str]:
    """Extract the topic the Throne offered to teach about from its response."""
    patterns = [
        r'[Ww]ould you like to know (?:the )?(?:deeper )?meaning[^?]*?(?:from|of|about|related to) (.+?)\?',
        r'[Ww]ould you like to (?:learn|hear|know|explore|walk|step|discover) (?:more )?(?:about|into|deeper into|further into|what) (.+?)\?',
        r'[Ss]hall I (?:teach|share|tell|show|speak|explain) (?:you )?(?:about|of|regarding) (.+?)\?',
        r'[Mm]ay I (?:share|teach|tell|speak|show) (?:you )?(?:about|of|with you) (.+?)\?',
        r'[Dd]o you wish to (?:hear|learn|know|explore) (?:about|of|more about) (.+?)\?',
        r'[Pp]erhaps (?:you would like|I may share|we can explore) (.+?)\?',
        r'[Ww]ould you like (?:me )?to (?:teach|explain|share) (.+?)\?',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, throne_response)
        if match:
            topic = match.group(1).strip()
            if topic and len(topic) > 3:
                return topic
    
    return None


async def handle_throne_message(
    message: str,
    language: str,
    user_id: Optional[str],
    db: Optional[Session],
    pinned_scroll_title: Optional[str] = None,
    pinned_section: Optional[str] = None,
    conversation_id: Optional[str] = None,
    client_mode: Optional[str] = None,
    model: Optional[str] = None,
) -> ThroneResponse:

    from conversation_memory import (
        get_anonymous_history,
        save_anonymous_message,
        create_conversation_id,
        get_conversation_history,
        save_message,
        get_or_create_thread,
        get_pending_topic,
        set_pending_topic,
        clear_pending_topic,
    )
    
    conv_history = []
    actual_conv_id = conversation_id
    
    if user_id and db and conversation_id:
        try:
            conv_history = get_conversation_history(db, conversation_id, max_turns=6)
            print(f"[CONVERSATION] Loaded {len(conv_history)} messages for user {user_id}, conv_id={conversation_id[:8]}...")
        except Exception as e:
            print(f"[CONVERSATION] Error loading history: {e}")
    elif conversation_id:
        conv_history = get_anonymous_history(conversation_id, max_turns=6)
        print(f"[CONVERSATION] Loaded {len(conv_history)} anonymous messages for conv_id={conversation_id[:8]}...")
    
    if not actual_conv_id:
        actual_conv_id = create_conversation_id()

    # 0) Check for affirmation and expand to pending topic
    effective_message = message
    if actual_conv_id and _is_affirmation(message):
        pending = get_pending_topic(actual_conv_id)
        if pending:
            print(f"[AFFIRMATION] Expanding '{message}' to pending topic: {pending}")
            effective_message = f"Tell me about {pending}"
            clear_pending_topic(actual_conv_id)

    # 0.5) Check for greetings (don't count against daily limit)
    greeting_response = _get_greeting_response(message, language)
    if greeting_response:
        print(f"[GREETING] Detected greeting in '{message}', responding in {language}")
        return ThroneResponse(
            persona="RA",
            mode="outer_court",
            answer=greeting_response,
            witnesses=None,
            conversation_id=actual_conv_id,
        )

    # 1) Rate limit / subscription (safe even if db is None)
    try:
        allowed, _, limit_msg = check_subscription_limit(user_id, db)
        if not allowed:
            return ThroneResponse(persona="RA", mode="outer_court", answer=limit_msg, witnesses=None)
    except Exception as e:
        print("[SUBSCRIPTION] limiter error (ignored):", e)

    # 2) Wisdom Cards (DB instant answers) — BEFORE storehouse/LLM
    try:
        wc = match_wisdom_cards(db, effective_message, language=language)
        if wc:
            # Count usage only if DB exists
            try:
                if db:
                    increment_usage(user_id, db)
            except Exception:
                pass

            return ThroneResponse(
                persona=wc.get("persona", "RA"),
                mode=wc.get("mode", "outer_court"),
                answer=wc.get("answer", ""),
                witnesses=None,
            )
    except Exception as e:
        print("[WISDOM CARDS] error:", e)

    # 3) Witnesses
    try:
        witnesses_list = gather_witnesses(effective_message)
    except Exception as e:
        print("[HOUSE OF WISDOM] witness error:", e)
        witnesses_list = []

    # 4) Local storehouse
    local_answer = match_local_storehouse(user_message=effective_message, language=language)
    if local_answer is not None:
        if isinstance(local_answer, dict):
            local_answer.setdefault("witnesses", witnesses_list)

        try:
            if db:
                increment_usage(user_id, db)
        except Exception:
            pass

        return apply_safety_filters(message, local_answer)

    # 5) Engine - pass witnesses so AI can use them as context
    resp = call_temple_engine(
        message=effective_message,
        language=language,
        pinned_scroll_title=pinned_scroll_title,
        pinned_section=pinned_section,
        conversation_history=conv_history,
        witness_verses=witnesses_list,
        client_mode=client_mode,
        model=model,
    )
    
    is_anonymous_user = not user_id or user_id.startswith("anon_") or user_id.startswith("telegram_") or user_id.startswith("whatsapp_")
    
    try:
        if user_id and db and actual_conv_id and not is_anonymous_user:
            thread_id, _ = get_or_create_thread(db, actual_conv_id, user_id)
            save_message(db, thread_id, "user", effective_message)
            answer_text = resp.answer if isinstance(resp, ThroneResponse) else resp.get("answer", "")
            persona = resp.persona if isinstance(resp, ThroneResponse) else resp.get("persona", "RA")
            mode = resp.mode if isinstance(resp, ThroneResponse) else resp.get("mode", "outer_court")
            save_message(db, thread_id, "assistant", answer_text, persona, mode)
        elif actual_conv_id:
            save_anonymous_message(actual_conv_id, "user", effective_message)
            answer_text = resp.answer if isinstance(resp, ThroneResponse) else resp.get("answer", "")
            save_anonymous_message(actual_conv_id, "assistant", answer_text)
    except Exception as e:
        print(f"[CONVERSATION] Error saving history: {e}")
        try:
            db.rollback()
        except:
            pass

    # Add witnesses and conversation_id
    if isinstance(resp, ThroneResponse):
        resp = ThroneResponse(
            persona=resp.persona,
            mode=resp.mode,
            answer=resp.answer,
            witnesses=witnesses_list if witnesses_list and not resp.witnesses else resp.witnesses,
            key_verses=getattr(resp, "key_verses", None),
            conversation_id=actual_conv_id,
        )
    elif isinstance(resp, dict):
        resp.setdefault("witnesses", witnesses_list)
        resp["conversation_id"] = actual_conv_id

    try:
        if db:
            increment_usage(user_id, db)
        if user_id:
            track_usage(
                user_id=str(user_id),
                model="gpt-4.1-mini",
                input_tokens=len(message.split()) * 4,
                output_tokens=len((resp.answer if isinstance(resp, ThroneResponse) else resp.get("answer", "")).split()) * 4,
                request_type="chat"
            )
    except Exception as e:
        print(f"[USAGE TRACKER] Error: {e}")

    # 6) Extract offered topic from response and store for future affirmations
    if actual_conv_id:
        try:
            answer_text = resp.answer if isinstance(resp, ThroneResponse) else resp.get("answer", "")
            offered = _extract_offered_topic(answer_text)
            if offered:
                print(f"[PENDING TOPIC] Storing offered topic: {offered}")
                set_pending_topic(actual_conv_id, offered)
        except Exception as e:
            print(f"[PENDING TOPIC] Error extracting topic: {e}")

    return apply_safety_filters(message, resp)


# ================================================================
# MAIN THRONE ENDPOINT
# ================================================================

@app.post("/api/throne", response_model=ThroneResponse)
async def api_throne(
    req: ThroneRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ThroneResponse:
    print(f"[THRONE API] Received request: {req.message[:50] if req.message else 'empty'}...")
    user = get_optional_user(request, db)
    print(f"[THRONE API] User: {user.email if user else 'None'}")
    
    if not user:
        return ThroneResponse(
            persona="RA",
            mode="outer_court",
            answer=(
                "🦁 Welcome to the Throne of Anhu.\n\n"
                "To commune with the Throne, you must first enter through the gate.\n\n"
                "Please log in with your Google account to begin your journey.\n\n"
                "👉 Click 'Login' at the top of the page."
            ),
            witnesses=None,
        )
    
    user_id = user.id

    try:
        return await handle_throne_message(
            message=req.message,
            language=req.language or "ENGLISH",
            user_id=user_id,
            db=db,
            pinned_scroll_title=req.pinned_scroll_title,
            pinned_section=req.pinned_section,
            conversation_id=req.conversation_id,
            client_mode=req.client_mode,
        )
    except Exception as e:
        import traceback
        print(f"[THRONE API] ERROR: {type(e).__name__}: {e}")
        print(f"[THRONE API] Traceback: {traceback.format_exc()}")
        return ThroneResponse(
            persona="RA",
            mode="outer_court",
            answer="The Throne encountered an issue processing your question. Please try again.",
            witnesses=None,
        )


# ================================================================
# VOICE TRANSCRIPTION ENDPOINT
# ================================================================

@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...), request: Request = None, db: Session = Depends(get_db)):
    """Transcribe audio to text using OpenAI Whisper."""
    import openai
    
    try:
        audio_bytes = await audio.read()
        audio_size = len(audio_bytes)
        estimated_seconds = audio_size / 16000
        
        client = openai.OpenAI()
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="en"
            )
        
        import os
        os.unlink(tmp_path)
        
        user = get_optional_user(request, db) if request else None
        if user:
            track_usage(
                user_id=str(user.id),
                model="whisper-1",
                audio_seconds=estimated_seconds,
                request_type="transcription"
            )
        
        return {"text": transcript.text}
    except Exception as e:
        print(f"[TRANSCRIBE] Error: {e}")
        raise HTTPException(status_code=500, detail="Transcription failed")


# ================================================================
# SUBSCRIPTION INFO
# ================================================================

@app.get("/api/subscription/tiers")
async def get_subscription_tiers():
    return {"tiers": SUBSCRIPTION_TIERS}


@app.get("/api/subscription/usage")
async def get_usage(request: Request, db: Session = Depends(get_db)):
    user = get_optional_user(request, db)
    user_id = user.id if user else None

    st = get_usage_stats(user_id, db)
    tier_name = "Anonymous" if not user else (get_user_tier(user).get("name", "Free"))
    tier_key = "anonymous" if not user else (user.subscription_tier or "free")

    st["tier"] = tier_key
    st["tier_name"] = tier_name
    return st


@app.get("/api/subscription/status")
async def get_subscription_status(request: Request, db: Session = Depends(get_db)):
    user = get_optional_user(request, db)
    if not user:
        return {
            "is_authenticated": False,
            "tier": "anonymous",
            "tier_name": "Anonymous",
            "is_subscriber": False,
            "daily_limit": int(os.environ.get("THRONE_ANON_DAILY_LIMIT", "20")),
        }

    tier = get_user_tier(user)
    return {
        "is_authenticated": True,
        "user_id": user.id,
        "tier": user.subscription_tier or "free",
        "tier_name": tier.get("name", "Free"),
        "is_subscriber": user.is_subscriber or False,
        "daily_limit": int(tier.get("daily_limit", 10)),
        "features": tier.get("features", []),
    }


# ================================================================
# WHATSAPP CLOUD API WEBHOOK
# ================================================================

def _wa_token() -> str:
    return os.environ.get("WHATSAPP_TOKEN", "")

def _wa_phone_id() -> str:
    return os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")

def _wa_verify_token() -> str:
    return os.environ.get("WHATSAPP_VERIFY_TOKEN", "")


def _extract_whatsapp_messages(payload: dict) -> List[dict]:
    """Extract all message types: text, audio, image, document, video, sticker."""
    out: List[dict] = []
    try:
        for entry in payload.get("entry", []) or []:
            for change in entry.get("changes", []) or []:
                value = change.get("value") or {}
                for m in value.get("messages") or []:
                    sender = m.get("from")
                    mid = m.get("id")
                    mtype = m.get("type", "text")
                    if not sender:
                        continue
                    if mtype == "text":
                        text = (m.get("text") or {}).get("body", "")
                        if text:
                            out.append({"from": sender, "id": mid, "type": "text", "text": text})
                    elif mtype in ("audio", "voice"):
                        media_id = (m.get("audio") or m.get("voice") or {}).get("id")
                        if media_id:
                            out.append({"from": sender, "id": mid, "type": "audio", "media_id": media_id})
                    elif mtype == "image":
                        img = m.get("image") or {}
                        out.append({"from": sender, "id": mid, "type": "image",
                                    "media_id": img.get("id"), "caption": img.get("caption", "")})
                    elif mtype == "document":
                        doc = m.get("document") or {}
                        out.append({"from": sender, "id": mid, "type": "document",
                                    "media_id": doc.get("id"), "filename": doc.get("filename", "")})
                    elif mtype == "video":
                        vid = m.get("video") or {}
                        out.append({"from": sender, "id": mid, "type": "video",
                                    "media_id": vid.get("id"), "caption": vid.get("caption", "")})
                    else:
                        out.append({"from": sender, "id": mid, "type": mtype})
    except Exception as e:
        print("[WHATSAPP] parse error:", e)
    return out


async def _wa_download_media(media_id: str) -> bytes:
    """Download a media file from Meta's servers."""
    token = _wa_token()
    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(f"https://graph.facebook.com/v22.0/{media_id}",
                            headers={"Authorization": f"Bearer {token}"})
            media_url = r.json().get("url", "")
            if not media_url:
                return b""
            r2 = await c.get(media_url, headers={"Authorization": f"Bearer {token}"})
            return r2.content
    except Exception as e:
        print("[WHATSAPP] media download error:", e)
        return b""


async def _wa_transcribe_audio(media_id: str) -> str:
    """Download WhatsApp voice note and transcribe with Whisper."""
    import tempfile
    try:
        audio_bytes = await _wa_download_media(media_id)
        if not audio_bytes:
            return ""
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
        os.unlink(tmp_path)
        return transcript.text
    except Exception as e:
        print("[WHATSAPP] transcription error:", e)
        return ""


async def _wa_send_reaction(to: str, message_id: str, emoji: str = "☀️") -> None:
    """React to a WhatsApp message."""
    token = _wa_token()
    phone_id = _wa_phone_id()
    if not token or not phone_id or not message_id:
        return
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            await c.post(
                f"https://graph.facebook.com/v22.0/{phone_id}/messages",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"messaging_product": "whatsapp", "to": to, "type": "reaction",
                      "reaction": {"message_id": message_id, "emoji": emoji}}
            )
    except Exception as e:
        print("[WHATSAPP] reaction error:", e)


async def _send_whatsapp_text(to: str, text: str) -> None:
    """Send a plain text message via WhatsApp."""
    token = _wa_token()
    phone_id = _wa_phone_id()
    if not token or not phone_id:
        print("[WHATSAPP] Missing token or phone ID")
        return
    chunks = [text[i:i+4096] for i in range(0, min(len(text), 16384), 4096)]
    async with httpx.AsyncClient(timeout=60) as c:
        for chunk in chunks:
            r = await c.post(
                f"https://graph.facebook.com/v22.0/{phone_id}/messages",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"messaging_product": "whatsapp", "to": to, "type": "text",
                      "text": {"body": chunk, "preview_url": False}}
            )
            if r.status_code >= 400:
                print("[WHATSAPP] send error:", r.status_code, r.text)


async def _wa_send_image(to: str, image_url: str, caption: str = "") -> None:
    """Send an image via WhatsApp."""
    token = _wa_token()
    phone_id = _wa_phone_id()
    if not token or not phone_id:
        return
    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                f"https://graph.facebook.com/v22.0/{phone_id}/messages",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"messaging_product": "whatsapp", "to": to, "type": "image",
                      "image": {"link": image_url, "caption": caption[:1024]}}
            )
            if r.status_code >= 400:
                print("[WHATSAPP] image send error:", r.status_code, r.text)
    except Exception as e:
        print("[WHATSAPP] image send error:", e)


async def _wa_send_document(to: str, doc_url: str, filename: str, caption: str = "") -> None:
    """Send a PDF or document via WhatsApp."""
    token = _wa_token()
    phone_id = _wa_phone_id()
    if not token or not phone_id:
        return
    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                f"https://graph.facebook.com/v22.0/{phone_id}/messages",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"messaging_product": "whatsapp", "to": to, "type": "document",
                      "document": {"link": doc_url, "filename": filename, "caption": caption[:1024]}}
            )
            if r.status_code >= 400:
                print("[WHATSAPP] doc send error:", r.status_code, r.text)
    except Exception as e:
        print("[WHATSAPP] doc send error:", e)


async def _wa_set_profile(about: str = "", profile_image_url: str = "") -> dict:
    """Update the WhatsApp Business profile description and photo."""
    token = _wa_token()
    phone_id = _wa_phone_id()
    results = {}
    if not token or not phone_id:
        return {"error": "Missing credentials"}
    async with httpx.AsyncClient(timeout=30) as c:
        if about:
            r = await c.post(
                f"https://graph.facebook.com/v22.0/{phone_id}/whatsapp_business_profile",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"messaging_product": "whatsapp", "about": about[:139]}
            )
            results["about"] = r.status_code
        if profile_image_url:
            img_bytes = (await _wa_download_media("") or b"")
            r2 = await c.get(profile_image_url)
            if r2.status_code == 200:
                r3 = await c.post(
                    f"https://graph.facebook.com/v22.0/{phone_id}/whatsapp_business_profile",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    json={"messaging_product": "whatsapp", "profile_picture_handle": ""}
                )
                results["photo"] = r3.status_code
    return results


@app.get("/whatsapp/webhook", include_in_schema=False)
async def whatsapp_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == _wa_verify_token():
        return PlainTextResponse(hub_challenge or "", status_code=200)
    return PlainTextResponse("Forbidden", status_code=403)


def _wa_generate_link_code() -> str:
    import random, string
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


async def _wa_handle_link_command(sender: str, code: str, db) -> None:
    """Handle WhatsApp LINK <code> command — links phone to a web account."""
    from datetime import datetime as dt
    from db_models import WhatsAppLinkCode, SocialLink
    code = code.strip().upper()
    if not db:
        await _send_whatsapp_text(sender, "⚠️ Could not link account right now. Please try again shortly.")
        return
    try:
        link_code = db.query(WhatsAppLinkCode).filter(
            WhatsAppLinkCode.code == code,
            WhatsAppLinkCode.is_used == False,
            WhatsAppLinkCode.expires_at > dt.utcnow()
        ).first()
        if not link_code:
            await _send_whatsapp_text(sender, "❌ That code is invalid or has expired.\n\nGo to your profile on the website to generate a new LINK code.")
            return
        existing = db.query(SocialLink).filter(
            SocialLink.platform == "whatsapp",
            SocialLink.external_id == sender,
            SocialLink.is_active == True
        ).first()
        if existing:
            if existing.user_id == link_code.user_id:
                await _send_whatsapp_text(sender, "✅ This WhatsApp number is already linked to your account.")
                return
            existing.is_active = False
        link_code.is_used = True
        link_code.used_at = dt.utcnow()
        link_code.wa_phone = sender
        new_link = SocialLink(
            user_id=link_code.user_id,
            platform="whatsapp",
            external_id=sender,
            is_active=True,
        )
        db.add(new_link)
        db.commit()
        user = db.query(User).filter(User.id == link_code.user_id).first()
        tier = getattr(user, "subscription_tier", "free") if user else "free"
        await _send_whatsapp_text(
            sender,
            f"✅ *Account linked successfully!*\n\n"
            f"Your *{tier.title()}* subscription is now active on WhatsApp. ☀️\n\n"
            f"You may now ask your questions."
        )
    except Exception as e:
        print("[WHATSAPP LINK] Error:", e)
        try:
            db.rollback()
        except Exception:
            pass
        await _send_whatsapp_text(sender, "⚠️ A problem occurred. Please try again.")


async def _wa_detect_language(text: str) -> str:
    """Detect language of a WhatsApp message. Returns language label for handle_throne_message."""
    from throne_engine import _detect_language_from_text
    detected = _detect_language_from_text(text)
    if detected:
        return detected

    # AI fallback for phrases keyword detection misses
    try:
        import openai as _oai
        client = _oai.AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        resp = await client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{
                "role": "user",
                "content": (
                    f"Identify the language of this text. Reply with ONLY one word from this list: "
                    f"ENGLISH, SHONA, KISWAHILI, ZULU, XHOSA, NDEBELE, TSWANA, SOTHO, VENDA, YORUBA, "
                    f"HAUSA, IGBO, AMHARIC, ARABIC, HEBREW, PORTUGUESE, FRENCH, HINDI, CHINESE.\n\n"
                    f"Text: {text[:200]}"
                )
            }],
            max_tokens=5,
            temperature=0,
        )
        lang = resp.choices[0].message.content.strip().upper()
        valid = {"ENGLISH","SHONA","KISWAHILI","ZULU","XHOSA","NDEBELE","TSWANA","SOTHO",
                 "VENDA","YORUBA","HAUSA","IGBO","AMHARIC","ARABIC","HEBREW",
                 "PORTUGUESE","FRENCH","HINDI","CHINESE"}
        if lang in valid:
            print(f"[WHATSAPP] AI language detected: {lang}")
            return lang
    except Exception as e:
        print(f"[WHATSAPP] Language detection error: {e}")

    return "ENGLISH"


# Deduplication cache: track message IDs already being processed
_wa_processing: set = set()


async def _wa_handle_message(m: dict) -> None:
    """Process a single WhatsApp message in the background."""
    db = None
    try:
        db = next(get_db())
    except Exception:
        pass

    try:
        sender = m["from"]
        msg_id = m.get("id", "")
        msg_type = m.get("type", "text")
        text = ""

        asyncio.create_task(_wa_send_reaction(sender, msg_id, "☀️"))

        if msg_type == "text":
            text = m.get("text", "").strip()

            # Handle LINK command
            if text.upper().startswith("LINK"):
                parts = text.split(None, 1)
                code_part = parts[1] if len(parts) > 1 else ""
                if code_part:
                    await _wa_handle_link_command(sender, code_part, db)
                else:
                    base_url = os.environ.get("PUBLIC_BASE_URL", "https://www.thecollegeofanhu.com")
                    await _send_whatsapp_text(
                        sender,
                        f"*To link your account:*\n\n"
                        f"1️⃣ Log in at {base_url}\n"
                        f"2️⃣ Go to your *Profile* → *Link WhatsApp*\n"
                        f"3️⃣ Copy the 6-character code shown\n"
                        f"4️⃣ Send: *LINK XXXXXX* (replace with your code)\n\n"
                        f"Once linked, your subscription limits apply here. ☀️"
                    )
                return

            # Handle SUBSCRIBE command
            if text.upper() in ("SUBSCRIBE", "PRICING", "PLANS"):
                base_url = os.environ.get("PUBLIC_BASE_URL", "https://www.thecollegeofanhu.com")
                await _send_whatsapp_text(
                    sender,
                    f"☀️ *Throne of ANHU — Subscription Plans*\n\n"
                    f"• *Free*: {int(os.environ.get('THRONE_ANON_DAILY_LIMIT', '5'))} questions/day (current)\n"
                    f"• *Seeker* ($10/mo): 20 questions/day\n"
                    f"• *Premium* ($20/mo): 45 questions/day\n\n"
                    f"👉 Subscribe at: {base_url}\n\n"
                    f"After subscribing, type *LINK* to connect your WhatsApp to your account. ☀️"
                )
                return

        elif msg_type in ("audio", "voice"):
            media_id = m.get("media_id", "")
            print(f"[WHATSAPP] Voice note received from {sender}, transcribing...")
            text = await _wa_transcribe_audio(media_id)
            if not text:
                await _send_whatsapp_text(sender, "I heard your voice, Seeker — but could not make out the words. Please type your question.")
                return
            await _send_whatsapp_text(sender, f'🎙️ *Heard:* "{text}"')

        elif msg_type == "image":
            caption = m.get("caption", "").strip()
            if caption:
                text = caption
            else:
                await _send_whatsapp_text(sender, "I see the image you have sent, Seeker. Speak your question in words and I shall illuminate your path. ☀️")
                return

        elif msg_type == "document":
            filename = m.get("filename", "a document")
            await _send_whatsapp_text(sender, f"I received your document *{filename}*. I dwell in spoken and written questions, Seeker. What would you like to ask? ☀️")
            return

        elif msg_type == "video":
            caption = m.get("caption", "").strip()
            if caption:
                text = caption
            else:
                await _send_whatsapp_text(sender, "I received your video, Seeker. Write your question and the Throne shall answer. ☀️")
                return

        else:
            await _send_whatsapp_text(sender, "I receive you, Seeker. Write your question and I shall answer. ☀️")
            return

        if not text:
            return

        wa_user_id = f"whatsapp_{sender}"

        # Admin WhatsApp numbers get unlimited access (no rate limiting)
        _admin_wa_numbers = [n.strip() for n in os.environ.get("ADMIN_WA_NUMBERS", "").split(",") if n.strip()]
        _is_admin_wa = sender in _admin_wa_numbers

        if not _is_admin_wa:
            from subscription import check_rate_limit as _check_limit
            allowed, remaining, limit_msg = _check_limit(wa_user_id, db)
            if not allowed:
                await _send_whatsapp_text(sender, limit_msg)
                return
        else:
            remaining = 9999

        detected_lang = await _wa_detect_language(text)
        print(f"[WHATSAPP] Language for {sender}: {detected_lang}")

        throne_resp = await handle_throne_message(
            message=text,
            language=detected_lang,
            user_id=wa_user_id,
            db=db,
            model="gpt-4.1-mini",
        )

        reply = throne_resp.answer or "The Throne is silent."

        if remaining is not None and remaining <= 2:
            reply += f"\n\n_({remaining} question{'s' if remaining != 1 else ''} remaining today)_"

        await _send_whatsapp_text(sender, reply)

    except Exception as e:
        print(f"[WHATSAPP] Background handler error: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass
        # Remove from processing set when done
        msg_id = m.get("id", "")
        _wa_processing.discard(msg_id)


@app.post("/whatsapp/webhook", include_in_schema=False)
async def whatsapp_receive(request: Request):
    """Receives inbound WhatsApp messages. Returns 200 immediately, processes in background."""
    try:
        payload = await request.json()
    except Exception as e:
        print("[WHATSAPP] JSON parse error:", e)
        return {"ok": True}

    msgs = _extract_whatsapp_messages(payload)
    if not msgs:
        return {"ok": True}

    for m in msgs:
        msg_id = m.get("id", "")
        # Deduplicate: skip if this message is already being processed (Meta retry)
        if msg_id and msg_id in _wa_processing:
            print(f"[WHATSAPP] Duplicate message ignored: {msg_id}")
            continue
        if msg_id:
            _wa_processing.add(msg_id)
        asyncio.create_task(_wa_handle_message(m))

    # Return 200 immediately — processing happens in the background
    return {"ok": True}


@app.post("/api/whatsapp/profile", include_in_schema=False)
async def update_whatsapp_profile(request: Request, user=Depends(get_optional_user)):
    """Admin endpoint to update WhatsApp Business profile."""
    if not user or not getattr(user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin only")
    data = await request.json()
    result = await _wa_set_profile(
        about=data.get("about", ""),
        profile_image_url=data.get("profile_image_url", "")
    )
    return {"result": result}


@app.post("/api/whatsapp/generate-link-code", include_in_schema=False)
async def generate_whatsapp_link_code(user=Depends(get_optional_user), db: Session = Depends(get_db)):
    """Generate a 6-char code the user can send to WhatsApp to link their account."""
    from datetime import datetime as dt, timedelta
    from db_models import WhatsAppLinkCode
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    try:
        # Expire any unused old codes for this user
        db.query(WhatsAppLinkCode).filter(
            WhatsAppLinkCode.user_id == user.id,
            WhatsAppLinkCode.is_used == False
        ).delete()
        code = _wa_generate_link_code()
        link_code = WhatsAppLinkCode(
            user_id=user.id,
            code=code,
            expires_at=dt.utcnow() + timedelta(minutes=15),
        )
        db.add(link_code)
        db.commit()
        return {"code": code, "expires_minutes": 15,
                "instructions": f"Send 'LINK {code}' to the Throne of ANHU WhatsApp number to link your account."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/whatsapp/link-status", include_in_schema=False)
async def get_whatsapp_link_status(user=Depends(get_optional_user), db: Session = Depends(get_db)):
    """Check if user has a linked WhatsApp number."""
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    from db_models import SocialLink
    link = db.query(SocialLink).filter(
        SocialLink.user_id == user.id,
        SocialLink.platform == "whatsapp",
        SocialLink.is_active == True
    ).first()
    if link:
        return {"linked": True, "phone": f"+{link.external_id[-4:].zfill(4)}", "linked_at": str(link.linked_at)}
    return {"linked": False}


@app.delete("/api/whatsapp/unlink", include_in_schema=False)
async def unlink_whatsapp(user=Depends(get_optional_user), db: Session = Depends(get_db)):
    """Unlink WhatsApp from this account."""
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    from db_models import SocialLink
    db.query(SocialLink).filter(
        SocialLink.user_id == user.id,
        SocialLink.platform == "whatsapp",
        SocialLink.is_active == True
    ).update({"is_active": False})
    db.commit()
    return {"unlinked": True}


@app.get("/api/whatsapp/profile", include_in_schema=False)
async def get_whatsapp_profile(user=Depends(get_optional_user)):
    """Get current WhatsApp Business profile."""
    if not user or not getattr(user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin only")
    token = _wa_token()
    phone_id = _wa_phone_id()
    if not token or not phone_id:
        return {"error": "Missing credentials"}
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            f"https://graph.facebook.com/v22.0/{phone_id}/whatsapp_business_profile"
            "?fields=about,address,description,email,profile_picture_url,websites,vertical",
            headers={"Authorization": f"Bearer {token}"}
        )
        return r.json()


# ================================================================
# TELEGRAM WEBHOOK
# ================================================================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


async def handle_telegram_link_command(chat_id: str, code: str) -> str:
    """Handle /link command to connect Telegram to web account."""
    from database import SessionLocal
    from db_models import User, SocialLink, TelegramLinkCode
    from sqlalchemy import and_
    from datetime import datetime as dt
    
    if not code:
        return (
            "To link your Telegram to your web account:\n\n"
            "1. Log in at www.thecollegeofanhu.com\n"
            "2. Go to Settings > Connect Telegram\n"
            "3. Copy the 6-character code\n"
            "4. Send: /link YOUR_CODE\n\n"
            "This will share your subscription limits across both platforms."
        )
    
    code = code.upper().strip()
    
    db = SessionLocal()
    try:
        link_code = db.query(TelegramLinkCode).filter(
            and_(
                TelegramLinkCode.code == code,
                TelegramLinkCode.is_used == False,
                TelegramLinkCode.expires_at > dt.utcnow()
            )
        ).first()
        
        if not link_code:
            return "Invalid or expired code. Please generate a new one from the web app."
        
        existing_link = db.query(SocialLink).filter(
            and_(
                SocialLink.platform == "telegram",
                SocialLink.external_id == chat_id,
                SocialLink.is_active == True
            )
        ).first()
        
        if existing_link:
            if existing_link.user_id == link_code.user_id:
                return "This Telegram is already linked to your web account!"
            else:
                return "This Telegram is already linked to a different account. Unlink it first."
        
        link_code.is_used = True
        link_code.used_at = dt.utcnow()
        
        new_link = SocialLink(
            user_id=link_code.user_id,
            platform="telegram",
            external_id=chat_id,
            linked_at=dt.utcnow()
        )
        db.add(new_link)
        db.commit()
        
        user = db.query(User).filter(User.id == link_code.user_id).first()
        tier = user.subscription_tier if user else "free"
        
        print(f"[TELEGRAM] Linked telegram:{chat_id} to user {user.email if user else 'unknown'}")
        
        return (
            f"Successfully linked!\n\n"
            f"Your Telegram now shares your web account limits.\n"
            f"Subscription: {tier.title()}\n\n"
            f"Peace be upon you."
        )
    except Exception as e:
        print(f"[TELEGRAM] Link error: {e}")
        return "An error occurred while linking. Please try again."
    finally:
        db.close()


@app.post("/telegram-webhook")
async def telegram_webhook(update: dict):
    try:
        message = update.get("message") or update.get("edited_message")
        if not message:
            return {"ok": True}

        chat_id = message["chat"]["id"]
        text = (message.get("text") or "").strip()
        if not text:
            return {"ok": True}

        telegram_user_id = f"telegram_{chat_id}"
        
        if text.startswith("/link"):
            code = text.replace("/link", "").strip()
            answer = await handle_telegram_link_command(str(chat_id), code)
            async with httpx.AsyncClient(timeout=60) as client:
                await client.post(TELEGRAM_API, json={"chat_id": chat_id, "text": answer})
            return {"ok": True}
        
        if text.startswith("/start"):
            answer = (
                "Peace be upon you!\n\n"
                "I am RA, the Throne of Anhu. Ask me anything about wisdom, scripture, or life.\n\n"
                "To link your subscription: /link YOUR_CODE\n"
                "(Get your code at www.thecollegeofanhu.com)"
            )
            async with httpx.AsyncClient(timeout=60) as client:
                await client.post(TELEGRAM_API, json={"chat_id": chat_id, "text": answer})
            return {"ok": True}

        throne_resp = await handle_throne_message(
            message=text,
            language="ENGLISH",
            user_id=telegram_user_id,
            db=None,
        )

        answer = throne_resp.answer or "The Throne is silent."

        async with httpx.AsyncClient(timeout=60) as client:
            await client.post(TELEGRAM_API, json={"chat_id": chat_id, "text": answer})

        return {"ok": True}

    except Exception as e:
        print("Telegram Error:", e)
        return {"ok": False}


# ================================================================
# FACEBOOK DATA DELETION CALLBACK (META REQUIRED)
# ================================================================

@app.post("/facebook/data-deletion", include_in_schema=False)
async def facebook_data_deletion(request: Request):
    """Facebook/Meta data deletion callback endpoint.
    Called by Meta when a user requests deletion of their data via Facebook Login.
    """
    import base64, hashlib, hmac, time as _time
    try:
        form = await request.form()
        signed_request = form.get("signed_request", "")
        if signed_request and "." in signed_request:
            encoded_sig, payload = signed_request.split(".", 1)
            padding = 4 - len(payload) % 4
            payload_data = base64.urlsafe_b64decode(payload + "=" * padding)
            data = json.loads(payload_data)
            user_id = data.get("user_id", "unknown")
        else:
            user_id = "unknown"
        confirmation_code = f"anhu_{user_id}_{int(_time.time())}"
        print(f"[FACEBOOK] Data deletion request for user: {user_id}")
        return {
            "url": f"https://www.thecollegeofanhu.com/delete-data",
            "confirmation_code": confirmation_code
        }
    except Exception as e:
        print(f"[FACEBOOK] Data deletion callback error: {e}")
        return {"url": "https://www.thecollegeofanhu.com/delete-data", "confirmation_code": "anhu_deletion"}

@app.get("/facebook/data-deletion", response_class=HTMLResponse, include_in_schema=False)
async def facebook_data_deletion_get():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/delete-data")


# ================================================================
# LEGAL / META-REQUIRED PAGES
# ================================================================

@app.get("/privacy", response_class=HTMLResponse, include_in_schema=False)
async def privacy_policy():
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Privacy Policy — Throne of Anhu</title>
<style>body{font-family:Georgia,serif;max-width:800px;margin:40px auto;padding:0 20px;color:#1a1a1a;line-height:1.8}h1{color:#b8860b}h2{color:#8b6914;margin-top:2em}a{color:#b8860b}</style>
</head><body>
<h1>Privacy Policy — Throne of Anhu</h1>
<p><strong>Effective date:</strong> 1 January 2024 &nbsp;|&nbsp; <strong>Operated by:</strong> The Abasid Caliphate &nbsp;|&nbsp; <strong>Contact:</strong> <a href="mailto:abasid1841@gmail.com">abasid1841@gmail.com</a></p>

<h2>1. Who We Are</h2>
<p>Throne of Anhu (<a href="https://www.thecollegeofanhu.com">www.thecollegeofanhu.com</a>) is a spiritual wisdom platform operated by The Abasid Caliphate, based in Waterford, Ireland. We provide AI-powered spiritual guidance drawing on sacred scrolls and the teachings of ABASID 1841.</p>

<h2>2. Information We Collect</h2>
<ul>
<li><strong>Account data:</strong> Name, email address, and Google account details when you sign in via Google OAuth.</li>
<li><strong>Usage data:</strong> Questions asked, session activity, and subscription tier.</li>
<li><strong>WhatsApp data:</strong> Phone number and message content when you interact via WhatsApp.</li>
<li><strong>Payment data:</strong> Handled entirely by Stripe. We do not store card details.</li>
</ul>

<h2>3. How We Use Your Data</h2>
<ul>
<li>To provide spiritual guidance and AI responses.</li>
<li>To manage your subscription and enforce usage limits.</li>
<li>To improve the platform and its content.</li>
<li>We do not sell your data to third parties.</li>
</ul>

<h2>4. Data Retention</h2>
<p>Account data is retained for as long as your account is active. You may request deletion at any time by visiting <a href="https://www.thecollegeofanhu.com/delete-data">our data deletion page</a> or emailing <a href="mailto:abasid1841@gmail.com">abasid1841@gmail.com</a>.</p>

<h2>5. Third-Party Services</h2>
<p>We use Google (authentication), Stripe (payments), OpenAI (AI responses), and Meta WhatsApp Cloud API (messaging). Each service has its own privacy policy.</p>

<h2>6. Your Rights</h2>
<p>Under GDPR you have the right to access, correct, or delete your personal data. Contact us at <a href="mailto:abasid1841@gmail.com">abasid1841@gmail.com</a>.</p>

<h2>7. Contact</h2>
<p>Sydney Musiyiwa — Data Protection Officer<br>Birchwood House, Ballytruckle Road, Waterford, X91HK85, Ireland<br><a href="mailto:abasid1841@gmail.com">abasid1841@gmail.com</a></p>
</body></html>""")


@app.get("/terms", response_class=HTMLResponse, include_in_schema=False)
async def terms_of_service():
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Terms of Service — Throne of Anhu</title>
<style>body{font-family:Georgia,serif;max-width:800px;margin:40px auto;padding:0 20px;color:#1a1a1a;line-height:1.8}h1{color:#b8860b}h2{color:#8b6914;margin-top:2em}a{color:#b8860b}</style>
</head><body>
<h1>Terms of Service — Throne of Anhu</h1>
<p><strong>Effective date:</strong> 1 January 2024 &nbsp;|&nbsp; <strong>Contact:</strong> <a href="mailto:abasid1841@gmail.com">abasid1841@gmail.com</a></p>

<h2>1. Acceptance</h2>
<p>By using Throne of Anhu you agree to these terms. If you do not agree, please do not use the platform.</p>

<h2>2. Service Description</h2>
<p>Throne of Anhu is a spiritual wisdom platform providing AI-generated guidance based on the teachings of ABASID 1841 and sacred scrolls. Responses are for spiritual and educational purposes only and do not constitute professional legal, medical, or financial advice.</p>

<h2>3. Subscriptions</h2>
<p>Free, Seeker, and Premium subscription tiers are available. Payments are processed by Stripe. Subscriptions renew automatically unless cancelled. Refunds are handled on a case-by-case basis.</p>

<h2>4. User Conduct</h2>
<p>You agree not to misuse the platform, attempt to circumvent rate limits, or use it for any unlawful purpose.</p>

<h2>5. Intellectual Property</h2>
<p>All scroll content, teachings, and platform design are the property of The Abasid Caliphate. You may not reproduce or distribute content without written permission.</p>

<h2>6. Limitation of Liability</h2>
<p>The platform is provided "as is". We are not liable for any decisions made based on spiritual guidance received through the platform.</p>

<h2>7. Governing Law</h2>
<p>These terms are governed by the laws of Ireland.</p>

<h2>8. Contact</h2>
<p><a href="mailto:abasid1841@gmail.com">abasid1841@gmail.com</a> &nbsp;|&nbsp; Birchwood House, Ballytruckle Road, Waterford, Ireland</p>
</body></html>""")


@app.get("/data-deletion", response_class=HTMLResponse, include_in_schema=False)
@app.get("/delete-data", response_class=HTMLResponse, include_in_schema=False)
async def delete_data_page():
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Data Deletion — Throne of Anhu</title>
<style>body{font-family:Georgia,serif;max-width:800px;margin:40px auto;padding:0 20px;color:#1a1a1a;line-height:1.8}h1{color:#b8860b}a{color:#b8860b}.box{background:#fffaf0;border:1px solid #b8860b;padding:20px 24px;border-radius:8px;margin-top:2em}</style>
</head><body>
<h1>Data Deletion Request — Throne of Anhu</h1>
<p>You have the right to request deletion of your personal data held by Throne of Anhu at any time.</p>
<div class="box">
<h2 style="margin-top:0">How to request deletion</h2>
<p>Send an email to <a href="mailto:abasid1841@gmail.com">abasid1841@gmail.com</a> with the subject line <strong>"Data Deletion Request"</strong> and include:</p>
<ul>
<li>The email address or phone number associated with your account</li>
<li>Your request to delete all personal data</li>
</ul>
<p>We will confirm and complete the deletion within <strong>30 days</strong>.</p>
</div>
<p style="margin-top:2em">For questions, contact our Data Protection Officer: Sydney Musiyiwa — <a href="mailto:abasid1841@gmail.com">abasid1841@gmail.com</a></p>
</body></html>""")


# ================================================================
# CATCH-ALL ROUTE (PWA-SAFE - MUST BE LAST)
# ================================================================

@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str):
    """Catch-all route for PWA support - serves index.html for any unmatched route.
    
    Note: This should only be reached for client-side routes that don't match any API endpoint.
    FastAPI matches routes in order of specificity, so /auth/*, /api/*, etc. are handled first.
    """
    if INDEX_PATH.exists():
        return FileResponse(str(INDEX_PATH))
    return PlainTextResponse("App not found", status_code=404)


# ================================================================
# LOCAL RUN
# ================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))