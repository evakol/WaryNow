import customtkinter as ctk
from PIL import Image
import os
from app.services.uc9_service import filter_by_category
from app.services.uc8_service import get_user_zones

class InfrastructureScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#F3F4F6", **kwargs)

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

        # Καμπανάκι (Σύνδεση με popup)
        self.right_top = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.right_top.pack(side="right", padx=10)
        ctk.CTkButton(self.right_top, text="🔔", width=40, fg_color="transparent", text_color="black", font=ctk.CTkFont(size=22), hover_color="#E5E7EB", command=self.show_zones_popup).pack(side="left")
        ctk.CTkButton(self.right_top, text="Settings", fg_color="#111827", text_color="white", corner_radius=8, width=80).pack(side="left", padx=10)

        # --- 2. ΚΕΝΤΡΙΚΟ ΠΕΡΙΕΧΟΜΕΝΟ ---
        self.main_card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E5E7EB")
        self.main_card.pack(fill="both", expand=True, padx=40, pady=30)

        ctk.CTkLabel(self.main_card, text="ΚΑΤΑΛΟΓΟΣ ΚΡΙΣΙΜΩΝ ΥΠΟΔΟΜΩΝ", font=ctk.CTkFont(size=20, weight="bold"), text_color="#111827").pack(pady=20)

        self.filter_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.filter_frame.pack(pady=10)

        self.id_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Zone ID", width=150)
        self.id_entry.pack(side="left", padx=10)

        self.category_var = ctk.StringVar(value="Όλες")
        self.filter_menu = ctk.CTkOptionMenu(self.filter_frame, values=["Όλες", "Στρατιωτικές", "Πολιτικές"], variable=self.category_var, width=150)
        self.filter_menu.pack(side="left", padx=10)

        ctk.CTkButton(self.filter_frame, text="Αναζήτηση", command=self.load_infrastructure, fg_color="#2563EB", hover_color="#1D4ED8").pack(side="left", padx=10)

        self.list_textbox = ctk.CTkTextbox(self.main_card, fg_color="#F9FAFB", height=300, border_width=1, border_color="#D1D5DB")
        self.list_textbox.pack(pady=20, padx=40, fill="both", expand=True)

    def load_infrastructure(self):
        cat = self.category_var.get()
        results = filter_by_category(cat)
        
        self.list_textbox.configure(state="normal")
        self.list_textbox.delete("1.0", "end")
        
        if not results:
            self.list_textbox.insert("0.0", "Δεν βρέθηκαν υποδομές για αυτή την κατηγορία.")
        else:
            for item in results:
                self.list_textbox.insert("end", f"🏗️ {item.name}\nΚατηγορία: {item.category}\nΚατάσταση: {item.status}\n{'-'*40}\n")
        
        self.list_textbox.configure(state="disabled")

    def show_zones_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Οι Ειδοποιήσεις μου")
        popup.geometry("450x350")
        popup.attributes("-topmost", True)
        popup.configure(fg_color="#FFFFFF")

        ctk.CTkLabel(popup, text="🔔 Ενεργές Ζώνες", font=ctk.CTkFont(size=18, weight="bold"), text_color="black").pack(pady=(20, 10))
        textbox = ctk.CTkTextbox(popup, fg_color="#F3F4F6", text_color="black", corner_radius=10)
        textbox.pack(padx=20, pady=10, fill="both", expand=True)

        zones = get_user_zones(1) # Υποθέτουμε subscriber_id = 1
        if not zones:
            textbox.insert("0.0", "Δεν έχετε ενεργές ειδοποιήσεις.")
        else:
            for z in zones:
                display_name = z.country if z.country else f"Ζώνη {z.id}"
                textbox.insert("end", f"ID: {z.id} | 📍 {display_name}\nΚέντρο: ({z.center_lat}, {z.center_lng})\nΑκτίνα: {z.radius_km} km\n{'-'*30}\n")
        textbox.configure(state="disabled")

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("900x600")
    ctk.set_appearance_mode("light")
    InfrastructureScreen(app).pack(fill="both", expand=True)
    app.mainloop()