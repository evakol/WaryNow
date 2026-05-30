from app.models.models import get_connection
import config

def validate_zone(center_lat, center_lng, radius_km):
    if radius_km <= 0:
        return False, "Η ακτίνα πρέπει να είναι θετικός αριθμός."
    if radius_km > config.MAX_ALERT_RADIUS_KM:
        return False, f"Η ακτίνα υπερβαίνει το μέγιστο όριο ({config.MAX_ALERT_RADIUS_KM} km)."
    if not (-90 <= center_lat <= 90):
        return False, "Μη έγκυρο γεωγραφικό πλάτος (latitude)."
    if not (-180 <= center_lng <= 180):
        return False, "Μη έγκυρο γεωγραφικό μήκος (longitude)."
    return True, None

def get_user_zones(subscriber_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, country, center_lat, center_lng, radius_km 
        FROM alert_zones 
        WHERE subscriber_id = ? AND is_active = 1
    """, (subscriber_id,))
    rows = cursor.fetchall()
    conn.close()
    
    class Zone:
        def __init__(self, r):
            self.id, self.country, self.center_lat, self.center_lng, self.radius_km = r
    return [Zone(row) for row in rows]

def create_alert_zone(subscriber_id, center_lat, center_lng, radius_km, country=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alert_zones (subscriber_id, center_lat, center_lng, radius_km, country, is_active)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (subscriber_id, center_lat, center_lng, radius_km, country))
    conn.commit()
    conn.close()
    return True