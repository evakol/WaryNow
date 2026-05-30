import customtkinter as ctk
from PIL import Image
import os
from app.services.uc8_service import validate_zone, create_alert_zone, get_user_zones

class AlertScreen(ctk.CTkFrame):
    def __init__(self, master, current_user_id=1, **kwargs):
        super().__init__(master, fg_color="#F3F4F6", **kwargs)
        self.user_id = int(current_user_id) if current_user_id else 1

        # --- 1. TOP BAR ---
        self.top_bar = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, height=65)
        self.top_bar.pack(fill="x", side="top")
        
        self.left_top = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.left_top.pack(side="left", padx=10)
        
        ctk.CTkButton(self.left_top, text="←", width=35, fg_color="transparent", text_color="black", font=ctk.CTkFont(size=24, weight="bold"), hover_color="#E5E7EB").pack(side="left", padx=5)
        ctk.CTkButton(self.left_top, text="☰", width=35, fg_color="transparent", text_color="black", font=ctk.CTkFont(size=24), hover_color="#E5E7EB").pack(side="left", padx=5)
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "image.png")
        try:
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(110, 45))
            ctk.CTkLabel(self.left_top, image=logo_img, text="").pack(side="left", padx=10)
        except:
            ctk.CTkLabel(self.left_top, text="WaryNow", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=10)

        self.right_top = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.right_top.pack(side="right", padx=10)
        ctk.CTkButton(self.right_top, text="🔔", width=40, fg_color="transparent", text_color="black", font=ctk.CTkFont(size=22), hover_color="#E5E7EB", command=self.show_zones_popup).pack(side="left")
        ctk.CTkButton(self.right_top, text="Settings", fg_color="#111827", text_color="white", corner_radius=8, width=80).pack(side="left", padx=10)

        # --- 2. ΚΥΡΙΩΣ ΠΛΑΙΣΙΟ (Διαχωρισμός σε Αριστερά/Δεξιά) ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=30)

        # ΑΡΙΣΤΕΡΑ: Η Φόρμα Εισαγωγής
        self.main_card = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E5E7EB")
        self.main_card.pack(fill="both", expand=True, side="left", padx=(0, 20))

        ctk.CTkLabel(self.main_card, text="ΟΡΙΣΜΟΣ ΖΩΝΗΣ ΕΙΔΟΠΟΙΗΣΗΣ", font=ctk.CTkFont(size=20, weight="bold"), text_color="#111827").pack(pady=20)

        self.country_entry = ctk.CTkEntry(self.main_card, placeholder_text="Όνομα Περιοχής / Χώρας (π.χ. Ουκρανία)", width=350, height=40)
        self.country_entry.pack(pady=10)

        self.lat_entry = ctk.CTkEntry(self.main_card, placeholder_text="Γεωγραφικό Πλάτος (Latitude - π.χ. 50.45)", width=350, height=40)
        self.lat_entry.pack(pady=10)

        self.lng_entry = ctk.CTkEntry(self.main_card, placeholder_text="Γεωγραφικό Μήκος (Longitude - π.χ. 30.52)", width=350, height=40)
        self.lng_entry.pack(pady=10)

        self.radius_entry = ctk.CTkEntry(self.main_card, placeholder_text="Ακτίνα Παρακολούθησης (km - π.w. 100)", width=350, height=40)
        self.radius_entry.pack(pady=10)

        ctk.CTkButton(self.main_card, text="Δημιουργία Ζώνης", font=ctk.CTkFont(size=15, weight="bold"), fg_color="#2563EB", hover_color="#1D4ED8", width=200, height=45, command=self.handle_create_zone).pack(pady=25)

        self.status_label = ctk.CTkLabel(self.main_card, text="", font=ctk.CTkFont(size=13))
        self.status_label.pack(pady=5)

        # ΔΕΞΙΑ: Ο Χάρτης (Η Υδρόγειος)
        import tkintermapview
        self.map_card = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E5E7EB")
        self.map_card.pack(fill="both", expand=True, side="right")

        self.map_widget = tkintermapview.TkinterMapView(self.map_card, corner_radius=15)
        self.map_widget.pack(fill="both", expand=True, padx=10, pady=10)
        self.map_widget.set_zoom(4)
        self.map_widget.set_position(37.9838, 23.7275) # Προεπιλογή Αθήνα

    def handle_create_zone(self):
        country = self.country_entry.get().strip()
        try:
            lat = float(self.lat_entry.get().strip())
            lng = float(self.lng_entry.get().strip())
            radius = float(self.radius_entry.get().strip())
        except ValueError:
            self.status_label.configure(text="❌ Παρακαλώ εισάγετε έγκυρους αριθμούς στα πεδία.", text_color="#EF4444")
            return

        is_valid, msg = validate_zone(lat, lng, radius)
        if not is_valid:
            self.status_label.configure(text=f"❌ {msg}", text_color="#EF4444")
            return

        success = create_alert_zone(self.user_id, lat, lng, radius, country)
        if success:
            self.status_label.configure(text="✅ Η ζώνη ειδοποίησης δημιουργήθηκε με επιτυχία!", text_color="#10B981")
            self.country_entry.delete(0, 'end')
            self.lat_entry.delete(0, 'end')
            self.lng_entry.delete(0, 'end')
            self.radius_entry.delete(0, 'end')
        else:
            self.status_label.configure(text="❌ Αποτυχία αποθήκευσης στη βάση δεδομένων.", text_color="#EF4444")

    def show_zones_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Οι Ειδοποιήσεις μου")
        popup.geometry("450x350")
        popup.attributes("-topmost", True)
        popup.configure(fg_color="#FFFFFF")

        ctk.CTkLabel(popup, text="🔔 Ενεργές Ζώνες", font=ctk.CTkFont(size=18, weight="bold"), text_color="black").pack(pady=(20, 10))
        textbox = ctk.CTkTextbox(popup, fg_color="#F3F4F6", text_color="black", corner_radius=10, border_width=1, border_color="#E5E7EB")
        textbox.pack(padx=20, pady=10, fill="both", expand=True)

        zones = get_user_zones(self.user_id)
        if not zones:
            textbox.insert("0.0", "Δεν έχετε ενεργές ειδοποιήσεις ακόμα.")
        else:
            for z in zones:
                display_name = z.country if z.country else f"Ζώνη {z.id}"
                textbox.insert("end", f"ID: {z.id} | 📍 {display_name}\nΚέντρο: ({z.center_lat}, {z.center_lng})\nΑκτίνα: {z.radius_km} km\n{'-'*30}\n")
        
        textbox.configure(state="disabled")

if __name__ == "__main__":
    from app.models.models import init_db
    init_db()
    app = ctk.CTk()
    app.title("WaryNow - UC8 UI")
    app.geometry("1100x650")
    ctk.set_appearance_mode("light") 
    AlertScreen(app).pack(fill="both", expand=True)
    app.mainloop()