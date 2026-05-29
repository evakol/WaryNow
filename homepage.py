import customtkinter as ctk
from tkinter import messagebox, Canvas
from PIL import Image, ImageTk
import subprocess
import sys
import random
import socket  
from datetime import datetime, timedelta  # Προσθήκη για τη διαχείριση χρόνου του UC5

# --- Ενσωμάτωση Βάσης Δεδομένων (SQLAlchemy) ---
try:
    from app.models.models import Session, Conflict, RawReport
    DB_CONNECTED = True
except ImportError:
    DB_CONNECTED = False
    print("⚠️ Το app.models.models δεν βρέθηκε. Ενεργοποίηση Mock Δεδομένων.")

# --- Ενσωμάτωση του UC5 (Search & Filter) ---
try:
    from uc5_search_filter import SearchFilterController
    UC5_AVAILABLE = True
except ImportError:
    UC5_AVAILABLE = False
    print("⚠️ Το αρχείο uc5_search_filter.py δεν βρέθηκε.")

# --- Ενσωμάτωση του UC10 & UC11 (Ελπίδα) ---
try:
    from uc10_ui import run_background_moderation_check
    from uc11_ui import open_statistics_window
    UC10_11_AVAILABLE = True
except ImportError:
    UC10_11_AVAILABLE = False


class WaryNowHomepage(ctk.CTk):
    def __init__(self, current_user_id=None):
        super().__init__()
        self.user_id = current_user_id
        
        self.title("WaryNow - Κεντρικό Σύστημα & Παγκόσμιος Χάρτης")
        self.geometry("1350x850")
        self.configure(fg_color="#F3F4F6")

        # Έλεγχος Σύνδεσης στο Διαδίκτυο
        self.is_offline = not self.check_internet_connection()

        self.map_width = 800
        self.map_height = 500
        self.map_photo = None
        self.original_map_img = None
        self.is_menu_open = False
        
        self.all_conflicts = []
        self.current_displayed_conflicts = []

        # Στήσιμο Διεπαφών (Boundary Objects)
        self.setup_menu_bar()       
        self.setup_left_menu()      
        self.setup_right_feed()     
        self.setup_world_map()      
        
        try:
            self.original_map_img = Image.open("WorldMap.png")
        except Exception as e:
            print(f"⚠️ Σφάλμα φόρτωσης WorldMap.png: {e}")

        # Φόρτωση Δεδομένων Χάρτη
        self.load_map_data()

        # Έλεγχος Κρίσιμων Alerts κατά την εκκίνηση
        self.after(1000, self.trigger_critical_alerts)

    # ==========================================
    #             BOUNDARY SETUP
    # ==========================================

    def setup_menu_bar(self):
        """Top Bar: Περιέχει το κύριο μενού πλοήγησης (Menu Bar Boundary)"""
        self.top_bar = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, height=65)
        self.top_bar.pack(fill="x", side="top")

        # Αριστερά: Μενού & Λογότυπο
        self.left_top = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.left_top.pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(self.left_top, text="☰", width=35, fg_color="transparent", 
                      text_color="black", font=ctk.CTkFont(size=24), command=self.toggle_left_menu).pack(side="left", padx=5)
        
        try:
            logo_img = ctk.CTkImage(light_image=Image.open("image.png"), dark_image=Image.open("image.png"), size=(40, 40))
            ctk.CTkLabel(self.left_top, image=logo_img, text="").pack(side="left", padx=5)
        except: pass
        
        ctk.CTkLabel(self.left_top, text="WaryNow", font=ctk.CTkFont(size=22, weight="bold"), text_color="black").pack(side="left", padx=5)

        # Κέντρο: Search Bar & Filters (UC5)
        self.search_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.search_frame.pack(side="left", expand=True, fill="x", padx=50)
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="⌕ Αναζήτηση χώρας ή γεγονότος...", height=35, corner_radius=20)
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        self.filter_btn = ctk.CTkButton(self.search_frame, text="⚙ Φίλτρα", width=80, height=35, corner_radius=20)
        self.filter_btn.pack(side="left")

        if UC5_AVAILABLE:
            self.search_controller = SearchFilterController(self)
            self.search_entry.bind("<Return>", self.search_controller.apply_text_search)
            self.filter_btn.configure(command=self.search_controller.open_filters_popup)

        # Δεξιά: Ειδοποιήσεις, Ρυθμίσεις & Αποσύνδεση
        self.right_top = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.right_top.pack(side="right", padx=10, pady=10)

        ctk.CTkButton(self.right_top, text="🔔", width=40, fg_color="#E5E7EB", text_color="black", 
                      font=ctk.CTkFont(size=18), command=self.handle_alerts_click).pack(side="left", padx=5)
        
        ctk.CTkButton(self.right_top, text="⚙", width=40, fg_color="#E5E7EB", text_color="black", 
                      font=ctk.CTkFont(size=18), command=self.open_settings).pack(side="left", padx=5)
                      
        logout_btn = ctk.CTkButton(self.right_top, text="🚪 Έξοδος", width=80, fg_color="#EF4444", text_color="white", 
                                   hover_color="#DC2626", font=ctk.CTkFont(weight="bold"), command=self.handle_logout)
        logout_btn.pack(side="left", padx=15)
        
        if not self.user_id:
            logout_btn.configure(text="Σύνδεση", fg_color="#3B82F6", hover_color="#2563EB", command=self.go_to_login)

    def setup_left_menu(self):
        """Αριστερό πάνελ για πλοήγηση στις λοιπές λειτουργίες (Menu Bar Boundary)"""
        self.left_menu = ctk.CTkFrame(self, width=220, fg_color="#FFFFFF", corner_radius=0)
        self.left_menu.pack_propagate(False)

        ctk.CTkLabel(self.left_menu, text="Λειτουργίες", font=ctk.CTkFont(size=16, weight="bold"), text_color="black").pack(pady=20)
        
        self.stats_btn = ctk.CTkButton(self.left_menu, text="📊 Στατιστικά", fg_color="#E5E7EB", text_color="black", anchor="w")
        self.stats_btn.pack(fill="x", padx=15, pady=10)
        
        self.mod_btn = ctk.CTkButton(self.left_menu, text="🛡️ Moderation", fg_color="#E5E7EB", text_color="black", anchor="w")
        self.mod_btn.pack(fill="x", padx=15, pady=10)

        self.sources_btn = ctk.CTkButton(self.left_menu, text="🌐 Πηγές Δεδομένων", fg_color="#E5E7EB", text_color="black", anchor="w", command=self.handle_sources)
        self.sources_btn.pack(fill="x", padx=15, pady=10)

        if UC10_11_AVAILABLE:
            self.stats_btn.configure(command=self.handle_statistics)
            self.mod_btn.configure(command=self.handle_moderation)

    def toggle_left_menu(self):
        if self.is_menu_open:
            self.left_menu.pack_forget()
            self.is_menu_open = False
        else:
            self.left_menu.pack(side="left", fill="y", before=self.map_container)
            self.is_menu_open = True

    def setup_right_feed(self):
        """Ροή Ειδήσεων (UC6 Integration)"""
        self.right_feed = ctk.CTkFrame(self, width=300, fg_color="#FFFFFF", corner_radius=0)
        self.right_feed.pack(side="right", fill="y")
        self.right_feed.pack_propagate(False)

        feed_title = "📰 Ροή Ειδήσεων" if not self.is_offline else "📰 Ροή (Offline Cache)"
        color = "black" if not self.is_offline else "#EF4444"
        
        ctk.CTkLabel(self.right_feed, text=feed_title, font=ctk.CTkFont(size=18, weight="bold"), text_color=color).pack(pady=(20, 10))
        self.news_scroll = ctk.CTkScrollableFrame(self.right_feed, fg_color="transparent")
        self.news_scroll.pack(expand=True, fill="both", padx=10, pady=10)

    def setup_world_map(self):
        """Κεντρικό Boundary (World Map)"""
        self.map_container = ctk.CTkFrame(self, fg_color="#A4D3EE") 
        self.map_container.pack(side="left", expand=True, fill="both")

        self.canvas = Canvas(self.map_container, bg="#A4D3EE", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        
        self.canvas.bind("<Configure>", self.on_map_resize)
        self.canvas.bind("<Button-1>", self.on_map_click)

    # ==========================================
    #          CONTROLLER / DATA LOGIC
    # ==========================================

    def check_internet_connection(self):
        try:
            socket.create_connection(("1.1.1.1", 53), timeout=2)
            return True
        except OSError:
            return False

    def load_map_data(self):
        """Ανάκτηση δεδομένων (MapDataManager Control Object)"""
        self.all_conflicts = []
        
        if self.is_offline:
            messagebox.showwarning("Εκτός Σύνδεσης", "Δεν υπάρχει σύνδεση στο διαδίκτυο.\nΦορτώνονται τα τελευταία αποθηκευμένα (cached) δεδομένα.")
            self.use_mock_conflicts()
        elif DB_CONNECTED:
            session = Session()
            conflicts_db = session.query(Conflict).filter_by(status="active").all()
            session.close()
            
            if not conflicts_db:
                self.use_mock_conflicts() 
            else:
                for c in conflicts_db:
                    intensity_val = getattr(c, 'intensity', None) or random.choice(["Low", "Medium", "High"])
                    country_val = getattr(c, 'country', None) or (c.title.split()[0] if c.title else "Άγνωστη")
                    lat = c.latitude if c.latitude else random.uniform(-60, 70)
                    lng = c.longitude if c.longitude else random.uniform(-150, 150)
                    
                    # Προσθήκη του πεδίου created_at για τη σωστή λειτουργία του χρονικού φίλτρου του UC5
                    self.all_conflicts.append({
                        "title": c.title, 
                        "intensity": intensity_val, 
                        "country": country_val, 
                        "lat": lat, 
                        "lng": lng,
                        "created_at": getattr(c, 'created_at', None)
                    })
        else:
            self.use_mock_conflicts()
        
        self.current_displayed_conflicts = self.all_conflicts
        self.load_news_feed()
        self.draw_markers(self.current_displayed_conflicts)

    def use_mock_conflicts(self):
        """Δημιουργία mock δεδομένων με κλιμακούμενες ημερομηνίες για δοκιμή των φίλτρων χρόνου"""
        now = datetime.utcnow()
        self.all_conflicts = [
            {"title": "Ένοπλη Σύρραξη", "intensity": "High", "country": "Ukraine", "lat": 49.0, "lng": 31.0, "created_at": now - timedelta(hours=4)},
            {"title": "Συνοριακή Ένταση", "intensity": "Medium", "country": "Syria", "lat": 34.8, "lng": 38.9, "created_at": now - timedelta(days=3)},
            {"title": "Διαδήλωση", "intensity": "Low", "country": "France", "lat": 46.2, "lng": 2.2, "created_at": now - timedelta(days=12)},
            {"title": "Ναυτικό Επεισόδιο", "intensity": "Medium", "country": "Taiwan", "lat": 23.5, "lng": 121.0, "created_at": now - timedelta(days=45)}
        ]

    def load_news_feed(self):
        for widget in self.news_scroll.winfo_children(): 
            widget.destroy()

        news_items = []
        if DB_CONNECTED and not self.is_offline:
            session = Session()
            reports = session.query(RawReport).order_by(RawReport.created_at.desc()).limit(15).all()
            session.close()
            for r in reports:
                news_items.append({"title": r.title, "source": r.source})

        if not news_items:
            news_items = [
                {"title": "ΟΗΕ: Νέα έκκληση για εκεχειρία και αποστολή ανθρωπιστικής βοήθειας.", "source": "Reuters"}, 
                {"title": "Αυξημένη στρατιωτική κινητικότητα εντοπίστηκε από δορυφόρους.", "source": "CNN"}
            ]

        for item in news_items:
            card = ctk.CTkFrame(self.news_scroll, fg_color="#F3F4F6", corner_radius=8)
            card.pack(fill="x", pady=5)
            ctk.CTkLabel(card, text=item['title'], font=ctk.CTkFont(weight="bold"), text_color="black", wraplength=250, justify="left").pack(anchor="w", padx=10, pady=(10, 0))
            ctk.CTkLabel(card, text=f"Πηγή: {item['source']}", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=10, pady=(0, 10))

    # ==========================================
    #            MAP RENDERING LOGIC
    # ==========================================

    def on_map_resize(self, event):
        if not self.original_map_img: return
        self.map_width = event.width
        self.map_height = event.height
        
        resized_img = self.original_map_img.resize((self.map_width, self.map_height), Image.Resampling.LANCZOS)
        self.map_photo = ImageTk.PhotoImage(resized_img)
        
        self.canvas.delete("background")
        self.canvas.create_image(0, 0, image=self.map_photo, anchor="nw", tags="background")
        self.draw_markers(self.current_displayed_conflicts)

    def draw_markers(self, conflicts_to_draw):
        self.canvas.delete("marker")
        
        map_top_lat = 85.0     
        map_bottom_lat = -90.0 
        lat_range = map_top_lat - map_bottom_lat
        
        for c in conflicts_to_draw:
            x = (c['lng'] + 180) * (self.map_width / 360.0)
            y = (map_top_lat - c['lat']) * (self.map_height / lat_range)
            
            color = "green" if c['intensity'] == "Low" else "yellow" if c['intensity'] == "Medium" else "red"
            self.canvas.create_oval(x-7, y-7, x+7, y+7, fill=color, outline="black", width=2, tags="marker")

    def on_map_click(self, event):
        map_top_lat = 85.0
        map_bottom_lat = -90.0
        lat_range = map_top_lat - map_bottom_lat

        clicked_lng = (event.x / self.map_width) * 360.0 - 180
        clicked_lat = map_top_lat - (event.y / self.map_height) * lat_range
        
        found = [c for c in self.current_displayed_conflicts if abs(c['lat'] - clicked_lat) < 5 and abs(c['lng'] - clicked_lng) < 5]
        if found:
            titles = "\n".join([f"• {c['title']} (Ένταση: {c['intensity']})" for c in found])
            messagebox.showinfo("Γεωγραφική Περιοχή", f"Συγκρούσεις στην περιοχή:\n{titles}")

    # ==========================================
    #     NAVIGATION & ALTERNATIVE FLOWS
    # ==========================================

    def trigger_critical_alerts(self):
        """Εμφάνιση Pop-Up αν υπάρχουν συμβάντα High Intensity κατά την είσοδο"""
        if self.user_id:
            high_conflicts = [c for c in self.all_conflicts if c['intensity'] == "High"]
            if high_conflicts:
                messagebox.showwarning("⚠️ Κρίσιμη Γεωειδοποίηση", 
                                       "Εντοπίστηκαν νέες συγκρούσεις Υψηλής Έντασης (High Intensity) κοντά στις περιοχές ενδιαφέροντός σας!\n\n"
                                       "Ο χάρτης έχει ενημερωθεί με κόκκινους δείκτες.")

    def handle_logout(self):
        if messagebox.askyesno("Αποσύνδεση", "Είστε σίγουροι ότι θέλετε να αποσυνδεθείτε από το σύστημα;"):
            self.destroy()
            try:
                subprocess.Popen([sys.executable, "Login.py"])
            except:
                pass

    def go_to_login(self):
        self.destroy()
        try:
            subprocess.Popen([sys.executable, "Login.py"])
        except: pass

    def handle_sources(self):
        if not self.user_id:
            self.show_guest_warning()
            return
        messagebox.showinfo("Πηγές Δεδομένων", "Άνοιγμα διαχείρισης πηγών GDELT API (UC6 Configuration).")

    def open_settings(self):
        if not self.user_id:
            self.show_guest_warning()
            return
        subprocess.Popen([sys.executable, "Settings.py"])

    def handle_alerts_click(self):
        if not self.user_id:
            self.show_guest_warning()
            return
        subprocess.Popen([sys.executable, "uc8_ui.py"])

    def handle_statistics(self):
        if not self.user_id:
            self.show_guest_warning()
            return
        open_statistics_window()

    def handle_moderation(self):
        if not self.user_id:
            self.show_guest_warning()
            return
        result = run_background_moderation_check()
        if result == "No reports to moderate":
            messagebox.showinfo("Moderation", "Δεν βρέθηκαν εκκρεμείς αναφορές προς έλεγχο.")
        else:
            messagebox.showinfo("Moderation", "Ο έλεγχος ολοκληρώθηκε στο παρασκήνιο.\nΑναλυτικά αποτελέσματα εκτυπώθηκαν στο Terminal.")

    def show_guest_warning(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Απαιτείται Σύνδεση")
        popup.geometry("450x280")
        popup.attributes("-topmost", True)
        popup.configure(fg_color="#FFFFFF")
        
        ctk.CTkLabel(popup, text="Μην Χάνετε Τίποτα!", font=ctk.CTkFont(size=20, weight="bold"), text_color="black").pack(pady=(20,10))
        msg = "Φαίνεται ότι δεν έχετε συνδεθεί.\nΓια πρόσβαση σε αυτή τη λειτουργία, απαιτείται λογαριασμός χρήστη."
        ctk.CTkLabel(popup, text=msg, font=ctk.CTkFont(size=13), text_color="black").pack(pady=10)
        
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Sign Up", command=lambda: self.go_to_signup(popup)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Ακύρωση", fg_color="#E5E7EB", text_color="black", command=popup.destroy).pack(side="left", padx=10)

    def go_to_signup(self, popup_window):
        popup_window.destroy()
        self.destroy()
        subprocess.Popen([sys.executable, "SignUp.py"])


if __name__ == "__main__":
    user_arg = sys.argv[1] if len(sys.argv) > 1 else None
    app = WaryNowHomepage(current_user_id=user_arg) 
    app.mainloop()