from app.services.uc10_service import get_flagged_reports, verify_report, reject_report

def run_background_moderation_check():
    """
    Background Service: Ο Moderator ελέγχει 'αόρατα' τις αναφορές.
    Δεν ανοίγει παράθυρο στο UI. Εκτελείται στο παρασκήνιο του συστήματος.
    """
    print("\n[Background System] Έναρξη αυτόματου ελέγχου αναφορών από τον Moderator...")
    
    reports = get_flagged_reports()
    if not reports:
        print("[Background System] Δεν βρέθηκαν νέες εκκρεμείς αναφορές προς έλεγχο.")
        return "No reports to moderate"

    # Επεξεργασία των εκκρεμών αναφορών στο παρασκήνιο
    for report in reports:
        report_id, title, desc, _ = report
        print(f"[Background System] Έλεγχος αναφοράς ID {report_id}: '{title}'")
        
        # Προσομοίωση απόφασης: Αν ο τίτλος περιέχει 'Ύποπτη', την εγκρίνει, αλλιώς την απορρίπτει
        if "Ύποπτη" in title or "Έκρηξη" in title:
            verify_report(report_id)
            print(f"--> [UC10 System Action] Η αναφορά {report_id} εγκρίθηκε αυτόματα και έγινε Conflict.")
        else:
            reject_report(report_id)
            print(f"--> [UC10 System Action] Η αναφορά {report_id} απορρίφθηκε αυτόματα ως μη έγκυρη.")
            
    print("[Background System] Ο έλεγχος του Moderator ολοκληρώθηκε.\n")
    return "Moderation complete"