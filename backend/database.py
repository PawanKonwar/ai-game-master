"""SQLite persistence for game states (save/load)."""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "game_states.db"


def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the game_states table if it does not exist."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS game_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                story_log TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_game(session_name: str, story_log: str) -> int:
    """Insert a game state and return its id."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO game_states (session_name, story_log, timestamp) VALUES (?, ?, ?)",
            (session_name, story_log, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def load_game(session_id: int) -> dict | None:
    """Return a single game state by id, or None if not found."""
    conn = get_connection()
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, session_name, story_log, timestamp FROM game_states WHERE id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "session_name": row["session_name"],
            "story_log": row["story_log"],
            "timestamp": row["timestamp"],
        }
    finally:
        conn.close()


def list_games():
    """Return all saved game states (id, session_name, timestamp) ordered by newest first."""
    conn = get_connection()
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, session_name, timestamp FROM game_states ORDER BY timestamp DESC"
        ).fetchall()
        return [
            {"id": r["id"], "session_name": r["session_name"], "timestamp": r["timestamp"]}
            for r in rows
        ]
    finally:
        conn.close()
