import os
import sqlite3
from datetime import datetime, timezone
from src.config import DB_PATH, logger

def init_db():
    # Ensure parent directory of DB exists
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # User style table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_styles (
            user_id INTEGER PRIMARY KEY,
            style_prompt TEXT NOT NULL
        )
    """)
    
    # Processed content table for idempotency
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_content (
            user_id INTEGER,
            source_identifier TEXT,
            style_prompt TEXT,
            timestamp TEXT NOT NULL,
            PRIMARY KEY (user_id, source_identifier, style_prompt)
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")

def get_user_style(user_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT style_prompt FROM user_styles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""

def set_user_style(user_id: int, style_prompt: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO user_styles (user_id, style_prompt)
        VALUES (?, ?)
    """, (user_id, style_prompt))
    conn.commit()
    conn.close()
    logger.info(f"Updated style memory for user {user_id}: {style_prompt[:50]}...")

def is_duplicate(user_id: int, source_identifier: str, style_prompt: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM processed_content
        WHERE user_id = ? AND source_identifier = ? AND style_prompt = ?
    """, (user_id, source_identifier, style_prompt))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def mark_processed(user_id: int, source_identifier: str, style_prompt: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT OR REPLACE INTO processed_content (user_id, source_identifier, style_prompt, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, source_identifier, style_prompt, timestamp))
    conn.commit()
    conn.close()
    logger.info(f"Marked processed: user={user_id}, id={source_identifier[:50]}, style={style_prompt[:30]}")
