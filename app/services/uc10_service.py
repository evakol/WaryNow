from datetime import datetime
import sqlite3

def get_flagged_reports():
    """Ανάκτηση των αναφορών με κατάσταση 'flagged' από την SQLite."""
    conn = sqlite3.connect("warynow.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, status FROM RawReport WHERE status = 'flagged'")
    reports = cursor.fetchall()
    conn.close()
    return reports

def verify_report(report_id):
    """Έγκριση αναφοράς: status='verified' και δημιουργία Conflict με status='active'."""
    conn = sqlite3.connect("warynow.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, description FROM RawReport WHERE id = ?", (report_id,))
    report = cursor.fetchone()
    
    if report:
        # Αλλαγή σε μικρά γράμματα 'verified' σύμφωνα με τις οδηγίες της ομάδας
        cursor.execute("UPDATE RawReport SET status = 'verified' WHERE id = ?", (report_id,))
        
        # Δημιουργία της σύγκρουσης (Conflict)
        current_date = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "INSERT INTO Conflict (title, description, status, created_at) VALUES (?, ?, 'active', ?)",
            (report[0], report[1], current_date)
        )
        conn.commit()
        conn.close()
        return True
        
    conn.close()
    return False

def reject_report(report_id):
    """Απόρριψη αναφοράς: status='rejected'."""
    conn = sqlite3.connect("warynow.db")
    cursor = conn.cursor()
    # Αλλαγή σε μικρά γράμματα 'rejected' σύμφωνα με τις οδηγίες της ομάδας
    cursor.execute("UPDATE RawReport SET status = 'rejected' WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()
    return True