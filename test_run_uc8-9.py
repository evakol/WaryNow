import sqlite3
from datetime import datetime, timezone
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.models import init_db, get_connection
from app.services.uc8_service import create_alert_zone, get_user_zones, validate_zone
from app.services.uc9_service import filter_by_category
import config

if not hasattr(config, 'MAX_ALERT_RADIUS_KM'):
    config.MAX_ALERT_RADIUS_KM = 500

# Βοηθητική συνάρτηση αξιολόγησης αποτελέσματος
def check(test_name, expected, actual):
    """
    Εκτυπώνει το αποτέλεσμα ενός test case.
    expected: True/False ή συγκεκριμένη τιμή
    actual:   αυτό που έβγαλε πραγματικά ο κώδικας
    """
    passed = expected == actual
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} | {test_name}")
    if not passed:
        print(f"         Αναμενόμενο: {expected}")
        print(f"         Πραγματικό:  {actual}")
    return passed

# Μετρητές 
total = 0
passed_count = 0

def run_test(test_name, expected, actual):
    global total, passed_count
    total += 1
    if check(test_name, expected, actual):
        passed_count += 1


print("=" * 60)
print("  ΕΝΑΡΞΗ ΔΟΚΙΜΩΝ: USE CASE 8 & USE CASE 9")
print("=" * 60)

# Αρχικοποίηση βάσης 
init_db()
print("\n✅ [ΒΑΣΗ] Αρχικοποίηση πινάκων SQLite3.")

conn = get_connection()
cursor = conn.cursor()

# Καθαρισμός προηγούμενων δοκιμαστικών δεδομένων
cursor.execute("DELETE FROM conflicts WHERE title = 'Test Conflict Ukraine'")
cursor.execute("DELETE FROM infrastructures WHERE name IN ('Zaporizhzhia Nuclear Plant', 'Kabul International Airport')")
cursor.execute("DELETE FROM alert_zones WHERE subscriber_id = 999")

# Εισαγωγή δοκιμαστικών δεδομένων
current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
cursor.execute("""
    INSERT INTO conflicts (title, description, latitude, longitude, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", ("Test Conflict Ukraine", "Δοκιμαστική σύγκρουση για UC9", 47.5, 34.5, "active", current_date, current_date))
conflict_id = cursor.lastrowid

cursor.execute("""
    INSERT INTO infrastructures (name, category, subcategory, latitude, longitude, country, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", ("Zaporizhzhia Nuclear Plant", "civilian", "Πυρηνικός Σταθμός", 47.507, 34.585, "Ukraine", "operational"))

cursor.execute("""
    INSERT INTO infrastructures (name, category, subcategory, latitude, longitude, country, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", ("Kabul International Airport", "military", "Αεροδρόμιο", 34.565, 69.212, "Afghanistan", "operational"))

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (999, 'TestUserFerit')")
conn.commit()
conn.close()
print("✅ [ΔΕΔΟΜΕΝΑ] Εισαγωγή δοκιμαστικών οντοτήτων.")


print("\n" + "=" * 60)
print("  UC8 — ΒΑΣΙΚΗ ΡΟΗ: validate_zone()")
print("=" * 60)

# TC-UC8-01: Έγκυρη ζώνη
is_valid, msg = validate_zone(47.0, 34.0, 200.0)
run_test(
    "TC-UC8-01 | Είσοδος: lat=47.0, lng=34.0, R=200km | Αναμένεται: Έγκυρη",
    True, is_valid
)

# TC-UC8-02: Έγκυρη ζώνη με μικρή ακτίνα
is_valid, msg = validate_zone(37.9, 23.7, 50.0)
run_test(
    "TC-UC8-02 | Είσοδος: lat=37.9, lng=23.7, R=50km | Αναμένεται: Έγκυρη",
    True, is_valid
)


print("\n" + "=" * 60)
print("  UC8 — ΕΝΑΛΛΑΚΤΙΚΗ ΡΟΗ: alt [R > 500km]")
print("=" * 60)

# TC-UC8-03: Ακτίνα πάνω από το όριο
is_valid, msg = validate_zone(47.0, 34.0, 600.0)
run_test(
    "TC-UC8-03 | Είσοδος: R=600km (> 500km) | Αναμένεται: Μη έγκυρη",
    False, is_valid
)
print(f"         Μήνυμα σφάλματος: {msg}")

# TC-UC8-04: Αρνητική ακτίνα
is_valid, msg = validate_zone(47.0, 34.0, -10.0)
run_test(
    "TC-UC8-04 | Είσοδος: R=-10km | Αναμένεται: Μη έγκυρη",
    False, is_valid
)
print(f"         Μήνυμα σφάλματος: {msg}")

# TC-UC8-05: Μηδενική ακτίνα
is_valid, msg = validate_zone(47.0, 34.0, 0.0)
run_test(
    "TC-UC8-05 | Είσοδος: R=0km | Αναμένεται: Μη έγκυρη",
    False, is_valid
)
print(f"         Μήνυμα σφάλματος: {msg}")


print("\n" + "=" * 60)
print("  UC8 — ΕΝΑΛΛΑΚΤΙΚΗ ΡΟΗ: Μη έγκυρες συντεταγμένες")
print("=" * 60)

# TC-UC8-06: Μη έγκυρο latitude (> 90)
is_valid, msg = validate_zone(95.0, 34.0, 100.0)
run_test(
    "TC-UC8-06 | Είσοδος: lat=95.0 (> 90) | Αναμένεται: Μη έγκυρη",
    False, is_valid
)
print(f"         Μήνυμα σφάλματος: {msg}")

# TC-UC8-07: Μη έγκυρο longitude (> 180)
is_valid, msg = validate_zone(47.0, 200.0, 100.0)
run_test(
    "TC-UC8-07 | Είσοδος: lng=200.0 (> 180) | Αναμένεται: Μη έγκυρη",
    False, is_valid
)
print(f"         Μήνυμα σφάλματος: {msg}")

# TC-UC8-08: Αρνητικό latitude (< -90)
is_valid, msg = validate_zone(-95.0, 34.0, 100.0)
run_test(
    "TC-UC8-08 | Είσοδος: lat=-95.0 (< -90) | Αναμένεται: Μη έγκυρη",
    False, is_valid
)
print(f"         Μήνυμα σφάλματος: {msg}")


print("\n" + "=" * 60)
print("  UC8 — ΒΑΣΙΚΗ ΡΟΗ: create_alert_zone() / get_user_zones()")
print("=" * 60)

# TC-UC8-09: Επιτυχής δημιουργία ζώνης
success = create_alert_zone(999, 47.0, 34.0, 200.0, "Ukraine Region")
run_test(
    "TC-UC8-09 | Δημιουργία ζώνης για user_id=999 | Αναμένεται: True",
    True, success
)

# TC-UC8-10: Ανάκτηση ζωνών χρήστη
zones = get_user_zones(999)
run_test(
    "TC-UC8-10 | Ανάκτηση ζωνών user_id=999 | Αναμένεται: ≥1 ζώνη",
    True, len(zones) >= 1
)
if zones:
    z = zones[-1]
    print(f"         -> ID: {z.id} | Τοποθεσία: {z.country} | "
          f"Κέντρο: ({z.center_lat}, {z.center_lng}) | Ακτίνα: {z.radius_km} km")

# TC-UC8-11: Ανάκτηση ζωνών για μη υπάρχοντα χρήστη
zones_empty = get_user_zones(99999)
run_test(
    "TC-UC8-11 | Ανάκτηση ζωνών για user_id=99999 (δεν υπάρχει) | Αναμένεται: 0 ζώνες",
    True, len(zones_empty) == 0
)


print("\n" + "=" * 60)
print("  UC9 — ΒΑΣΙΚΗ ΡΟΗ: filter_by_category()")
print("=" * 60)

# TC-UC9-01: Φιλτράρισμα όλων των υποδομών
all_infra = filter_by_category("Όλες")
run_test(
    "TC-UC9-01 | Φίλτρο='Όλες' | Αναμένεται: ≥2 εγγραφές",
    True, len(all_infra) >= 2
)
print(f"         Βρέθηκαν {len(all_infra)} υποδομές συνολικά.")

# TC-UC9-02: Φιλτράρισμα πολιτικών υποδομών
civilian = filter_by_category("Πολιτικές")
run_test(
    "TC-UC9-02 | Φίλτρο='Πολιτικές' | Αναμένεται: ≥1 εγγραφή",
    True, len(civilian) >= 1
)
for item in civilian:
    print(f"         -> {item.name} | {item.category} | {item.status}")

# TC-UC9-03: Επιβεβαίωση ότι οι πολιτικές υποδομές δεν περιέχουν στρατιωτικές
only_civilian = all(item.category_en == "civilian" for item in civilian)
run_test(
    "TC-UC9-03 | Φίλτρο='Πολιτικές' | Αναμένεται: Καμία στρατιωτική εγγραφή",
    True, only_civilian
)

# TC-UC9-04: Φιλτράρισμα στρατιωτικών υποδομών
military = filter_by_category("Στρατιωτικές")
run_test(
    "TC-UC9-04 | Φίλτρο='Στρατιωτικές' | Αναμένεται: ≥1 εγγραφή",
    True, len(military) >= 1
)
for item in military:
    print(f"         -> {item.name} | {item.category} | {item.status}")

# TC-UC9-05: Επιβεβαίωση ότι οι στρατιωτικές δεν περιέχουν πολιτικές
only_military = all(item.category_en == "military" for item in military)
run_test(
    "TC-UC9-05 | Φίλτρο='Στρατιωτικές' | Αναμένεται: Καμία πολιτική εγγραφή",
    True, only_military
)

# TC-UC9-06: Φίλτρο με κατηγορία που δεν υπάρχει
empty = filter_by_category("ΔενΥπάρχει")
run_test(
    "TC-UC9-06 | Φίλτρο='ΔενΥπάρχει' | Αναμένεται: 0 εγγραφές",
    True, len(empty) == 0
)

# TC-UC9-07: Έλεγχος μετατροπής κατηγορίας (EN→GR)
if civilian:
    run_test(
        "TC-UC9-07 | Μετατροπή category_en='civilian' → 'Πολιτική' | Αναμένεται: 'Πολιτική'",
        "Πολιτική", civilian[0].category
    )

if military:
    run_test(
        "TC-UC9-08 | Μετατροπή category_en='military' → 'Στρατιωτική' | Αναμένεται: 'Στρατιωτική'",
        "Στρατιωτική", military[0].category
    )


print("\n" + "=" * 60)
print(f"  ΑΠΟΤΕΛΕΣΜΑ: {passed_count}/{total} tests PASS")
if passed_count == total:
    print("  ✅ ΟΛΑ ΤΑ TESTS ΠΕΡΑΣΑΝ ΕΠΙΤΥΧΩΣ")
else:
    print(f"  ❌ {total - passed_count} tests ΑΠΕΤΥΧΑΝ")
print("=" * 60)
