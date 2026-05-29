import tkinter as tk
from tkinter import messagebox
from app.services.uc11_service import get_statistics, export_statistics_file

def open_statistics_window():
    """Ανοίγει το παράθυρο στατιστικών από το Αριστερό Μενού."""
    window = tk.Toplevel()
    window.title("WaryNow - UC11 Εξαγωγή Στατιστικών")
    window.geometry("450x350")
    window.configure(bg="#1a1a1a") # Σκούρο φόντο όπως το mockup σου

    tk.Label(window, text="Παρουσίαση Λειτουργιών", font=("Arial", 14, "bold"), fg="white", bg="#1a1a1a").pack(pady=10)
    tk.Label(window, text="Στατιστικά Στοιχεία Συγκρούσεων", font=("Arial", 11), fg="#lightgray", bg="#1a1a1a").pack(pady=5)

    # Προσομοίωση επιλογής ημερομηνιών
    tk.Label(window, text="Εύρος: 2026-05-01 έως 2026-05-31", font=("Arial", 10, "italic"), fg="yellow", bg="#1a1a1a").pack(pady=15)

    def process_stats():
        # Κλήση της back-end λογικής
        stats = get_statistics("2026-05-01", "2026-05-31")
        if stats:
            lbl_res.config(text=f"Συνολικά Γεγονότα: {stats['total']}\nΕνεργές Συγκρούσεις: {stats['active']}")
            btn_export.config(state="normal")
            window.stats_data = stats
        else:
            lbl_res.config(text="Δεν βρέθηκαν δεδομένα για αυτό το εύρος.")

    tk.Button(window, text="Υπολογισμός Έντασης", command=process_stats, font=("Arial", 10, "bold")).pack(pady=5)

    lbl_res = tk.Label(window, text="", font=("Arial", 11), fg="white", bg="#1a1a1a", justify="center")
    lbl_res.pack(pady=15)

    def current_export():
        if export_statistics_file(window.stats_data, "PDF"):
            messagebox.showinfo("Σύστημα", "Το αρχείο PDF αποθηκεύτηκε επιτυχώς στο Device Storage!")
            window.destroy()

    btn_export = tk.Button(window, text="💾 Εξαγωγή σε PDF (Device Storage)", command=current_export, state="disabled", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
    btn_export.pack(pady=10)