import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta

# ==========================================
#             ENTITY OBJECTS
# ==========================================

class FilterCriteria:
    """Entity: Αποθηκεύει προσωρινά τα κριτήρια αναζήτησης του χρήστη."""
    def __init__(self):
        self.country = ""
        self.intensity = "All"
        self.timeframe = "All time"

    def clear(self):
        self.country = ""
        self.intensity = "All"
        self.timeframe = "All time"


# ==========================================
#             CONTROL OBJECTS
# ==========================================

class FilterLogic:
    """Control Object: Υλοποιεί αποκλειστικά τους κανόνες φιλτραρίσματος."""
    @staticmethod
    def apply_filters(conflicts, criteria):
        filtered = []
        now = datetime.utcnow()

        for c in conflicts:
            # 1. Φίλτρο Χώρας / Τίτλου
            match_country = criteria.country.lower() in c.get('country', '').lower()
            match_title = criteria.country.lower() in c.get('title', '').lower()
            if criteria.country and not (match_country or match_title):
                continue
                
            # 2. Φίλτρο Έντασης
            if criteria.intensity != "All" and c.get('intensity') != criteria.intensity:
                continue
                
            # 3. Φίλτρο Χρονικής Περιόδου (Timeframe)
            created_at = c.get('created_at')
            if created_at and criteria.timeframe != "All time":
                if criteria.timeframe == "Last 24 hours" and now - created_at > timedelta(days=1):
                    continue
                elif criteria.timeframe == "Last 7 days" and now - created_at > timedelta(days=7):
                    continue
                elif criteria.timeframe == "Last 30 days" and now - created_at > timedelta(days=30):
                    continue

            filtered.append(c)
        return filtered

class MapUpdateManager:
    """Control Object: Αναλαμβάνει την οπτική ενημέρωση και εστίαση του χάρτη."""
    def __init__(self, master):
        self.master = master

    def update_map(self, filtered_conflicts, focus_country=None):
        # Βασική Ροή 5: Δυναμική ενημέρωση markers
        self.master.draw_markers(filtered_conflicts)
        
        # Βασική Ροή 6: Εστίαση (Auto-zoom) στη συγκεκριμένη περιοχή
        if focus_country and filtered_conflicts:
            self.simulate_focus(filtered_conflicts)

    def simulate_focus(self, conflicts):
        """Σχεδιάζει ένα οπτικό 'ραντάρ' εστίασης γύρω από τα αποτελέσματα."""
        map_top_lat = 90.0     
        map_bottom_lat = -60.0 
        lat_range = map_top_lat - map_bottom_lat
        
        for c in conflicts:
            x = (c['lng'] + 180) * (self.master.map_width / 360.0)
            y = (map_top_lat - c['lat']) * (self.master.map_height / lat_range)
            
            # Δημιουργία οπτικού "στόχου" γύρω από την επιλεγμένη περιοχή
            self.master.canvas.create_oval(x-20, y-20, x+20, y+20, outline="#3B82F6", width=2, dash=(4, 4), tags="marker")
            self.master.canvas.create_oval(x-30, y-30, x+30, y+30, outline="#60A5FA", width=1, dash=(2, 4), tags="marker")


class SearchFilterController:
    """
    Control Object: Ο κεντρικός ελεγκτής του UC5 (SearchController).
    Διαχειρίζεται τη διεπαφή (Boundaries) και συντονίζει τα υπόλοιπα Controls.
    """
    def __init__(self, master):
        self.master = master
        self.current_criteria = FilterCriteria()
        self.map_manager = MapUpdateManager(master)

    def apply_text_search(self, event=None):
        """Εκτελείται από τη μπάρα αναζήτησης της Αρχικής Οθόνης (Enter key)."""
        query = self.master.search_entry.get().strip()
        
        # Αποθήκευση στο Entity
        self.current_criteria.clear()
        self.current_criteria.country = query
        
        # Αν η αναζήτηση είναι κενή, επαναφορά
        if not query:
            self.master.current_displayed_conflicts = self.master.all_conflicts
            self.map_manager.update_map(self.master.current_displayed_conflicts)
            return

        # Εκτέλεση Λογικής
        filtered = FilterLogic.apply_filters(self.master.all_conflicts, self.current_criteria)
        self.master.current_displayed_conflicts = filtered
        
        # Ενημέρωση χάρτη με εστίαση (Auto-zoom)
        self.map_manager.update_map(filtered, focus_country=query)
        
        # Εναλλακτική Ροή 1
        if not filtered:
            messagebox.showinfo("Αναζήτηση", "Δεν βρέθηκαν συγκρούσεις ή γεγονότα για τη λέξη που δώσατε.")

    def open_filters_popup(self):
        """Boundary Object: Το αναδυόμενο παράθυρο φίλτρων (FilterPanel)."""
        popup = ctk.CTkToplevel(self.master)
        popup.title("Φίλτρα Αναζήτησης")
        popup.geometry("350x420")
        popup.attributes("-topmost", True)
        popup.configure(fg_color="#FFFFFF")
        
        # --- UI Elements ---
        ctk.CTkLabel(popup, text="Χώρα / Τοποθεσία:", text_color="black", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        country_entry = ctk.CTkEntry(popup, placeholder_text="π.χ. Syria", border_color="#E5E7EB")
        country_entry.insert(0, self.current_criteria.country)
        country_entry.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(popup, text="Επίπεδο Έντασης:", text_color="black", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        intensity_var = ctk.StringVar(value=self.current_criteria.intensity)
        ctk.CTkComboBox(popup, values=["All", "Low", "Medium", "High"], variable=intensity_var, border_color="#E5E7EB").pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(popup, text="Χρονική Περίοδος:", text_color="black", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        timeframe_var = ctk.StringVar(value=self.current_criteria.timeframe)
        ctk.CTkComboBox(popup, values=["All time", "Last 24 hours", "Last 7 days", "Last 30 days"], variable=timeframe_var, border_color="#E5E7EB").pack(pady=5, padx=20, fill="x")

        def execute_search():
            """Βασική Ροή: Εφαρμογή Φίλτρων"""
            self.current_criteria.country = country_entry.get().strip()
            self.current_criteria.intensity = intensity_var.get()
            self.current_criteria.timeframe = timeframe_var.get()
            
            filtered = FilterLogic.apply_filters(self.master.all_conflicts, self.current_criteria)
            self.master.current_displayed_conflicts = filtered
            
            # Ενημέρωση και εστίαση
            self.map_manager.update_map(filtered, focus_country=self.current_criteria.country)
            
            if not filtered:
                messagebox.showinfo("Φίλτρα", "Δεν βρέθηκαν αποτελέσματα με αυτά τα κριτήρια.")
            popup.destroy()

        def clear_filters():
            """Εναλλακτική Ροή 3: Επαναφορά/Εκκαθάριση Φίλτρων"""
            self.current_criteria.clear()
            self.master.current_displayed_conflicts = self.master.all_conflicts
            self.master.search_entry.delete(0, 'end') 
            self.map_manager.update_map(self.master.all_conflicts)
            popup.destroy()

        # --- Κουμπιά Ελέγχου ---
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=25)
        
        ctk.CTkButton(btn_frame, text="Εφαρμογή", font=ctk.CTkFont(weight="bold"), command=execute_search, width=120).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Καθαρισμός", font=ctk.CTkFont(weight="bold"), fg_color="#EF4444", hover_color="#DC2626", command=clear_filters, width=120).pack(side="left", padx=10)