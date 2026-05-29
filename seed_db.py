from app.models.models import Session, Conflict, RawReport, init_db
from datetime import datetime

def populate_presentation_data():
    """
    Γεμίζει τη βάση με τα τέλεια δεδομένα για να δουλέψουν ΟΛΑ τα Use Cases της ομάδας
    χωρίς να εξαρτόμαστε από το GDELT API.
    """
    init_db()
    session = Session()

    # Έλεγχος: Αν υπάρχουν ήδη δεδομένα, καθάρισέ τα για να έχουμε καθαρή παρουσίαση
    session.query(Conflict).delete()
    session.query(RawReport).delete()
    session.commit()

    print("⏳ Γέμισμα βάσης δεδομένων για την παρουσίαση...")

    # --- 1. Δεδομένα για τον Χάρτη σου (UC4/UC5) & Στατιστικά Ελπίδας (UC11) ---
    # Βάζουμε ημερομηνίες Μαΐου 2026 γιατί έτσι το έχει γράψει η Ελπίδα στο uc11_ui.py
    c1 = Conflict(title="Ukraine: Ένοπλη Σύρραξη στο Κίεβο", description="Ανταλλαγή πυρών.", latitude=50.45, longitude=30.52, status="active", created_at=datetime(2026, 5, 10))
    c2 = Conflict(title="Syria: Συνοριακή Ένταση", description="Συγκρούσεις στα βόρεια σύνορα.", latitude=36.2, longitude=37.1, status="active", created_at=datetime(2026, 5, 15))
    c3 = Conflict(title="Taiwan: Ναυτικό Επεισόδιο", description="Στρατιωτικά πλοία στα στενά.", latitude=23.5, longitude=121.0, status="active", created_at=datetime(2026, 5, 20))
    c4 = Conflict(title="Sudan: Εμφύλιες Ταραχές", description="Οδομαχίες στο Χαρτούμ.", latitude=15.5, longitude=32.5, status="active", created_at=datetime(2026, 5, 25))

    session.add_all([c1, c2, c3, c4])

    # --- 2. Δεδομένα για το Moderation της Ελπίδας (UC10) ---
    # Η Ελπίδα ψάχνει 'flagged' reports. Και έχει βάλει κανόνα να εγκρίνει όσα έχουν τις λέξεις "Ύποπτη" ή "Έκρηξη".
    r1 = RawReport(title="Ύποπτη κίνηση στρατευμάτων", description="Αναφορά από τοπικά μέσα.", location="Border", latitude=10.0, longitude=10.0, source="Local News", status="flagged", created_at=datetime.utcnow())
    r2 = RawReport(title="Έκρηξη σε αποθήκη πυρομαχικών", description="Ανεπιβεβαίωτες πληροφορίες.", location="City", latitude=20.0, longitude=20.0, source="Twitter", status="flagged", created_at=datetime.utcnow())
    r3 = RawReport(title="Ειρηνική διαδήλωση στην πλατεία", description="Δεν υπάρχει βία.", location="Square", latitude=30.0, longitude=30.0, source="News", status="flagged", created_at=datetime.utcnow())

    # --- 3. Δεδομένα για τη Ροή Ειδήσεων του Βάιου (UC6) ---
    # Θέλουμε μερικά processed reports για να φαίνονται στο δεξί πλαίσιο.
    r4 = RawReport(title="ΟΗΕ: Νέα έκκληση για εκεχειρία στη Μέση Ανατολή.", source="Reuters", status="processed", created_at=datetime.utcnow())
    r5 = RawReport(title="Αυξημένη στρατιωτική κινητικότητα εντοπίστηκε από δορυφόρους.", source="CNN", status="processed", created_at=datetime.utcnow())

    session.add_all([r1, r2, r3, r4, r5])

    session.commit()
    session.close()
    print("✅ Η βάση γέμισε επιτυχώς! Μπορείτε να ξεκινήσετε την εφαρμογή.")

if __name__ == "__main__":
    populate_presentation_data()