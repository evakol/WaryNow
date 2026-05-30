import sqlite3

def get_statistics(start_date, end_date):
    """Υπολογισμός στατιστικών από τα Conflicts της SQLite για το συγκεκριμένο χρονικό εύρος."""
    conn = sqlite3.connect("warynow.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT status, created_at FROM Conflict")
        all_conflicts = cursor.fetchall()
        conn.close()
        
        # Φιλτράρισμα βάσει ημερομηνίας
        filtered_conflicts = [c for c in all_conflicts if c[1] and (start_date <= c[1] <= end_date)]
        
        total_events = len(filtered_conflicts)
        # Καταμέτρηση ενεργών με μικρά γράμματα 'active'
        active_count = sum(1 for c in filtered_conflicts if c[0] == "active")
        
        return {
            "total": total_events,
            "active": active_count,
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        print(f"[Error] Σφάλμα στατιστικών: {e}")
        conn.close()
        return None

def export_statistics_file(stats_data, file_format="CSV"):
    """Προσομοίωση εξαγωγής και αποθήκευσης του αρχείου στατιστικών στη συσκευή."""
    if not stats_data:
        return False
    print(f"\n[FormatFile] Μορφοποίηση δεδομένων σε αρχείο {file_format}...")
    print(f"[ExportFile] Δημιουργία αναφοράς για το εύρος {stats_data['start_date']} έως {stats_data['end_date']}...")
    print("[DeviceStorage] Το αρχείο αποθηκεύτηκε επιτυχώς στη συσκευή!")
    return True