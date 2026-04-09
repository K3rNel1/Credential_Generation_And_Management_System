# Project: Credential Generation and Management System
# Author: Ali Zubair Shah
# GitHub: https://github.com/K3rNel1 
#GUI version

import tkinter as tk
from tkinter import messagebox
import sqlite3
import random
import os

# ---------------- Database ----------------
conn = sqlite3.connect("passwords.db")
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS passwords (key TEXT PRIMARY KEY, password TEXT)"
)
os.system('attrib +h passwords.db')
conn.commit()

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890@#!$&"

# ---------------- App Window ----------------
root = tk.Tk()
root.title("Password Manager")
root.configure(bg="#121212")

root.geometry("1920x1080")
root.state("zoomed")   # Keeps minimize & close buttons
root.resizable(True, True)

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT = ("Segoe UI", 11)
FONT_BTN = ("Segoe UI", 10, "bold")

# ---------------- Keyboard Control ----------------
current_action = None
previous_screen = None

def set_action(func):
    global current_action
    current_action = func

def handle_enter(event=None):
    if current_action:
        current_action()

def handle_escape(event=None):
    if previous_screen:
        previous_screen()

root.bind("<Return>", handle_enter)
root.bind("<Escape>", handle_escape)

# ---------------- Helpers ----------------
def clear_center():
    for widget in center.winfo_children():
        widget.destroy()

def refresh_saved():
    saved_box.delete(1.0, tk.END)
    cursor.execute("SELECT * FROM passwords")
    rows = cursor.fetchall()
    if not rows:
        saved_box.insert(tk.END, "No passwords saved\n")
    else:
        for k, p in rows:
            saved_box.insert(tk.END, f"{k} → {p}\n")

def back_button():
    tk.Button(
        center, text="← Back",
        command=show_home,
        bg="#2a2a2a", fg="white",
        activebackground="#3a3a3a",
        font=FONT_BTN, bd=0, padx=12, pady=6
    ).pack(anchor="w", pady=5, padx=5)

def entry(label):
    tk.Label(center, text=label, bg="#1e1e1e",
             fg="#bbbbbb", font=FONT).pack(pady=(10, 2))
    e = tk.Entry(center, width=35)
    e.pack(ipady=6)
    return e

def btn(text, command):
    tk.Button(
        center, text=text, command=command,
        bg="#2a2a2a", fg="white",
        activebackground="#3a3a3a",
        font=FONT_BTN, width=28, bd=0, pady=8
    ).pack(pady=6)

# ---------------- Screens ----------------
def show_home():
    global previous_screen
    clear_center()
    previous_screen = None
    set_action(None)

    tk.Label(center, text="Welcome to Password Manager",
             bg="#1e1e1e", fg="white",
             font=FONT_TITLE).pack(pady=30)

    btn("Generate Password", show_generate)
    btn("Save Your Own Password", show_save)
    btn("Update Saved Password", show_update)
    btn("Delete Saved Password", show_delete)

def show_generate():
    global previous_screen
    clear_center()
    previous_screen = show_home

    back_button()
    tk.Label(center, text="Generate Password",
             bg="#1e1e1e", fg="white",
             font=FONT_TITLE).pack(pady=15)

    length_entry = entry("Password Length")
    key_entry = entry("Key")
    pwd_entry = entry("Generated Password")

    def generate():
        try:
            length = int(length_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number")
            return
        pwd = "".join(random.choice(chars) for _ in range(length))
        pwd_entry.delete(0, tk.END)
        pwd_entry.insert(0, pwd)

    btn("Generate Password", generate)
    set_action(generate)

    def save():
        if not key_entry.get() or not pwd_entry.get():
            messagebox.showerror("Error", "Key or password missing")
            return
        cursor.execute(
            "INSERT OR REPLACE INTO passwords VALUES (?, ?)",
            (key_entry.get(), pwd_entry.get())
        )#Author : Github.com/K3rnel1
        conn.commit()
        refresh_saved()
        messagebox.showinfo("Saved", "Password saved successfully")

    btn("Save Password", save)

def show_save():
    global previous_screen
    clear_center()
    previous_screen = show_home

    back_button()
    tk.Label(center, text="Save Your Own Password",
             bg="#1e1e1e", fg="white",
             font=FONT_TITLE).pack(pady=15)

    key_entry = entry("Key")
    pwd_entry = entry("Password")

    def save():
        cursor.execute(
            "INSERT OR REPLACE INTO passwords VALUES (?, ?)",
            (key_entry.get(), pwd_entry.get())
        )
        conn.commit()
        refresh_saved()
        messagebox.showinfo("Saved", "Password saved")

    btn("Save Password", save)
    set_action(save)

def show_update():
    global previous_screen
    clear_center()
    previous_screen = show_home

    back_button()
    tk.Label(center, text="Update Password",
             bg="#1e1e1e", fg="white",
             font=FONT_TITLE).pack(pady=15)

    key_entry = entry("Key")
    pwd_entry = entry("New Password")

    def update():
        cursor.execute(
            "REPLACE INTO passwords VALUES (?, ?)",
            (key_entry.get(), pwd_entry.get())
        )
        conn.commit()
        refresh_saved()
        messagebox.showinfo("Updated", "Password updated")

    btn("Update Password", update)
    set_action(update)

def show_delete():
    global previous_screen
    clear_center()
    previous_screen = show_home

    back_button()
    tk.Label(center, text="Delete Saved Password",
             bg="#1e1e1e", fg="white",
             font=FONT_TITLE).pack(pady=15)

    key_entry = entry("Key to Delete")

    def delete():
        cursor.execute(
            "DELETE FROM passwords WHERE key = ?",
            (key_entry.get(),)
        )
        conn.commit()
        refresh_saved()
        messagebox.showinfo("Deleted", "Password deleted")

    btn("Delete Password", delete)
    set_action(delete)

# ---------------- Layout ----------------
left = tk.Frame(root, bg="#1e1e1e")
left.pack(side="left", fill="both", expand=True)

right = tk.Frame(root, bg="#181818", width=320)
right.pack(side="right", fill="y")

center = tk.Frame(left, bg="#1e1e1e")
center.pack(expand=True)

# ---------------- Saved Panel ----------------
tk.Label(right, text="Saved Passwords",
         bg="#181818", fg="white",
         font=("Segoe UI", 14, "bold")).pack(pady=10)

saved_box = tk.Text(
    right, bg="#101010", fg="#00ffcc",
    font=("Consolas", 10),
    width=36, height=30, bd=0
)
saved_box.pack(padx=10, pady=5)

refresh_saved()
show_home()

root.mainloop()
