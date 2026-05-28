import customtkinter as ctk
from tkinter import messagebox, PhotoImage
import sqlite3
import subprocess
import sys

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

def username_exists(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_user(email, username, password, pronouns):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (email, username, password, pronouns) VALUES (?, ?, ?, ?)",
        (email, username, password, pronouns)
    )
    conn.commit()
    conn.close()

class SignUpScreen(ctk.CTk):
    def __init__(self, on_success=None):
        super().__init__()
        self.title("WaryNow - Sign Up")
        self.geometry("900x600")
        self.resizable(False, False)
        self.on_success = on_success
        init_db()
        self.build_ui()

    def build_ui(self):
        left_frame = ctk.CTkFrame(self, fg_color="black", width=450, height=600, corner_radius=0)
        left_frame.pack(side="left", fill="both")
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="Sign Up", font=("Arial", 22, "bold"),
                     text_color="black", fg_color="white", width=200,
                     corner_radius=5).pack(pady=30)

        self.email_entry = ctk.CTkEntry(left_frame, placeholder_text="Email", width=300,
                                         fg_color="white", text_color="black")
        self.email_entry.pack(pady=8)

        self.username_entry = ctk.CTkEntry(left_frame, placeholder_text="Username", width=300,
                                            fg_color="white", text_color="black")
        self.username_entry.pack(pady=8)

        self.pronouns_entry = ctk.CTkEntry(left_frame, placeholder_text="Pronouns", width=300,
                                            fg_color="white", text_color="black")
        self.pronouns_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(left_frame, placeholder_text="Password", show="*",
                                            width=300, fg_color="white", text_color="black")
        self.password_entry.pack(pady=8)

        self.confirm_entry = ctk.CTkEntry(left_frame, placeholder_text="Confirm Password", show="*",
                                           width=300, fg_color="white", text_color="black")
        self.confirm_entry.pack(pady=8)

        ctk.CTkButton(left_frame, text="Δημιουργία Λογαριασμού", command=self.create_account,
                      width=250, fg_color="white", text_color="black",
                      hover_color="lightgray").pack(pady=10)

        ctk.CTkButton(left_frame, text="Είσοδος σαν Επισκέπτης", command=self.enter_as_guest,
                      width=250, fg_color="white", text_color="black",
                      hover_color="lightgray").pack(pady=5)

        ctk.CTkButton(left_frame, text="Log In", command=self.back_to_login,
                      width=250, fg_color="white", text_color="black",
                      hover_color="lightgray").pack(pady=5)

        right_frame = ctk.CTkFrame(self, fg_color="white", width=450, height=600, corner_radius=0)
        right_frame.pack(side="right", fill="both", expand=True)
        right_frame.pack_propagate(False)

        try:
            self.logo = PhotoImage(file="C:\\Users\\evako\\Downloads\\image.png")
            logo_label = ctk.CTkLabel(right_frame, image=self.logo, text="")
            logo_label.pack(expand=True)
        except Exception as e:
            ctk.CTkLabel(right_frame, text="WaryNow", font=("Arial", 40, "bold"),
                         text_color="black").pack(expand=True)

    def create_account(self):
        email = self.email_entry.get()
        username = self.username_entry.get()
        pronouns = self.pronouns_entry.get()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if not email or not username or not password or not confirm:
            messagebox.showerror("Σφάλμα", "Παρακαλώ συμπληρώστε όλα τα πεδία!")
            return

        if password != confirm:
            messagebox.showerror("Σφάλμα", "Οι κωδικοί δεν ταιριάζουν!")
            return

        if username_exists(username):
            messagebox.showerror("Σφάλμα", "Το username χρησιμοποιείται ήδη!")
            return

        save_user(email, username, password, pronouns)
        messagebox.showinfo("Επιτυχία", "Ο λογαριασμός δημιουργήθηκε επιτυχώς!")
        self.open_login()

    def open_login(self):
        self.destroy()
        subprocess.Popen([sys.executable, "C:\\Users\\evako\\Downloads\\Login.py"])

    def enter_as_guest(self):
        self.destroy()

    def back_to_login(self):
        self.destroy()
        subprocess.Popen([sys.executable, "C:\\Users\\evako\\Downloads\\Login.py"])

if __name__ == "__main__":
    app = SignUpScreen()
    app.mainloop()