# UC7 - Conflict Merging
# Controls: MergeController, GeoProximityChecker, ConflictMerger, ConflictCreator

from geopy.distance import geodesic
from datetime import datetime
from app.models.models import get_connection
import config

# GeoProximityChecker
def calc_distance(lat1, lon1, lat2, lon2):
    """Υπολογισμός απόστασης μεταξύ δύο σημείων με Haversine."""
    return geodesic((lat1, lon1), (lat2, lon2)).km

def check_proximity(report_lat, report_lon):
    """
    Check αν το report ανήκει σε ήδη υπάρχοντα Conflict.
    return: ('merge', conflict_id), ('pending', conflict_id), ('new', None)
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, latitude, longitude 
            FROM conflicts 
            WHERE status = 'active'
        """)
        conflicts = cursor.fetchall()

        for conflict in conflicts:
            conflict_id = conflict[0]
            conflict_lat = conflict[1]
            conflict_lon = conflict[2]

            if conflict_lat is None or conflict_lon is None:
                continue

            dist = calc_distance(
                report_lat, report_lon,
                conflict_lat, conflict_lon
            )

            if dist < config.MERGE_THRESHOLD_KM:
                return "merge", conflict_id
            elif dist < config.BORDERLINE_THRESHOLD_KM:
                return "pending", conflict_id

        return "new", None
    finally:
        conn.close()

# ConflictMerger 
def merge_conflict(report_id, report_desc, conflict_id):
    """
    Ενημερώνει ήδη υπάρχοντα Conflict με δεδομένα από RawReport.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Ανάκτηση υπάρχουσας περιγραφής
        cursor.execute("""
            SELECT description FROM conflicts WHERE id = ?
        """, (conflict_id,))
        existing = cursor.fetchone()
        existing_desc = existing[0] if existing else ""

        # Ενημέρωση Conflict
        cursor.execute("""
            UPDATE conflicts 
            SET description = ?, updated_at = ?
            WHERE id = ?
        """, (
            (existing_desc or "") + " | " + (report_desc or ""),
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            conflict_id
        ))

        # Ενημέρωση RawReport ως processed
        cursor.execute("""
            UPDATE raw_reports SET status = 'processed' 
            WHERE id = ?
        """, (report_id,))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# ── ConflictCreator ────────────────────────────────────────
def create_new_conflict(report_id, title, desc, lat, lon):
    """
    Δημιουργία νέου Conflict από RawReport.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO conflicts 
            (title, description, latitude, longitude, 
            status, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'active', ?, ?)
        """, (
            title, desc, lat, lon,
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        ))

        # Ενημέρωση RawReport ως processed
        cursor.execute("""
            UPDATE raw_reports SET status = 'processed' 
            WHERE id = ?
        """, (report_id,))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# MergeController 
def start_merging():
    """
     μέθοδος UC7.
    Ανακτά pending RawReport και αποφασίζει για κάθε ένα.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, title, description, latitude, longitude 
            FROM raw_reports 
            WHERE status = 'pending'
        """)
        pending_reports = cursor.fetchall()
    finally:
        conn.close()

    for report in pending_reports:
        report_id = report[0]
        title = report[1]
        desc = report[2]
        lat = report[3]
        lon = report[4]

        # Αν δεν έχει συντεταγμένες, παράλειψη
        if lat is None or lon is None:
            conn = get_connection()
            conn.execute("""
                UPDATE raw_reports SET status = 'processed' 
                WHERE id = ?
            """, (report_id,))
            conn.commit()
            conn.close()
            continue

        result, conflict_id = check_proximity(lat, lon)

        if result == "merge":
            merge_conflict(report_id, desc, conflict_id)
        elif result == "pending":
            conn = get_connection()
            conn.execute("""
                UPDATE raw_reports SET status = 'flagged' 
                WHERE id = ?
            """, (report_id,))
            conn.commit()
            conn.close()
        else:
            create_new_conflict(report_id, title, desc, lat, lon)