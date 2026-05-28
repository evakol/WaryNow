# app/services/uc7_service.py
# Υλοποίηση του UC7 - Conflict Merging
# Controls: MergeController, GeoProximityChecker, ConflictMerger, ConflictCreator

from geopy.distance import geodesic
from datetime import datetime
from app.models.models import RawReport, Conflict, Coordinate, Session
import config

# ── GeoProximityChecker ────────────────────────────────────
def calc_distance(lat1, lon1, lat2, lon2):
    """Υπολογισμός απόστασης μεταξύ δύο σημείων (Haversine μέσω geopy)"""
    return geodesic((lat1, lon1), (lat2, lon2)).km

def check_proximity(report, session):
    """
    Ελέγχει αν το report ανήκει σε υπάρχον Conflict.
    Επιστρέφει: 'merge', 'pending', ή 'new'
    """
    conflicts = session.query(Conflict).all()

    for conflict in conflicts:
        if conflict.latitude is None or conflict.longitude is None:
            continue

        dist = calc_distance(
            report.latitude, report.longitude,
            conflict.latitude, conflict.longitude
        )

        if dist < config.MERGE_THRESHOLD_KM:
            return "merge", conflict
        elif dist < config.BORDERLINE_THRESHOLD_KM:
            return "pending", conflict

    return "new", None

# ── ConflictMerger ─────────────────────────────────────────
def merge_conflict(report, conflict, session):
    """
    Ενημερώνει υπάρχον Conflict με δεδομένα από το RawReport.
    """
    conflict.description = (
        (conflict.description or "") + " | " + (report.description or "")
    )
    conflict.updated_at = datetime.utcnow()
    report.status = "processed"

# ── ConflictCreator ────────────────────────────────────────
def create_new_conflict(report, session):
    """
    Δημιουργεί νέο Conflict από το RawReport.
    """
    new_conflict = Conflict(
        title=report.title,
        description=report.description,
        latitude=report.latitude,
        longitude=report.longitude,
        status="active",
        created_at=datetime.utcnow()
    )
    session.add(new_conflict)
    report.status = "processed"

# ── MergeController ────────────────────────────────────────
def start_merging():
    """
    Κεντρική μέθοδος UC7. Ανακτά τα pending RawReport
    και αποφασίζει merge/new/pending για κάθε ένα.
    """
    session = Session()
    try:
        # Ανάκτηση αδιαχείριστων reports
        pending_reports = session.query(RawReport).filter_by(
            status="pending"
        ).all()

        for report in pending_reports:
            # Αν δεν έχει συντεταγμένες, παράλειψη
            if report.latitude is None or report.longitude is None:
                report.status = "processed"
                continue

            result, conflict = check_proximity(report, session)

            if result == "merge":
                merge_conflict(report, conflict, session)
            elif result == "pending":
                report.status = "flagged"  # → PendingFlagInterface
            else:
                create_new_conflict(report, session)

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()