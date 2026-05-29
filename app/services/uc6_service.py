#  UC6 - Fetch Conflict Data
# Controls: SchedulerController, APIConnector, KeywordFilter, DataNormalizer

import requests
from datetime import datetime
from app.models.models import get_connection
import config

# KeywordFilter
def filter_keywords(results):
    """
    Φιλτράρει αποτελέσματα βάσει conflict keywords.
    Εναλλακτική Ροή: αν δεν βρεθεί match επιστρέφει κενή λίστα.
    """
    filtered = []
    for item in results:
        text = (item.get("title", "") + " " +
                item.get("description", "")).lower()
        if any(kw in text for kw in config.CONFLICT_KEYWORDS):
            filtered.append(item)
    return filtered

# DataNormalizer
def normalize_and_save(items, source_name):
    """
    Κανονικοποίηση και αποθήκευση δεδομένων ως RawReport.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for item in items:
            cursor.execute("""
                INSERT INTO raw_reports 
                (title, description, location, latitude, 
                longitude, source, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
            """, (
                item.get("title", "No title"),
                item.get("description", ""),
                item.get("location", ""),
                item.get("latitude"),
                item.get("longitude"),
                source_name,
                datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# APIConnector 
def fetch_data(source_name, source_url):
    """
    HTTP request στο GDELT API.
    Εναλλακτική ροή: αν αποτύχει καταγράφει στο ErrorLog.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        params = {
            "query": "conflict war attack",
            "mode": "artlist",
            "maxrecords": 10,
            "format": "json"
        }
        response = requests.get(
            config.GDELT_API_URL,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])

        # Filter keywords
        filtered = filter_keywords(articles)

        # Εναλλακτική ροή: κανένα match
        if not filtered:
            return

        # save
        normalize_and_save(filtered, source_name)

    except Exception as e:
        # Εναλλακτική ροή: καταγραφή σφάλματος
        cursor.execute("""
            INSERT INTO error_logs 
            (source, error_message, created_at)
            VALUES (?, ?, ?)
        """, (
            source_name,
            str(e),
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
    finally:
        conn.close()

# SchedulerController 
def activate():
    """
    μέθοδος UC6.
    Διαβάζει ενεργές NewsSource και καλεί APIConnector.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT name, url FROM news_sources 
            WHERE is_active = 1
        """)
        sources = cursor.fetchall()
        for source in sources:
            fetch_data(source[0], source[1])
    finally:
        conn.close()