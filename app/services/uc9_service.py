# app/services/uc9_service.py
# Υλοποίηση του UC9 - Κατάλογος Κρίσιμων Υποδομών (Infrastructure Directory)
# Controls: InfrastructureController, SearchEngine, FilterController

from geopy.distance import geodesic
from app.models.models import Conflict, Infrastructure, Session
import config


# ── SearchEngine ───────────────────────────────────────────
def search_by_location(lat, lng, radius_km):
    """
    Αναζητά υποδομές εντός ακτίνας radius_km από το σημείο (lat, lng).
    Αντιστοιχεί στο searchByLocation() → getInRadius() του Sequence Diagram.
    Επιστρέφει: λίστα Infrastructure objects εντός ακτίνας
    """
    session = Session()
    try:
        all_infra = session.query(Infrastructure).all()

        results = []
        for infra in all_infra:
            if infra.latitude is None or infra.longitude is None:
                continue

            dist = geodesic(
                (lat, lng),
                (infra.latitude, infra.longitude)
            ).km

            if dist <= radius_km:
                results.append({
                    "id": infra.id,
                    "name": infra.name,
                    "category": infra.category,
                    "subcategory": infra.subcategory,
                    "latitude": infra.latitude,
                    "longitude": infra.longitude,
                    "country": infra.country,
                    "status": infra.status,
                    "distance_km": round(dist, 2)
                })

        # Ταξινόμηση κατά απόσταση (κοντινότερα πρώτα)
        results.sort(key=lambda x: x["distance_km"])
        return results

    finally:
        session.close()


# ── FilterController ───────────────────────────────────────
def filter_by_category(results, category):
    """
    Φιλτράρει τα αποτελέσματα βάσει κατηγορίας.
    Αντιστοιχεί στο filterByCategory() του Sequence Diagram.
    category: "military" ή "civilian"
    Επιστρέφει: φιλτραρισμένη λίστα
    """
    if category is None or category == "all":
        return results

    return [
        infra for infra in results
        if infra["category"].lower() == category.lower()
    ]


def get_infrastructure_details(infra_id):
    """
    Ανακτά αναλυτικές πληροφορίες μιας υποδομής.
    Αντιστοιχεί στο showDetails(infrastructure) του Sequence Diagram.
    Επιστρέφει: dict με τα στοιχεία ή None
    """
    session = Session()
    try:
        infra = session.query(Infrastructure).filter_by(
            id=infra_id
        ).first()

        if infra is None:
            return None

        return {
            "id": infra.id,
            "name": infra.name,
            "category": infra.category,
            "subcategory": infra.subcategory,
            "latitude": infra.latitude,
            "longitude": infra.longitude,
            "country": infra.country,
            "status": infra.status
        }
    finally:
        session.close()


# ── InfrastructureController ──────────────────────────────
def request_infrastructure(conflict_id, radius_km=None):
    """
    Κεντρική μέθοδος UC9.
    Αντιστοιχεί στο Sequence Diagram:
    requestInfrastructure() → searchByLocation() → displayResults()
    
    ALT: αν results == 0 → suggestExpandRadius()
    
    conflict_id: ID της επιλεγμένης σύγκρουσης
    radius_km: ακτίνα αναζήτησης (default από config)
    Επιστρέφει: (results_list, conflict_data) ή (None, error_message)
    """
    if radius_km is None:
        radius_km = config.INFRASTRUCTURE_SEARCH_RADIUS_KM

    session = Session()
    try:
        # getConflictData()
        conflict = session.query(Conflict).filter_by(
            id=conflict_id
        ).first()

        if conflict is None:
            return None, "Η σύγκρουση δεν βρέθηκε."

        if conflict.latitude is None or conflict.longitude is None:
            return None, "Η σύγκρουση δεν έχει γεωγραφικές συντεταγμένες."

        conflict_data = {
            "id": conflict.id,
            "title": conflict.title,
            "latitude": conflict.latitude,
            "longitude": conflict.longitude
        }

    finally:
        session.close()

    # searchByLocation(lat, lng, radius)
    results = search_by_location(
        conflict_data["latitude"],
        conflict_data["longitude"],
        radius_km
    )

    # ALT: αν δεν βρεθούν υποδομές → suggestExpandRadius()
    if len(results) == 0:
        return [], f"Δεν βρέθηκαν υποδομές εντός {radius_km} km. Δοκιμάστε μεγαλύτερη ακτίνα."

    return results, conflict_data


def search_with_expanded_radius(conflict_id, current_radius_km):
    """
    Επαναληπτική αναζήτηση με μεγαλύτερη ακτίνα.
    Αντιστοιχεί στην εναλλακτική ροή: suggestExpandRadius() → Επαναληπτική αναζήτηση
    """
    new_radius = current_radius_km * config.RADIUS_EXPAND_FACTOR
    return request_infrastructure(conflict_id, radius_km=new_radius)


# ── Βοηθητικές μέθοδοι για populate δεδομένων ─────────────
def add_infrastructure(name, category, subcategory, lat, lng, country, status="operational"):
    """
    Προσθήκη υποδομής στη βάση (χρήσιμο για αρχικό populate).
    """
    session = Session()
    try:
        infra = Infrastructure(
            name=name,
            category=category,
            subcategory=subcategory,
            latitude=lat,
            longitude=lng,
            country=country,
            status=status
        )
        session.add(infra)
        session.commit()
        return infra.id
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()


def populate_sample_infrastructure():
    """
    Γεμίζει τη βάση με δείγματα υποδομών για testing.
    Καλείται μία φορά κατά την αρχικοποίηση.
    """
    samples = [
        # Στρατιωτικές υποδομές
        ("Incirlik Air Base", "military", "Αεροπορική Βάση", 37.002, 35.425, "Turkey"),
        ("Camp Bondsteel", "military", "Στρατιωτική Βάση", 42.366, 21.253, "Kosovo"),
        ("Ramstein Air Base", "military", "Αεροπορική Βάση", 49.436, 7.600, "Germany"),
        ("Deveselu Naval Base", "military", "Ναυτική Βάση", 44.033, 24.416, "Romania"),

        # Πολιτικές υποδομές
        ("Al-Shifa Hospital", "civilian", "Νοσοκομείο", 31.524, 34.442, "Palestine"),
        ("Aleppo University", "civilian", "Πανεπιστήμιο", 36.214, 37.127, "Syria"),
        ("Mariupol Drama Theatre", "civilian", "Θέατρο", 47.097, 37.551, "Ukraine"),
        ("Zaporizhzhia Nuclear Plant", "civilian", "Πυρηνικός Σταθμός", 47.507, 34.585, "Ukraine"),
        ("Kabul International Airport", "military", "Αεροδρόμιο", 34.565, 69.212, "Afghanistan"),
        ("Médecins Sans Frontières Kunduz", "civilian", "Νοσοκομείο", 36.728, 68.868, "Afghanistan"),
    ]

    session = Session()
    try:
        # Έλεγχος αν υπάρχουν ήδη δεδομένα
        count = session.query(Infrastructure).count()
        if count > 0:
            return  # Ήδη υπάρχουν δεδομένα

        for name, cat, subcat, lat, lng, country in samples:
            infra = Infrastructure(
                name=name,
                category=cat,
                subcategory=subcat,
                latitude=lat,
                longitude=lng,
                country=country,
                status="operational"
            )
            session.add(infra)

        session.commit()
        print(f"[UC9] Προστέθηκαν {len(samples)} δείγματα υποδομών.")
    except Exception as e:
        session.rollback()
        print(f"[UC9] Σφάλμα populate: {e}")
    finally:
        session.close()