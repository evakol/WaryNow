import tkinter as tk
from tkinter import messagebox
import sqlite3

# Εισαγωγή των UI λειτουργιών σου
from app.ui.uc10_ui import run_background_moderation_check
from app.ui.uc11_ui import open_statistics_window

def seed_mock_data():
    """Γεμίζει την τοπική SQLite βάση με δεδομένα ελέγχου."""
    conn = sqlite3.connect("warynow.db")
    cursor = conn.cursor()
    
    # Δημιουργία πινάκων αν δεν υπάρχουν
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS RawReport (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            status TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Conflict (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            status TEXT,
            created_at TEXT
        )
    """)
    
    # Καθαρισμός παλιών
    cursor.execute("DELETE FROM RawReport")
    cursor.execute("DELETE FROM Conflict")
    
    # Προσθήκη δοκιμαστικών με μικρά γράμματα (verified/flagged)
    cursor.execute("INSERT INTO RawReport (title, description, status) VALUES (?, ?, ?)",
                   ("Ύποπτη κίνηση οχημάτων", "Κοντά στα σύνορα", "flagged"))
    cursor.execute("INSERT INTO Conflict (title, description, status, created_at) VALUES (?, ?, ?, ?)",
                   ("Σύρραξη Α", "Ανταλλαγή πυρών", "active", "2026-05-10"))
    
    conn.commit()
    conn.close()
    print("[Test Setup] Τα δοκιμαστικά δεδομένα δημιουργήθηκαν επιτυχώς στην SQLite!")

def trigger_moderation():
    run_background_moderation_check()
    messagebox.showinfo("Σύστημα", "Ο Moderator έλεγξε τις αναφορές στο παρασκήνιο! Δείτε το Terminal.")

def main():
    seed_mock_data()

    root = tk.Tk()
    root.title("WaryNow App - Use Cases 10 & 11")
    root.geometry("450x280")
    root.configure(bg="#2c3e50")

    tk.Label(root, text="WaryNow - Σύστημα Ελέγχου", font=("Arial", 14, "bold"), fg="white", bg="#2c3e50").pack(pady=15)

    btn_uc11 = tk.Button(root, text="📊 Αριστερό Μενού: Εξαγωγή Στατιστικών (UC11)", 
                         command=open_statistics_window, font=("Arial", 11, "bold"), width=38, bg="#4CAF50", fg="white")
    btn_uc11.pack(pady=12)

    btn_uc10 = tk.Button(root, text="⚙️ Εκτέλεση Background Έλεγχου Moderator (UC10)", 
                         command=trigger_moderation, font=("Arial", 10), width=38, bg="#7f8c8d", fg="white")
    btn_uc10.pack(pady=12)

    root.mainloop()

if __name__ == "__main__":
    main()