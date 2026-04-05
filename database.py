"""Database connection and session management for Throne of Anhu."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get("DATABASE_URL")

# Fallback for local/dev (Replit can run fine on SQLite if DATABASE_URL isn't set)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./throne.db"

# SQLite needs special connect args
_connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

_db_initialized = False


def _run_migrations():
    """Run any pending schema migrations."""
    from sqlalchemy import text, inspect
    
    inspector = inspect(engine)
    
    if "masowe_chat_messages" in inspector.get_table_names():
        existing_cols = {col["name"] for col in inspector.get_columns("masowe_chat_messages")}
        
        with engine.connect() as conn:
            if "reply_to_id" not in existing_cols:
                try:
                    conn.execute(text("ALTER TABLE masowe_chat_messages ADD COLUMN reply_to_id VARCHAR"))
                    conn.commit()
                    print("[THRONE] Added reply_to_id column")
                except Exception as e:
                    print(f"[THRONE] Migration reply_to_id: {e}")
            
            if "reply_to_author" not in existing_cols:
                try:
                    conn.execute(text("ALTER TABLE masowe_chat_messages ADD COLUMN reply_to_author VARCHAR"))
                    conn.commit()
                    print("[THRONE] Added reply_to_author column")
                except Exception as e:
                    print(f"[THRONE] Migration reply_to_author: {e}")
            
            if "reply_to_preview" not in existing_cols:
                try:
                    conn.execute(text("ALTER TABLE masowe_chat_messages ADD COLUMN reply_to_preview VARCHAR"))
                    conn.commit()
                    print("[THRONE] Added reply_to_preview column")
                except Exception as e:
                    print(f"[THRONE] Migration reply_to_preview: {e}")


def init_db():
    """Initialize database tables (idempotent)."""
    global _db_initialized
    if _db_initialized:
        return

    # IMPORTANT: import ALL models so their tables are registered on Base.metadata
    from db_models import User, ChatThread, ChatMessage, WisdomCard  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _run_migrations()
    _db_initialized = True
    print("[THRONE] Database tables initialized")


def get_db():
    """Dependency that provides a database session with lazy init."""
    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()