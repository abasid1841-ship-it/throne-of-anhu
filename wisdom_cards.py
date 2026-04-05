import json
import re
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from db_models import WisdomCard


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

    # Pull enabled cards for language + fallback ENGLISH
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
                # bad regex - ignore
                continue

    return None


# -------------------------
# Admin helpers
# -------------------------

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
    # validate JSON serializable patterns
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