"""
Usage Tracker for OpenAI API costs per user.
Tracks tokens used, questions asked, and estimated costs.
"""
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

PRICING = {
    "gpt-4.1-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "text-embedding-3-small": {"input": 0.00002, "output": 0},
    "whisper-1": {"per_minute": 0.006},
}

Base = declarative_base()

class UsageRecord(Base):
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    model = Column(String(50), nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    audio_seconds = Column(Float, default=0)
    estimated_cost = Column(Float, default=0)
    request_type = Column(String(50), default="chat")
    
_engine = None
_Session = None

def _get_session():
    global _engine, _Session
    if _engine is None and DATABASE_URL:
        _engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(_engine)
        _Session = sessionmaker(bind=_engine)
        print("[USAGE TRACKER] Database initialized")
    return _Session() if _Session else None

def track_usage(
    user_id: str,
    model: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    audio_seconds: float = 0,
    request_type: str = "chat"
) -> Optional[float]:
    """
    Track API usage and return estimated cost.
    """
    pricing = PRICING.get(model, PRICING.get("gpt-4o-mini"))
    
    if audio_seconds > 0:
        cost = (audio_seconds / 60) * pricing.get("per_minute", 0.006)
    else:
        input_cost = (input_tokens / 1000) * pricing.get("input", 0.00015)
        output_cost = (output_tokens / 1000) * pricing.get("output", 0.0006)
        cost = input_cost + output_cost
    
    session = _get_session()
    if session:
        try:
            record = UsageRecord(
                user_id=str(user_id),
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                audio_seconds=audio_seconds,
                estimated_cost=cost,
                request_type=request_type
            )
            session.add(record)
            session.commit()
        except Exception as e:
            print(f"[USAGE TRACKER] Error saving: {e}")
            session.rollback()
        finally:
            session.close()
    
    return cost

def get_user_usage(user_id: str, days: int = 30) -> Dict:
    """
    Get usage statistics for a user over the past N days.
    """
    session = _get_session()
    if not session:
        return {"error": "Database not available"}
    
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        records = session.query(UsageRecord).filter(
            UsageRecord.user_id == str(user_id),
            UsageRecord.timestamp >= cutoff
        ).all()
        
        total_cost = sum(r.estimated_cost for r in records)
        total_questions = len(records)
        total_input_tokens = sum(r.input_tokens for r in records)
        total_output_tokens = sum(r.output_tokens for r in records)
        total_audio_seconds = sum(r.audio_seconds for r in records)
        
        by_model = {}
        for r in records:
            if r.model not in by_model:
                by_model[r.model] = {"count": 0, "cost": 0}
            by_model[r.model]["count"] += 1
            by_model[r.model]["cost"] += r.estimated_cost
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_questions": total_questions,
            "total_cost_usd": round(total_cost, 4),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_audio_seconds": round(total_audio_seconds, 1),
            "avg_cost_per_question": round(total_cost / total_questions, 6) if total_questions > 0 else 0,
            "by_model": by_model
        }
    except Exception as e:
        print(f"[USAGE TRACKER] Error getting usage: {e}")
        return {"error": str(e)}
    finally:
        session.close()

def get_all_users_usage(days: int = 30) -> List[Dict]:
    """
    Get usage statistics for all users (admin view).
    """
    session = _get_session()
    if not session:
        return []
    
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        from sqlalchemy import func
        
        results = session.query(
            UsageRecord.user_id,
            func.count(UsageRecord.id).label("total_questions"),
            func.sum(UsageRecord.estimated_cost).label("total_cost"),
            func.sum(UsageRecord.input_tokens).label("input_tokens"),
            func.sum(UsageRecord.output_tokens).label("output_tokens")
        ).filter(
            UsageRecord.timestamp >= cutoff
        ).group_by(UsageRecord.user_id).all()
        
        users = []
        for r in results:
            users.append({
                "user_id": r.user_id,
                "total_questions": r.total_questions,
                "total_cost_usd": round(float(r.total_cost or 0), 4),
                "input_tokens": r.input_tokens or 0,
                "output_tokens": r.output_tokens or 0
            })
        
        users.sort(key=lambda x: x["total_cost_usd"], reverse=True)
        return users
    except Exception as e:
        print(f"[USAGE TRACKER] Error: {e}")
        return []
    finally:
        session.close()

def get_total_usage(days: int = 30) -> Dict:
    """
    Get total platform usage statistics.
    """
    session = _get_session()
    if not session:
        return {"error": "Database not available"}
    
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        from sqlalchemy import func
        
        result = session.query(
            func.count(UsageRecord.id).label("total_requests"),
            func.sum(UsageRecord.estimated_cost).label("total_cost"),
            func.sum(UsageRecord.input_tokens).label("input_tokens"),
            func.sum(UsageRecord.output_tokens).label("output_tokens"),
            func.count(func.distinct(UsageRecord.user_id)).label("unique_users")
        ).filter(UsageRecord.timestamp >= cutoff).first()
        
        return {
            "period_days": days,
            "total_requests": result.total_requests or 0,
            "total_cost_usd": round(float(result.total_cost or 0), 2),
            "total_input_tokens": result.input_tokens or 0,
            "total_output_tokens": result.output_tokens or 0,
            "unique_users": result.unique_users or 0,
            "avg_cost_per_user": round(float(result.total_cost or 0) / max(result.unique_users or 1, 1), 4)
        }
    except Exception as e:
        print(f"[USAGE TRACKER] Error: {e}")
        return {"error": str(e)}
    finally:
        session.close()
