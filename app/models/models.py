import sqlite3
import os

# Υπολογισμός του μονοπατιού για το αρχείο warynow.db
DATABASE_PATH = os.path.join(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))), "warynow.db")

def get_connection():
    """Επιστροφή σύνδεσης με τη βάση δεδομένων SQLite3"""
    return sqlite3.connect(DATABASE_PATH)

def init_db():
    """Αν δεν υπάρχουν οι πίνακες, θα δημιουργηθούν με καθαρό SQLite3."""
    conn = get_connection()
    cursor = conn.cursor()

    # === ΠΙΝΑΚΕΣ ΒΑΪΟΥ (UC6 & UC7) ===
    
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

    # === ΠΙΝΑΚΕΣ ΦΕΡΙΤ (UC8 & UC9) ===

    # AlertZone: UC8
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subscriber_id INTEGER NOT NULL,
            center_lat REAL NOT NULL,
            center_lng REAL NOT NULL,
            radius_km REAL NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT,
            country TEXT
        )
    """)

    # Notification: UC8
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subscriber_id INTEGER NOT NULL,
            conflict_id INTEGER NOT NULL,
            zone_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    # Infrastructure: UC9
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS infrastructures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            country TEXT,
            status TEXT DEFAULT 'operational'
        )
    """)

    conn.commit()
    conn.close()