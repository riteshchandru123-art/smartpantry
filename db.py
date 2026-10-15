import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = "pantry.db"

@contextmanager
def get_db(db_path: str = DEFAULT_DB_PATH):
    """Context manager for SQLite connection that guarantees connection is closed on exit."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db(db_path: str = DEFAULT_DB_PATH):
    """Initializes the database schema if it doesn't already exist."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pantry_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity TEXT NOT NULL,
                category TEXT DEFAULT 'Other',
                expiry_date TEXT,
                added_at TEXT NOT NULL,
                notes TEXT DEFAULT ''
            )
        """)
        conn.commit()

def add_item(
    name: str,
    quantity: str,
    category: str = "Other",
    expiry_date: Optional[str] = None,
    notes: str = "",
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """Adds a new item to the pantry inventory."""
    added_at = datetime.now().strftime("%Y-%m-%d")
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pantry_items (name, quantity, category, expiry_date, added_at, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name.strip().title(), quantity.strip(), category.strip(), expiry_date, added_at, notes))
        conn.commit()
        return cursor.lastrowid

def get_all_items(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves all items currently in the pantry."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pantry_items ORDER BY expiry_date ASC, name ASC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_expiring_soon_items(days_ahead: int = 3, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves items expiring within the specified number of days or already expired."""
    target_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM pantry_items 
            WHERE expiry_date IS NOT NULL AND expiry_date != '' AND expiry_date <= ?
            ORDER BY expiry_date ASC
        """, (target_date,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def delete_item(item_id: int, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Deletes an item from the pantry."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pantry_items WHERE id = ?", (item_id,))
        conn.commit()
        return cursor.rowcount > 0

def clear_all_items(db_path: str = DEFAULT_DB_PATH):
    """Clears all pantry items."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pantry_items")
        conn.commit()
