from app.models.models import init_db, Session, Conflict
from app.services.uc8_service import create_alert_zone, get_user_zones, monitor_all_zones
from app.services.uc9_service import populate_sample_infrastructure, request_infrastructure
from datetime import datetime
import config

# Προσωρινή προσθήκη σταθερών στο config (αν δεν υπάρχουν) για να τρέξει το τεστ
if not hasattr(config, 'MAX_ALERT_RADIUS_KM'):
    config.MAX_ALERT_RADIUS_KM = 500
if not hasattr(config, 'INFRASTRUCTURE_SEARCH_RADIUS_KM'):
    config.INFRASTRUCTURE_SEARCH_RADIUS_KM = 100

print("--- ΕΚΚΙΝΗΣΗ ΔΟΚΙΜΩΝ UC8 & UC9 ---\n")

# 1. Δημιουργία πινάκων
init_db()
print("✅ [ΒΑΣΗ] Οι πίνακες είναι έτοιμοι.")

# 2. Γέμισμα με ψεύτικα δεδομένα (Mock Data)
# Βάζουμε μερικές υποδομές από τη συνάρτησή σου
populate_sample_infrastructure()
print("✅ [UC9] Η βάση γέμισε με υποδομές.")

# Φτιάχνουμε και μια εικονική σύγκρουση (Conflict) κοντά στην Ουκρανία για να κάνουμε αναζήτηση
session = Session()
test_conflict = session.query(Conflict).filter_by(title="Test Conflict Ukraine").first()
if not test_conflict:
    test_conflict = Conflict(
        title="Test Conflict Ukraine",
        description="Δοκιμαστική σύγκρουση για το UC9",
        latitude=47.5,   # Κοντά στη Zaporizhzhia (47.507, 34.585)
        longitude=34.5,
        status="active",
        created_at=datetime.utcnow()
    )
    session.add(test_conflict)
    session.commit()
conflict_id = test_conflict.id
session.close()


print("\n--- ΤΕΣΤ UC9: ΑΝΑΖΗΤΗΣΗ ΥΠΟΔΟΜΩΝ ---")
# Δοκιμάζουμε να βρούμε υποδομές γύρω από τη σύγκρουση (με ακτίνα 100km)
results, conflict_info = request_infrastructure(conflict_id, radius_km=100)

if type(results) == list and len(results) > 0:
    print(f"✅ [UC9 ΕΠΙΤΥΧΙΑ]: Βρέθηκαν {len(results)} υποδομές κοντά στο {conflict_info['title']}!")
    for r in results:
        print(f"   -> {r['name']} ({r['category']}) - Απόσταση: {r['distance_km']} km")
else:
    print(f"❌ [UC9 ΣΦΑΛΜΑ ή ΑΔΕΙΟ]: {results}")


print("\n--- ΤΕΣΤ UC8: ΔΗΜΙΟΥΡΓΙΑ ΓΕΩ-ΖΩΝΗΣ ---")
# --- ΠΡΟΣΘΗΚΗ ΓΙΑ ΤΟ ΤΕΣΤ: Φτιάχνουμε προσωρινά τον πίνακα 'users' της Ευαγγελίας ---
import sqlite3
conn = sqlite3.connect("warynow.db")
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
conn.execute("INSERT OR IGNORE INTO users (id, name) VALUES (1, 'TestUser')")
conn.commit()
conn.close()
# -------------------------------------------------------------------------------------
# Δοκιμάζουμε να φτιάξουμε μια ζώνη για τον χρήστη "1"
# (Προσοχή: Η check_subscription του κώδικά σου ψάχνει πίνακα users. Για το τεστ θα πετάξει λογικά ότι δεν είναι εγγεγραμμένος, εκτός αν η Εύα έφτιαξε τον πίνακα).
user_id = 1
lat, lng, radius = 47.0, 34.0, 200 # Μια ζώνη κοντά στην Ουκρανία
success, result = create_alert_zone(user_id, lat, lng, radius)

if success:
    print(f"✅ [UC8 ΕΠΙΤΥΧΙΑ]: Η γεω-ζώνη δημιουργήθηκε με ID: {result}")
    
    # Δοκιμάζουμε αν φέρνει τις ζώνες του χρήστη
    zones = get_user_zones(user_id)
    print(f"✅ [UC8]: Βρέθηκαν {len(zones)} ενεργές ζώνες για τον χρήστη {user_id}.")
else:
    print(f"⚠️ [UC8 ΑΠΟΤΥΧΙΑ]: {result} (Λογικό αν δεν έχει συνδεθεί η βάση 'users' της Ευαγγελίας ακόμα).")

print("\n--- ΤΕΛΟΣ ΔΟΚΙΜΩΝ ---")