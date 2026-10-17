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
    """Initializes the database schema and performs auto-migrations for new columns."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        
        # 1. Pantry Items Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pantry_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity TEXT NOT NULL,
                category TEXT DEFAULT 'Other',
                expiry_date TEXT,
                added_at TEXT NOT NULL,
                notes TEXT DEFAULT '',
                price REAL DEFAULT 0.0,
                calories INTEGER DEFAULT 0,
                protein_g REAL DEFAULT 0.0,
                carbs_g REAL DEFAULT 0.0,
                fat_g REAL DEFAULT 0.0
            )
        """)

        # Auto-migration: check if new columns exist, add if missing
        cursor.execute("PRAGMA table_info(pantry_items)")
        columns = [row["name"] for row in cursor.fetchall()]
        
        new_cols = {
            "price": "REAL DEFAULT 0.0",
            "calories": "INTEGER DEFAULT 0",
            "protein_g": "REAL DEFAULT 0.0",
            "carbs_g": "REAL DEFAULT 0.0",
            "fat_g": "REAL DEFAULT 0.0"
        }
        for col_name, col_type in new_cols.items():
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE pantry_items ADD COLUMN {col_name} {col_type}")

        # 2. Meal Logs Table (for daily macro tracking and money saved)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meal_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_title TEXT NOT NULL,
                cooked_at TEXT NOT NULL,
                calories INTEGER DEFAULT 0,
                protein_g REAL DEFAULT 0.0,
                carbs_g REAL DEFAULT 0.0,
                fat_g REAL DEFAULT 0.0,
                cost REAL DEFAULT 0.0,
                takeout_savings REAL DEFAULT 0.0
            )
        """)
        conn.commit()

def add_item(
    name: str,
    quantity: str,
    category: str = "Other",
    expiry_date: Optional[str] = None,
    notes: str = "",
    price: float = 0.0,
    calories: int = 0,
    protein_g: float = 0.0,
    carbs_g: float = 0.0,
    fat_g: float = 0.0,
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """Adds a new item to the pantry inventory with nutrition and price data."""
    added_at = datetime.now().strftime("%Y-%m-%d")
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pantry_items (
                name, quantity, category, expiry_date, added_at, notes,
                price, calories, protein_g, carbs_g, fat_g
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name.strip().title(), quantity.strip(), category.strip(), expiry_date, added_at, notes,
            float(price or 0.0), int(calories or 0), float(protein_g or 0.0), float(carbs_g or 0.0), float(fat_g or 0.0)
        ))
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

def get_total_inventory_value(db_path: str = DEFAULT_DB_PATH) -> float:
    """Calculates total grocery value sitting in the pantry."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(price) as total_val FROM pantry_items")
        row = cursor.fetchone()
        return round(float(row["total_val"] or 0.0), 2)

def log_meal(
    recipe_title: str,
    calories: int,
    protein_g: float,
    carbs_g: float,
    fat_g: float,
    cost: float,
    takeout_savings: float,
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """Logs a cooked meal for daily macro and money-saved tracking."""
    cooked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO meal_logs (recipe_title, cooked_at, calories, protein_g, carbs_g, fat_g, cost, takeout_savings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (recipe_title, cooked_at, calories, protein_g, carbs_g, fat_g, cost, takeout_savings))
        conn.commit()
        return cursor.lastrowid

def get_today_nutrition_summary(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Returns total calories, macros, and money saved logged today."""
    today_prefix = datetime.now().strftime("%Y-%m-%d") + "%"
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as meals_count,
                SUM(calories) as total_calories,
                SUM(protein_g) as total_protein,
                SUM(carbs_g) as total_carbs,
                SUM(fat_g) as total_fat,
                SUM(cost) as total_cost,
                SUM(takeout_savings) as total_savings
            FROM meal_logs
            WHERE cooked_at LIKE ?
        """, (today_prefix,))
        row = cursor.fetchone()
        return {
            "meals_count": row["meals_count"] or 0,
            "calories": row["total_calories"] or 0,
            "protein_g": round(float(row["total_protein"] or 0.0), 1),
            "carbs_g": round(float(row["total_carbs"] or 0.0), 1),
            "fat_g": round(float(row["total_fat"] or 0.0), 1),
            "cost": round(float(row["total_cost"] or 0.0), 2),
            "savings": round(float(row["total_savings"] or 0.0), 2),
        }
