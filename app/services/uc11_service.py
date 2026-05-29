import sqlite3

DATABASE_PATH = "warynow.db"

def get_statistics(start_date, end_date):
    """CheckDataAvailability & CalculateIntensity βάσει ημερομηνιών."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Έλεγχος αν υπάρχουν Conflicts (CheckDataAvailability)
    cursor.execute("SELECT * FROM Conflict WHERE created_at >= ? AND created_at <= ?", (start_date, end_date))
    conflicts = cursor.fetchall()
    
    if not conflicts:
        conn.close()
        return None # Εναλλακτική ροή: showNoDataMessage
        
    # Υπολογισμός συνόλου και ενεργών (CalculateIntensity)
    cursor.execute("SELECT COUNT(*) FROM Conflict WHERE created_at >= ? AND created_at <= ?", (start_date, end_date))
    total_conflicts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Conflict WHERE created_at >= ? AND created_at <= ? AND status = 'active'", (start_date, end_date))
    active_conflicts = cursor.fetchone()[0]
    
    conn.close()
    return {
        "start": start_date,
        "end": end_date,
        "total": total_conflicts,
        "active": active_conflicts
    }

def export_statistics_file(stats_data, file_format="CSV"):
    """
    FormatFile & ExportFile -> Ενεργοποιείται από το αριστερό μενού 
    (Παρουσίαση Λειτουργιών / Εξαγωγή στατιστικών).
    """
    if not stats_data:
        return False
    
    print("\n[UI Action] Ο χρήστης άνοιξε το αριστερό Sidebar...")
    print("[UI Action] Επιλέχθηκε: 'Εξαγωγή στατιστικών'...")
    print(f"[FormatFile] Μορφοποίηση των {stats_data['total']} γεγονότων σε {file_format}...")
    print(f"[ExportFile] Δημιουργία δομής αρχείου αναφοράς...")
    print(f"[DeviceStorage] Επιτυχής αποθήκευση στη συσκευή!")
    return True