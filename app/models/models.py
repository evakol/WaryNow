import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))), "warynow.db")

def get_connection():
    """Επιστροφή σ΄θνδεσης με βάση δεδομένων"""
    return sqlite3.connect(DATABASE_PATH)

def init_db():
    """Αν δεν υπάρχουν οι πίνακες, θα δημιουργηθούν."""
    conn = get_connection()
    cursor = conn.cursor()

    # NewsSource: UC6
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    """)

    # RawReport: UC6/UC7
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            location TEXT,
            latitude REAL,
            longitude REAL,
            source TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    """)

    # Conflict: UC7
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conflicts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            latitude REAL,
            longitude REAL,
            status TEXT DEFAULT 'active',
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # Coordinate: UC7
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coordinates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conflict_id INTEGER NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    """)

    # ErrorLog: UC6
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS error_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            error_message TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()