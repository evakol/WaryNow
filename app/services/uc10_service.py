import sqlite3

DATABASE_PATH = "warynow.db"

def get_flagged_reports():
    """Ανάκτηση των reports με status='flagged' (queryPendingReports)."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, status FROM RawReport WHERE status = 'flagged'")
    reports = cursor.fetchall()
    conn.close()
    return reports

def verify_report(report_id):
    """Κύρια Ροή: Έγκριση αναφοράς, status='Verified' και δημιουργία Conflict."""
    from datetime import datetime
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # UpdateStatus -> setVerificationStatus("Verified")
    cursor.execute("UPDATE RawReport SET status = 'Verified' WHERE id = ?", (report_id,))
    
    # ArchiveReport -> Ανάκτηση δεδομένων για μετατροπή
    cursor.execute("SELECT title, description FROM RawReport WHERE id = ?", (report_id,))
    report = cursor.fetchone()
    
    if report:
        # Δημιουργία ενεργού Conflict στη βάση
        current_date = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO Conflict (title, description, status, created_at) VALUES (?, ?, 'active', ?)", 
                       (report[0], report[1], current_date))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def reject_report(report_id):
    """Εναλλακτική Ροή: Απόρριψη αναφοράς (status='Rejected')."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE RawReport SET status = 'Rejected' WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()
    return True