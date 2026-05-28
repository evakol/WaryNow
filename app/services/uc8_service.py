# app/services/uc8_service.py
# Υλοποίηση του UC8 - Ρύθμιση Γεω-ειδοποιήσεων (Geofencing Alerts)
# Controls: AlertController, ZoneValidator, NotificationService

from geopy.distance import geodesic
from datetime import datetime
from app.models.models import AlertZone, Notification, Conflict, Session
import config


# ── ZoneValidator ──────────────────────────────────────────
def validate_zone(center_lat, center_lng, radius_km):
    """
    Ελέγχει αν η ακτίνα R είναι εντός ορίων και αν το σημείο
    είναι σε υποστηριζόμενη περιοχή.
    ALT: αν R > MAX_ALERT_RADIUS_KM → invalidRadius()
    Επιστρέφει: (True, None) ή (False, "μήνυμα σφάλματος")
    """
    # Έλεγχος ακτίνας
    if radius_km <= 0:
        return False, "Η ακτίνα πρέπει να είναι θετικός αριθμός."
    if radius_km > config.MAX_ALERT_RADIUS_KM:
        return False, f"Η ακτίνα υπερβαίνει το μέγιστο όριο ({config.MAX_ALERT_RADIUS_KM} km)."

    # Έλεγχος εγκυρότητας συντεταγμένων
    if not (-90 <= center_lat <= 90):
        return False, "Μη έγκυρο γεωγραφικό πλάτος (latitude)."
    if not (-180 <= center_lng <= 180):
        return False, "Μη έγκυρο γεωγραφικό μήκος (longitude)."

    return True, None


# ── AlertController ────────────────────────────────────────
def check_subscription(subscriber_id):
    """
    Ελέγχει αν ο χρήστης είναι Subscriber.
    ALT: αν δεν είναι → showUpgradePrompt()
    Επιστρέφει: True αν είναι subscriber, False αν είναι guest
    """
    # Εδώ ελέγχουμε στη βάση αν ο χρήστης υπάρχει στον πίνακα users
    # Προσωρινά: αν subscriber_id > 0 θεωρείται subscriber
    # Αυτό θα συνδεθεί με τον κώδικα της Ευαγγελίας (UC1-3)
    import sqlite3
    conn = sqlite3.connect("warynow.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE id = ?", (subscriber_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def create_alert_zone(subscriber_id, center_lat, center_lng, radius_km):
    """
    Κεντρική μέθοδος UC8 - Δημιουργία νέας ζώνης παρακολούθησης.
    Αντιστοιχεί στο Sequence Diagram:
    checkSubscription() → validate() → createZone() → saveZoneToProfile()
    
    Επιστρέφει: (True, zone_id) ή (False, error_message)
    """
    # Βήμα 1: checkSubscription()
    if not check_subscription(subscriber_id):
        return False, "Δεν είστε εγγεγραμμένος χρήστης. Αναβαθμίστε τον λογαριασμό σας."

    # Βήμα 2: validate(center, R)
    is_valid, error_msg = validate_zone(center_lat, center_lng, radius_km)
    if not is_valid:
        return False, error_msg

    # Βήμα 3: createZone(center, R) + saveZoneToProfile(zone)
    session = Session()
    try:
        new_zone = AlertZone(
            subscriber_id=subscriber_id,
            center_lat=center_lat,
            center_lng=center_lng,
            radius_km=radius_km,
            is_active=1,
            created_at=datetime.utcnow()
        )
        session.add(new_zone)
        session.commit()

        zone_id = new_zone.id
        return True, zone_id

    except Exception as e:
        session.rollback()
        return False, f"Σφάλμα αποθήκευσης: {str(e)}"
    finally:
        session.close()


def get_user_zones(subscriber_id):
    """
    Ανακτά όλες τις ενεργές ζώνες ενός χρήστη.
    Χρησιμοποιείται για εμφάνιση στο AlertScreen.
    """
    session = Session()
    try:
        zones = session.query(AlertZone).filter_by(
            subscriber_id=subscriber_id,
            is_active=1
        ).all()
        return zones
    finally:
        session.close()


def delete_alert_zone(zone_id, subscriber_id):
    """
    Απενεργοποίηση ζώνης (soft delete).
    """
    session = Session()
    try:
        zone = session.query(AlertZone).filter_by(
            id=zone_id,
            subscriber_id=subscriber_id
        ).first()
        if zone:
            zone.is_active = 0
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()


# ── NotificationService ───────────────────────────────────
def check_new_conflicts(zone):
    """
    Ελέγχει αν υπάρχουν νέα Conflicts εντός της ζώνης.
    Καλείται περιοδικά από τον scheduler.
    Επιστρέφει: λίστα Conflicts εντός ακτίνας
    """
    session = Session()
    try:
        # Ανάκτηση ενεργών conflicts
        conflicts = session.query(Conflict).filter_by(
            status="active"
        ).all()

        nearby = []
        for conflict in conflicts:
            if conflict.latitude is None or conflict.longitude is None:
                continue

            dist = geodesic(
                (zone.center_lat, zone.center_lng),
                (conflict.latitude, conflict.longitude)
            ).km

            if dist <= zone.radius_km:
                nearby.append(conflict)

        return nearby
    finally:
        session.close()


def create_notification(subscriber_id, conflict, zone):
    """
    Δημιουργεί Notification για τον χρήστη.
    Αντιστοιχεί στο createNotification() του Sequence Diagram.
    """
    session = Session()
    try:
        notif = Notification(
            subscriber_id=subscriber_id,
            conflict_id=conflict.id,
            zone_id=zone.id,
            message=f"Νέα σύγκρουση: {conflict.title} - "
                    f"Απόσταση: {geodesic((zone.center_lat, zone.center_lng), (conflict.latitude, conflict.longitude)).km:.1f} km",
            is_read=0,
            created_at=datetime.utcnow()
        )
        session.add(notif)
        session.commit()
        return notif.id
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()


def get_user_notifications(subscriber_id):
    """
    Ανακτά τις ειδοποιήσεις ενός χρήστη (πιο πρόσφατες πρώτα).
    """
    session = Session()
    try:
        notifs = session.query(Notification).filter_by(
            subscriber_id=subscriber_id
        ).order_by(Notification.created_at.desc()).all()
        return notifs
    finally:
        session.close()


# ── activateMonitoring (καλείται από τον scheduler) ───────
def monitor_all_zones():
    """
    Κεντρική μέθοδος UC8 που τρέχει περιοδικά.
    Ελέγχει ΟΛΕΣ τις ενεργές ζώνες και αποστέλλει
    ειδοποιήσεις αν βρεθούν νέα conflicts.
    Η μόνη μέθοδος που καλείται από έξω (scheduler/main.py).
    """
    session = Session()
    try:
        # Ανάκτηση όλων των ενεργών ζωνών
        active_zones = session.query(AlertZone).filter_by(
            is_active=1
        ).all()

        for zone in active_zones:
            # checkNewConflicts(zone)
            nearby_conflicts = check_new_conflicts(zone)

            for conflict in nearby_conflicts:
                # Έλεγχος αν έχει ήδη σταλεί ειδοποίηση
                existing = session.query(Notification).filter_by(
                    subscriber_id=zone.subscriber_id,
                    conflict_id=conflict.id,
                    zone_id=zone.id
                ).first()

                if not existing:
                    # createNotification() + sendPushNotification()
                    create_notification(
                        zone.subscriber_id,
                        conflict,
                        zone
                    )

    except Exception as e:
        print(f"[UC8] Monitoring error: {e}")
    finally:
        session.close()
