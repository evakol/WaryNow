import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import sqlite3

DB_FILE = "warynow.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            pronouns TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def username_exists(username, exclude=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if exclude:
        cursor.execute("SELECT 1 FROM users WHERE username = ? AND username != ?", (username, exclude))
    else:
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def update_username(old_username, new_username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, old_username))
    conn.commit()
    conn.close()

def update_password(username, new_password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()

def update_pronouns(username, new_pronouns):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET pronouns = ? WHERE username = ?", (new_pronouns, username))
    conn.commit()
    conn.close()

def check_password(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

class SettingsScreen(ctk.CTk):
    def __init__(self, username="guest"):
        super().__init__()
        self.title("WaryNow - Settings")
        self.geometry("900x650")
        self.resizable(False, False)
        self.username = username
        init_db()
        self.build_ui()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="white", height=70, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Πίσω βέλος
        ctk.CTkButton(header, text="←", width=40, fg_color="white",
                      text_color="black", hover_color="#dddddd",
                      command=self.go_back, font=("Arial", 18)).pack(side="left", padx=5)

        # Hamburger menu
        ctk.CTkButton(header, text="≡", width=40, fg_color="white",
                      text_color="black", hover_color="#dddddd",
                      font=("Arial", 18)).pack(side="left", padx=5)

        # Logo με border
        logo_frame = ctk.CTkFrame(header, fg_color="white", border_color="gray",
                                   border_width=1, corner_radius=5)
        logo_frame.pack(side="left", padx=5, pady=5)
        try:
            logo_img = Image.open("C:\\Users\\evako\\Downloads\\image.png")
            self.logo = ctk.CTkImage(light_image=logo_img, size=(80, 50))
            ctk.CTkLabel(logo_frame, image=self.logo, text="", fg_color="white").pack(padx=5, pady=5)
        except Exception as e:
            ctk.CTkLabel(logo_frame, text="WaryNow", fg_color="white",
                         text_color="black", font=("Arial", 12, "bold")).pack(padx=5, pady=5)

        # Search bar
        search = ctk.CTkEntry(header, placeholder_text="Search bar", width=400,
                               fg_color="black", text_color="white",
                               border_color="black")
        search.pack(side="left", padx=20)

        # Settings button
        ctk.CTkButton(header, text="Settings", width=100, fg_color="black",
                      text_color="white", hover_color="#333333").pack(side="right", padx=10)

        # Κουδουνάκι με border
        bell_frame = ctk.CTkFrame(header, fg_color="white", border_color="black",
                                   border_width=2, corner_radius=5)
        bell_frame.pack(side="right", padx=5, pady=5)
        try:
            bell_img = Image.open("C:\\Users\\evako\\Downloads\\image 2.png")
            self.bell = ctk.CTkImage(light_image=bell_img, size=(60, 40))
            ctk.CTkLabel(bell_frame, image=self.bell, text="", fg_color="white").pack(padx=5, pady=5)
        except Exception as e:
            ctk.CTkLabel(bell_frame, text="🔔", fg_color="white",
                         text_color="black", font=("Arial", 18)).pack(padx=5, pady=5)

        # Main content
        content = ctk.CTkFrame(self, fg_color="white")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(content, text="Settings", font=("Arial", 24, "bold"),
                     text_color="black").pack(pady=15)

        # Tabview για κατηγορίες
        tabview = ctk.CTkTabview(content, width=800, fg_color="white",
                                  segmented_button_fg_color="black",
                                  segmented_button_selected_color="gray",
                                  segmented_button_unselected_color="black",
                                  segmented_button_selected_hover_color="darkgray",
                                  text_color="white")
        tabview.pack(pady=10)

        tabview.add("Προφίλ")
        tabview.add("Λογαριασμός")
        tabview.add("Σχετικά")

        # --- Προφίλ Tab ---
        profile_tab = tabview.tab("Προφίλ")

        ctk.CTkLabel(profile_tab, text="Νέο Username:", text_color="black").pack(pady=5)
        self.new_username_entry = ctk.CTkEntry(profile_tab, placeholder_text="Νέο username",
                                                width=300, fg_color="white", text_color="black")
        self.new_username_entry.pack(pady=5)

        ctk.CTkLabel(profile_tab, text="Νέες Αντωνυμίες:", text_color="black").pack(pady=5)
        self.new_pronouns_entry = ctk.CTkEntry(profile_tab, placeholder_text="Νέες αντωνυμίες",
                                                width=300, fg_color="white", text_color="black")
        self.new_pronouns_entry.pack(pady=5)

        ctk.CTkButton(profile_tab, text="Αποθήκευση Αλλαγών",
                      command=self.save_profile,
                      fg_color="black", text_color="white",
                      hover_color="#333333", width=250).pack(pady=15)

        # --- Λογαριασμός Tab ---
        account_tab = tabview.tab("Λογαριασμός")

        ctk.CTkLabel(account_tab, text="Τρέχων Κωδικός:", text_color="black").pack(pady=5)
        self.current_password_entry = ctk.CTkEntry(account_tab, placeholder_text="Τρέχων κωδικός",
                                                    show="*", width=300,
                                                    fg_color="white", text_color="black")
        self.current_password_entry.pack(pady=5)

        ctk.CTkLabel(account_tab, text="Νέος Κωδικός:", text_color="black").pack(pady=5)
        self.new_password_entry = ctk.CTkEntry(account_tab, placeholder_text="Νέος κωδικός",
                                                show="*", width=300,
                                                fg_color="white", text_color="black")
        self.new_password_entry.pack(pady=5)

        ctk.CTkLabel(account_tab, text="Νέο Email:", text_color="black").pack(pady=5)
        self.new_email_entry = ctk.CTkEntry(account_tab, placeholder_text="Νέο email",
                                             width=300, fg_color="white", text_color="black")
        self.new_email_entry.pack(pady=5)

        ctk.CTkButton(account_tab, text="Αποθήκευση Αλλαγών",
                      command=self.save_account,
                      fg_color="black", text_color="white",
                      hover_color="#333333", width=250).pack(pady=15)

        # --- Σχετικά Tab ---
        about_tab = tabview.tab("Σχετικά")
        ctk.CTkLabel(about_tab, text="WaryNow v1.0", font=("Arial", 16, "bold"),
                     text_color="black").pack(pady=20)
        ctk.CTkLabel(about_tab, text="Εφαρμογή ενημέρωσης για επικίνδυνα γεγονότα παγκοσμίως.",
                     text_color="black").pack(pady=5)

    def save_profile(self):
        new_username = self.new_username_entry.get()
        new_pronouns = self.new_pronouns_entry.get()

        if new_username:
            if username_exists(new_username, exclude=self.username):
                messagebox.showerror("Σφάλμα", "Το username χρησιμοποιείται ήδη!")
                return
            update_username(self.username, new_username)
            self.username = new_username
            messagebox.showinfo("Επιτυχία", "Το username άλλαξε επιτυχώς!")

        if new_pronouns:
            update_pronouns(self.username, new_pronouns)
            messagebox.showinfo("Επιτυχία", "Οι αντωνυμίες άλλαξαν επιτυχώς!")

    def save_account(self):
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()

        if new_password:
            if not current_password:
                messagebox.showerror("Σφάλμα", "Εισάγετε τον τρέχοντα κωδικό!")
                return
            if not check_password(self.username, current_password):
                messagebox.showerror("Σφάλμα", "Λάθος τρέχων κωδικός!")
                return
            update_password(self.username, new_password)
            messagebox.showinfo("Επιτυχία", "Ο κωδικός άλλαξε επιτυχώς!")

    def go_back(self):
        self.destroy()

if __name__ == "__main__":
    app = SettingsScreen(username="test_user")
    app.mainloop()