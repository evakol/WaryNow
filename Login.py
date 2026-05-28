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

def check_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return "username_not_found"
    cursor.execute("SELECT 1 FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    if result:
        return "success"
    return "wrong_password"

class LoginScreen(ctk.CTk):
    def __init__(self, on_success=None):
        super().__init__()
        self.title("WaryNow - Log In")
        self.geometry("900x600")
        self.resizable(False, False)
        self.on_success = on_success
        init_db()
        self.build_ui()

    def build_ui(self):
        left_frame = ctk.CTkFrame(self, fg_color="black", width=450, height=600, corner_radius=0)
        left_frame.pack(side="left", fill="both")
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="Log In", font=("Arial", 22, "bold"),
                     text_color="black", fg_color="white", width=200,
                     corner_radius=5).pack(pady=30)

        self.username_entry = ctk.CTkEntry(left_frame, placeholder_text="Username", width=300,
                                            fg_color="white", text_color="black")
        self.username_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(left_frame, placeholder_text="Password", show="*",
                                            width=300, fg_color="white", text_color="black")
        self.password_entry.pack(pady=8)

        ctk.CTkButton(left_frame, text="Σύνδεση", command=self.login,
                      width=250, fg_color="white", text_color="black",
                      hover_color="lightgray").pack(pady=15)

        ctk.CTkButton(left_frame, text="Δημιουργία Λογαριασμού", command=self.go_to_signup,
                      width=250, fg_color="white", text_color="black",
                      hover_color="lightgray").pack(pady=5)

        ctk.CTkButton(left_frame, text="Είσοδος σαν Επισκέπτης", command=self.enter_as_guest,
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

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Σφάλμα", "Παρακαλώ συμπληρώστε όλα τα πεδία!")
            return

        result = check_user(username, password)

        if result == "username_not_found":
            messagebox.showerror("Σφάλμα", "Το όνομα χρήστη δε βρέθηκε!")
        elif result == "wrong_password":
            messagebox.showerror("Σφάλμα", "Λάθος κωδικός!")
        elif result == "success":
            messagebox.showinfo("Επιτυχία", f"Καλωσήρθες, {username}!")
            self.destroy()

    def go_to_signup(self):
        self.destroy()
        subprocess.Popen([sys.executable, "C:\\Users\\evako\\Downloads\\SignUp.py"])

    def enter_as_guest(self):
        self.destroy()

if __name__ == "__main__":
    app = LoginScreen()
    app.mainloop()