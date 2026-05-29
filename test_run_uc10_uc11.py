import tkinter as tk
from tkinter import messagebox
from app.models.models import init_db
import sqlite3

# Εισαγωγή των διορθωμένων λειτουργιών
from app.ui.uc10_ui import run_background_moderation_check
from app.ui.uc11_ui import open_statistics_window

def seed_mock_data():
    """Γεμίζει τη βάση με αρχικά δεδομένα ελέγχου."""
    conn = sqlite3.connect("warynow.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM RawReport")
    cursor.execute("DELETE FROM Conflict")
    
    # Αναφορές που περιμένουν έλεγχο στο παρασκήνιο (UC10)
    cursor.execute("INSERT INTO RawReport (title, description, status) VALUES ('Ύποπτη κίνηση οχημάτων', 'Κοντά στα σύνορα', 'flagged')")
    cursor.execute("INSERT INTO RawReport (title, description, status) VALUES ('Απλό παράπονο χρήστη', 'Λάθος τοποθεσία χάρτη', 'flagged')")
    
    # Έτοιμα Conflicts για τα στατιστικά (UC11)
    cursor.execute("INSERT INTO Conflict (title, description, status, created_at) VALUES ('Σύρραξη Α', 'Ανταλλαγή πυρών', 'active', '2026-05-10')")
    
    conn.commit()
    conn.close()

def trigger_moderation():
    # Εκτελεί τον αόρατο έλεγχο και βγάζει απλά ένα ενημερωτικό μήνυμα επιτυχίας
    result = run_background_moderation_check()
    messagebox.showinfo("Σύστημα", "Ο Moderator έλεγξε τις αναφορές στο παρασκήνιο! Δείτε τα logs στο Terminal.")

def main():
    init_db()
    seed_mock_data()

    # Κεντρικό παράθυρο (Προσομοίωση της εφαρμογής WaryNow)
    root = tk.Tk()
    root.title("WaryNow App")
    root.geometry("450x280")
    root.configure(bg="#2c3e50")

    tk.Label(root, text="WaryNow - Σύστημα Ελέγχου", font=("Arial", 14, "bold"), fg="white", bg="#2c3e50").pack(pady=15)

    # ΚΟΥΜΠΙ 1: Προσομοίωση του Mockup Sidebar (UC11 - Στατιστικά)
    # Αυτό αντιστοιχεί ακριβώς στο μαύρο πλαίσιο της φωτογραφίας σου
    btn_uc11 = tk.Button(root, text="📊 Αριστερό Μενού: Εξαγωγή Στατιστικών (UC11)", 
                         command=open_statistics_window, font=("Arial", 11, "bold"), width=38, bg="#4CAF50", fg="white")
    btn_uc11.pack(pady=12)

    # ΚΟΥΜΠΙ 2: Προσομοίωση του Background Service (UC10 - Moderator)
    # Αυτό τρέχει αόρατα, δεν ανοίγει δικό του παράθυρο
    btn_uc10 = tk.Button(root, text="⚙️ Εκτέλεση Background Έλεγχου Moderator (UC10)", 
                         command=trigger_moderation, font=("Arial", 10), width=38, bg="#7f8c8d", fg="white")
    btn_uc10.pack(pady=12)

    tk.Label(root, text="* Το UC10 εκτελείται στο background χωρίς UI, όπως ζητήθηκε.", 
             font=("Arial", 9, "italic"), fg="#bdc3c7", bg="#2c3e50").pack(pady=15)

    root.mainloop()

if __name__ == "__main__":
    main()