import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from app.services.uc8_service import create_alert_zone, get_user_zones

class AlertScreen(ctk.CTkFrame):
    def __init__(self, master, current_user_id=1, **kwargs):
        # Μοντέρνο απαλό γκρι φόντο για όλη την εφαρμογή
        super().__init__(master, fg_color="#F3F4F6", **kwargs)
        self.user_id = current_user_id

        # Διαδρομή για το λογότυπο
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_dir, "image.png")

        # --- 1. ΜΠΑΡΑ ΠΛΟΗΓΗΣΗΣ (TOP BAR) ---
        self.top_bar = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, height=65)
        self.top_bar.pack(fill="x", side="top")

        # Αριστερό Group (Βελάκι, Μενού, Λογότυπο)
        self.left_top_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.left_top_frame.pack(side="left", fill="y", padx=10)

        self.back_btn = ctk.CTkButton(self.left_top_frame, text="←", width=35, fg_color="transparent", text_color="black", font=ctk.CTkFont(size=24, weight="bold"), hover_color="#E5E7EB")
        self.back_btn.pack(side="left", padx=5)

        self.menu_btn = ctk.CTkButton(self.left_top_frame, text="☰", width=35, fg_color="transparent", text_color="black", font=ctk.CTkFont(size=24), hover_color="#E5E7EB")
        self.menu_btn.pack(side="left", padx=5)

        try:
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(110, 45))
            self.logo_label = ctk.CTkLabel(self.left_top_frame, image=logo_img, text="")
            self.logo_label.pack(side="left", padx=10)
        except FileNotFoundError:
            self.logo_label = ctk.CTkLabel(self.left_top_frame, text="WaryNow", font=ctk.CTkFont(size=20, weight="bold"))
            self.logo_label.pack(side="left", padx=10)

        # Κεντρικό Group (Search Bar)
        self.search_entry = ctk.CTkEntry(self.top_bar, placeholder_text="Αναζήτηση...", width=350, height=35, corner_radius=20, border_width=1, border_color="#D1D5DB", fg_color="#F9FAFB", text_color="black")
        self.search_entry.pack(side="left", expand=True, padx=20)

        # Δεξί Group (Καμπανάκι, Settings)
        self.right_top_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.right_top_frame.pack(side="right", fill="y", padx=10)

        self.bell_btn = ctk.CTkButton(self.right_top_frame, text="🔔", width=40, fg_color="transparent", text_color="black", font=ctk.CTkFont(size=22), hover_color="#E5E7EB", command=self.show_zones_popup)
        self.bell_btn.pack(side="left", padx=10)

        self.settings_btn = ctk.CTkButton(self.right_top_frame, text="Settings", fg_color="#111827", text_color="white", corner_radius=8, width=90, height=35, hover_color="#374151")
        self.settings_btn.pack(side="left", padx=10)

        # --- 2. ΚΕΝΤΡΙΚΟ ΠΕΡΙΕΧΟΜΕΝΟ (2 Στήλες) ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=40, pady=30)
        
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(1, weight=1)

        # --- ΑΡΙΣΤΕΡΗ ΣΤΗΛΗ (Η Φόρμα ως "Κάρτα") ---
        self.left_col = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Λευκή Κάρτα Φόρμας (Modern UI)
        self.form_card = ctk.CTkFrame(self.left_col, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E5E7EB")
        self.form_card.pack(fill="both", expand=True)

        self.title_label = ctk.CTkLabel(self.form_card, text="ΓΕΩΕΙΔΟΠΟΙΗΣΕΙΣ", font=ctk.CTkFont(size=20, weight="bold"), text_color="#111827")
        self.title_label.pack(pady=(30, 20))

        # Στυλ για τα μοντέρνα πεδία
        field_kwargs = {"fg_color": "#F9FAFB", "text_color": "black", "corner_radius": 8, "height": 45, "border_width": 1, "border_color": "#D1D5DB"}

        self.country_entry = ctk.CTkEntry(self.form_card, placeholder_text="Χώρα Ενδιαφέροντος (π.χ. Ουκρανία)", **field_kwargs)
        self.country_entry.pack(pady=15, padx=40, fill="x")

        self.zone_entry = ctk.CTkEntry(self.form_card, placeholder_text="Συντεταγμένες Ζώνης (π.χ. 47.0, 34.0)", **field_kwargs)
        self.zone_entry.pack(pady=15, padx=40, fill="x")

        self.radius_entry = ctk.CTkEntry(self.form_card, placeholder_text="Ακτίνα σε km (π.χ. 50)", **field_kwargs)
        self.radius_entry.pack(pady=15, padx=40, fill="x")

        self.save_btn = ctk.CTkButton(self.form_card, text="Αποθήκευση", fg_color="#2563EB", text_color="white", corner_radius=8, height=45, hover_color="#1D4ED8", font=ctk.CTkFont(size=15, weight="bold"), command=self.add_zone)
        self.save_btn.pack(pady=(20, 40), padx=40, fill="x")

        # --- ΔΕΞΙΑ ΣΤΗΛΗ (Χώρος Υδρογείου) ---
        self.right_col = ctk.CTkFrame(self.main_content, fg_color="#1E293B", corner_radius=15)
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
        
        self.globe_placeholder = ctk.CTkLabel(self.right_col, text="🌍\nΔιαδραστικός Χάρτης\n(Αναμονή δεδομένων...)", text_color="white", font=ctk.CTkFont(size=18, weight="bold"))
        self.globe_placeholder.pack(expand=True)

    def add_zone(self):
        """Λογική Αποθήκευσης Ζώνης"""
        try:
            zone_text = self.zone_entry.get().replace(" ", "")
            lat_str, lng_str = zone_text.split(",")
            lat = float(lat_str)
            lng = float(lng_str)
            radius = float(self.radius_entry.get())
            country = self.country_entry.get() # Διαβάζουμε τη χώρα

            # Στέλνουμε και τη χώρα στο back-end
            success, result = create_alert_zone(self.user_id, lat, lng, radius, country)

            if success:
                messagebox.showinfo("Επιτυχία", "Η ζώνη προστέθηκε! Μπορείτε να τη δείτε πατώντας το καμπανάκι 🔔.")
                self.zone_entry.delete(0, 'end')
                self.radius_entry.delete(0, 'end')
                self.country_entry.delete(0, 'end')
            else:
                messagebox.showerror("Σφάλμα", result)

        except ValueError:
            messagebox.showwarning("Προσοχή", "Εισάγετε συντεταγμένες στη μορφή: 47.0, 34.0")

    def show_zones_popup(self):
        """Το Παράθυρο που ανοίγει όταν πατάς το Καμπανάκι"""
        popup = ctk.CTkToplevel(self)
        popup.title("Οι Ειδοποιήσεις μου")
        popup.geometry("450x350")
        popup.attributes("-topmost", True)
        popup.configure(fg_color="#FFFFFF")

        title = ctk.CTkLabel(popup, text="🔔 Ενεργές Ζώνες", font=ctk.CTkFont(size=18, weight="bold"), text_color="black")
        title.pack(pady=(20, 10))

        textbox = ctk.CTkTextbox(popup, fg_color="#F3F4F6", text_color="black", corner_radius=10, border_width=1, border_color="#E5E7EB")
        textbox.pack(padx=20, pady=10, fill="both", expand=True)

        zones = get_user_zones(self.user_id)
        if not zones:
            textbox.insert("0.0", "Δεν έχετε ενεργές ειδοποιήσεις ακόμα.")
        else:
            for z in zones:
                # Αν υπάρχει χώρα, την τυπώνουμε!
                display_name = z.country if z.country else f"Ζώνη {z.id}"
                zone_info = f"📍 {display_name}\nΚέντρο: ({z.center_lat}, {z.center_lng})\nΑκτίνα: {z.radius_km} km\n{'-'*30}\n"
                textbox.insert("end", zone_info)
        
        textbox.configure(state="disabled")

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("WaryNow - UC8 UI")
    app.geometry("1100x650")
    
    ctk.set_appearance_mode("light") 
    
    alert_screen = AlertScreen(app)
    alert_screen.pack(fill="both", expand=True)

    app.mainloop()