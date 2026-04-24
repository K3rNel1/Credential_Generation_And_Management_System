import sys
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox
import os

from Backend import (
    _get_conn, _CHARS,
    encrypt_password, decrypt_password,
    generate_password,
    add_entry, get_entries, update_entry, delete_entry,
    setup_security_question, get_security_question,
    verify_security_answer, auth_configured,
)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def set_dark_title_bar(window):
    try:
        window.update()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)),
            ctypes.sizeof(ctypes.c_int(1))
        )
    except Exception:
        pass


BG_COLOR     = "#0f172a"
PANEL_COLOR  = "#1e293b"
ACCENT_COLOR = "#3b82f6"
ACCENT_HOVER = "#2563eb"
TEXT_COLOR   = "#f8fafc"
TEXT_MUTED   = "#94a3b8"
DANGER_COLOR = "#ef4444"
DANGER_HOVER = "#dc2626"
SUCCESS_COLOR = "#10b981"
WARNING_COLOR = "#f59e0b"

FONT_MAIN  = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_LARGE = ("Segoe UI", 14)


class ModernButton(tk.Frame):
    def __init__(self, parent, text, command, bg=ACCENT_COLOR, hover_bg=ACCENT_HOVER, fg=TEXT_COLOR, font=FONT_BOLD, pady=8, padx=16):
        super().__init__(parent, bg=bg, cursor="hand2")
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg

        self.lbl = tk.Label(self, text=text, bg=bg, fg=fg, font=font)
        self.lbl.pack(expand=True, fill="both", pady=pady, padx=padx)

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.lbl.bind("<Enter>", self.on_enter)
        self.lbl.bind("<Leave>", self.on_leave)

        self.bind("<Button-1>", self.on_click)
        self.lbl.bind("<Button-1>", self.on_click)

    def on_enter(self, e):
        self.config(bg=self.hover_bg)
        self.lbl.config(bg=self.hover_bg)

    def on_leave(self, e):
        self.config(bg=self.bg)
        self.lbl.config(bg=self.bg)

    def on_click(self, e):
        self.command()


class IconButton(tk.Frame):
    def __init__(self, parent, text, command, bg=PANEL_COLOR, hover_bg="#334155", fg=TEXT_COLOR):
        super().__init__(parent, bg=bg, cursor="hand2")
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg

        self.lbl = tk.Label(self, text=text, bg=bg, fg=fg, font=("Segoe UI", 12))
        self.lbl.pack(expand=True, fill="both", pady=4, padx=8)

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.lbl.bind("<Enter>", self.on_enter)
        self.lbl.bind("<Leave>", self.on_leave)

        self.bind("<Button-1>", self.on_click)
        self.lbl.bind("<Button-1>", self.on_click)

    def on_enter(self, e):
        self.config(bg=self.hover_bg)
        self.lbl.config(bg=self.hover_bg)

    def on_leave(self, e):
        self.config(bg=self.bg)
        self.lbl.config(bg=self.bg)

    def on_click(self, e):
        self.command()


class ScrollableFrame(tk.Frame):
    def __init__(self, container, bg_color, *args, **kwargs):
        super().__init__(container, bg=bg_color, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Vertical.TScrollbar", gripcount=0,
                        background=PANEL_COLOR, darkcolor=BG_COLOR, lightcolor=BG_COLOR,
                        troughcolor=BG_COLOR, bordercolor=BG_COLOR, arrowcolor=TEXT_COLOR)
        style.configure("Horizontal.TScale", background=PANEL_COLOR, darkcolor=PANEL_COLOR, lightcolor=PANEL_COLOR,
                        troughcolor=BG_COLOR, bordercolor=PANEL_COLOR)

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview, style="Vertical.TScrollbar")
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if self.scrollable_frame.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Manager")
        self.geometry("900x600")
        self.configure(bg=BG_COLOR)

        try:
            self.iconbitmap(resource_path("a.ico"))
        except Exception:
            pass

        set_dark_title_bar(self)

        _get_conn().close()

        self.sidebar = tk.Frame(self, bg=PANEL_COLOR, width=320)
        self.sidebar.pack_propagate(False)

        self.main_content = tk.Frame(self, bg=BG_COLOR)
        self.main_content.pack(side="right", fill="both", expand=True)

        self.build_sidebar()

        self.views = {}
        self.edit_key = None

        self.build_dashboard()
        self.build_save_page()
        self.build_generate_page()
        self.build_auth_setup_page()
        self.build_login_page()

        if auth_configured():
            self.show_view("login")
        else:
            self.show_view("auth_setup")

    def build_sidebar(self):
        tk.Label(self.sidebar, text="🔐 Password Manager", bg=PANEL_COLOR, fg=TEXT_COLOR, font=FONT_TITLE, pady=25).pack(fill="x")

        self.btn_dash = self.add_sidebar_btn("📋 Dashboard", lambda: self.show_view("dashboard"))
        self.btn_save = self.add_sidebar_btn("➕ Add Password", lambda: self.show_save_page())
        self.btn_gen  = self.add_sidebar_btn("🎲 Generate", lambda: self.show_view("generate"))

        tk.Label(self.sidebar, text="© Ali Zubair Shah - K3rNel", bg=PANEL_COLOR, fg=TEXT_MUTED, font=("Segoe UI", 8)).pack(side="bottom", pady=15)

    def add_sidebar_btn(self, text, command):
        btn = ModernButton(self.sidebar, text, command, bg=PANEL_COLOR, hover_bg="#334155", font=FONT_LARGE)
        btn.lbl.config(anchor="w", padx=20)
        btn.pack(fill="x", pady=5, padx=10)
        return btn

    def show_view(self, name):
        for view in self.views.values():
            view.pack_forget()
        self.views[name].pack(fill="both", expand=True)

        if name == "dashboard":
            self.refresh_dashboard()
        elif name == "login":
            q = get_security_question()
            if q:
                self.login_q_lbl.config(text=f"Q: {q}")
            self.login_a_entry.focus()

    def show_save_page(self, key=None, prefill_pwd=None):
        self.edit_key = key
        self.save_title.config(text="Edit Password" if key else "Add New Password")
        self.save_key_entry.config(state="normal")
        self.save_key_entry.delete(0, tk.END)

        if key:
            self.save_key_entry.insert(0, key)
            self.save_key_entry.config(state="disabled")

        self.save_pwd_entry.delete(0, tk.END)
        if prefill_pwd:
            self.save_pwd_entry.insert(0, prefill_pwd)

        self.update_strength_indicator()
        self.show_view("save")

    def build_dashboard(self):
        view = tk.Frame(self.main_content, bg=BG_COLOR)
        self.views["dashboard"] = view

        header = tk.Frame(view, bg=BG_COLOR)
        header.pack(fill="x", padx=40, pady=(40, 10))

        tk.Label(header, text="Dashboard", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT_TITLE).pack(side="left")

        self.cards_container = ScrollableFrame(view, BG_COLOR)
        self.cards_container.pack(fill="both", expand=True, padx=40, pady=10)

    def refresh_dashboard(self):
        for widget in self.cards_container.scrollable_frame.winfo_children():
            widget.destroy()

        entries = get_entries()
        if not entries:
            tk.Label(self.cards_container.scrollable_frame, text="No passwords saved yet.", bg=BG_COLOR, fg=TEXT_MUTED, font=FONT_MAIN).pack(pady=40)
            return

        for key, encrypted_pwd in entries:
            self.create_password_card(key, encrypted_pwd)

    def create_password_card(self, key, encrypted_pwd):
        card = tk.Frame(self.cards_container.scrollable_frame, bg=PANEL_COLOR, pady=15, padx=25)
        card.pack(fill="x", pady=8, padx=5)

        info_frame = tk.Frame(card, bg=PANEL_COLOR)
        info_frame.pack(side="left", fill="x", expand=True)

        tk.Label(info_frame, text=key, bg=PANEL_COLOR, fg=TEXT_COLOR, font=FONT_BOLD, anchor="w").pack(fill="x")

        lbl_pwd = tk.Label(info_frame, text="••••••••••••", bg=PANEL_COLOR, fg=TEXT_MUTED, font=FONT_MAIN, anchor="w")
        lbl_pwd.pack(fill="x", pady=(2, 0))

        actions_frame = tk.Frame(card, bg=PANEL_COLOR)
        actions_frame.pack(side="right")

        is_visible = [False]

        def toggle_visibility():
            if is_visible[0]:
                lbl_pwd.config(text="••••••••••••", fg=TEXT_MUTED)
                btn_view.lbl.config(text="👁")
            else:
                lbl_pwd.config(text=decrypt_password(encrypted_pwd), fg=TEXT_COLOR)
                btn_view.lbl.config(text="🙈")
            is_visible[0] = not is_visible[0]

        def copy_pwd():
            self.clipboard_clear()
            self.clipboard_append(decrypt_password(encrypted_pwd))
            self.show_toast("Copied to clipboard!", SUCCESS_COLOR)

        def edit_entry():
            self.show_save_page(key=key, prefill_pwd=decrypt_password(encrypted_pwd))

        def del_entry():
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the password for '{key}'?", parent=self):
                if delete_entry(key):
                    self.show_toast("Deleted successfully.", SUCCESS_COLOR)
                    self.refresh_dashboard()
                else:
                    self.show_toast("Failed to delete.", DANGER_COLOR)

        btn_view = IconButton(actions_frame, "👁", toggle_visibility)
        btn_view.pack(side="left", padx=3)

        IconButton(actions_frame, "📋", copy_pwd).pack(side="left", padx=3)
        IconButton(actions_frame, "✏️", edit_entry).pack(side="left", padx=3)
        IconButton(actions_frame, "🗑", del_entry, hover_bg=DANGER_HOVER).pack(side="left", padx=3)

    def build_save_page(self):
        view = tk.Frame(self.main_content, bg=BG_COLOR)
        self.views["save"] = view

        container = tk.Frame(view, bg=PANEL_COLOR, padx=50, pady=50)
        container.place(relx=0.5, rely=0.5, anchor="center")

        self.save_title = tk.Label(container, text="Add New Password", bg=PANEL_COLOR, fg=TEXT_COLOR, font=FONT_TITLE)
        self.save_title.pack(pady=(0, 25), anchor="w")

        tk.Label(container, text="Account / Service Name", bg=PANEL_COLOR, fg=TEXT_MUTED, font=FONT_MAIN).pack(anchor="w")
        self.save_key_entry = tk.Entry(container, bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, font=FONT_LARGE, relief="flat")
        self.save_key_entry.pack(fill="x", pady=(5, 20), ipady=8)

        tk.Label(container, text="Password", bg=PANEL_COLOR, fg=TEXT_MUTED, font=FONT_MAIN).pack(anchor="w")
        pwd_frame = tk.Frame(container, bg=BG_COLOR)
        pwd_frame.pack(fill="x", pady=(5, 8))

        self.save_pwd_entry = tk.Entry(pwd_frame, bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, font=FONT_LARGE, relief="flat", show="•")
        self.save_pwd_entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.save_pwd_entry.bind("<KeyRelease>", lambda e: self.update_strength_indicator())

        self.show_pwd_var = tk.BooleanVar(value=False)
        def toggle_save_pwd():
            if self.show_pwd_var.get():
                self.save_pwd_entry.config(show="")
            else:
                self.save_pwd_entry.config(show="•")

        tk.Checkbutton(pwd_frame, text="Show", variable=self.show_pwd_var, command=toggle_save_pwd, bg=BG_COLOR, fg=TEXT_MUTED, selectcolor=BG_COLOR, activebackground=BG_COLOR, activeforeground=TEXT_COLOR, font=FONT_MAIN).pack(side="right", padx=10)

        strength_frame = tk.Frame(container, bg=PANEL_COLOR)
        strength_frame.pack(fill="x", pady=(0, 25))

        self.strength_lbl = tk.Label(strength_frame, text="Strength: None", bg=PANEL_COLOR, fg=TEXT_MUTED, font=FONT_MAIN)
        self.strength_lbl.pack(side="left")

        self.strength_bar = tk.Canvas(strength_frame, height=4, bg=BG_COLOR, highlightthickness=0)
        self.strength_bar.pack(side="right", fill="x", expand=True, padx=(15, 0))
        self.strength_rect = self.strength_bar.create_rectangle(0, 0, 0, 4, fill=BG_COLOR, outline="")

        ModernButton(container, "Save Password", self.save_password).pack(fill="x", pady=(10, 0))

    def update_strength_indicator(self):
        pwd = self.save_pwd_entry.get()
        if not pwd:
            self.strength_lbl.config(text="Strength: None", fg=TEXT_MUTED)
            self.strength_bar.itemconfig(self.strength_rect, fill=BG_COLOR)
            self.strength_bar.coords(self.strength_rect, 0, 0, 0, 4)
            return

        score = 0
        if len(pwd) >= 8: score += 1
        if len(pwd) >= 12: score += 1
        if any(c.isupper() for c in pwd): score += 1
        if any(c.islower() for c in pwd): score += 1
        if any(c.isdigit() for c in pwd): score += 1
        if any(c in _CHARS[-7:] for c in pwd): score += 1

        width = self.strength_bar.winfo_width()
        if width <= 1: width = 250

        if score < 3:
            text, color, w_ratio = "Weak", DANGER_COLOR, 0.33
        elif score < 5:
            text, color, w_ratio = "Medium", WARNING_COLOR, 0.66
        else:
            text, color, w_ratio = "Strong", SUCCESS_COLOR, 1.0

        self.strength_lbl.config(text=f"Strength: {text}", fg=color)
        self.strength_bar.itemconfig(self.strength_rect, fill=color)
        self.strength_bar.coords(self.strength_rect, 0, 0, width * w_ratio, 4)

    def save_password(self):
        key = self.save_key_entry.get().strip()
        pwd = self.save_pwd_entry.get()

        if not key or not pwd:
            self.show_toast("Please fill all fields.", DANGER_COLOR)
            return

        if self.edit_key:
            if update_entry(self.edit_key, pwd):
                self.show_toast("Password updated!", SUCCESS_COLOR)
                self.show_view("dashboard")
            else:
                self.show_toast("Failed to update.", DANGER_COLOR)
        else:
            existing = [k[0] for k in get_entries()]
            if key in existing:
                if not messagebox.askyesno("Overwrite", "This account name already exists. Overwrite?", parent=self):
                    return

            if add_entry(key, pwd):
                self.show_toast("Password saved!", SUCCESS_COLOR)
                self.show_view("dashboard")
            else:
                self.show_toast("Failed to save.", DANGER_COLOR)

    def build_auth_setup_page(self):
        view = tk.Frame(self.main_content, bg=BG_COLOR)
        self.views["auth_setup"] = view

        container = tk.Frame(view, bg=PANEL_COLOR, padx=50, pady=50)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="Create Account", bg=PANEL_COLOR, fg=TEXT_COLOR, font=FONT_TITLE).pack(pady=(0, 25), anchor="w")
        tk.Label(container, text="Security Question", bg=PANEL_COLOR, fg=TEXT_MUTED, font=FONT_MAIN).pack(anchor="w")

        self.setup_q_entry = tk.Entry(container, bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, font=FONT_LARGE, relief="flat")
        self.setup_q_entry.pack(fill="x", pady=(5, 20), ipady=8)

        tk.Label(container, text="Answer", bg=PANEL_COLOR, fg=TEXT_MUTED, font=FONT_MAIN).pack(anchor="w")
        self.setup_a_entry = tk.Entry(container, bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, font=FONT_LARGE, relief="flat", show="•")
        self.setup_a_entry.pack(fill="x", pady=(5, 25), ipady=8)

        ModernButton(container, "Save & Continue", self.save_auth_setup).pack(fill="x")

    def save_auth_setup(self):
        q = self.setup_q_entry.get().strip()
        a = self.setup_a_entry.get().strip()
        if not q or not a:
            self.show_toast("Please fill both fields.", DANGER_COLOR)
            return
        if setup_security_question(q, a):
            self.show_toast("Account created successfully!", SUCCESS_COLOR)
            self.sidebar.pack(side="left", fill="y", before=self.main_content)
            self.show_view("dashboard")
        else:
            self.show_toast("Failed to create account.", DANGER_COLOR)

    def build_login_page(self):
        view = tk.Frame(self.main_content, bg=BG_COLOR)
        self.views["login"] = view

        container = tk.Frame(view, bg=PANEL_COLOR, padx=50, pady=50)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="Login", bg=PANEL_COLOR, fg=TEXT_COLOR, font=FONT_TITLE).pack(pady=(0, 25), anchor="w")

        self.login_q_lbl = tk.Label(container, text="", bg=PANEL_COLOR, fg=TEXT_MUTED, font=FONT_MAIN, wraplength=300, justify="left")
        self.login_q_lbl.pack(anchor="w", pady=(0, 5))

        self.login_a_entry = tk.Entry(container, bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, font=FONT_LARGE, relief="flat", show="•")
        self.login_a_entry.pack(fill="x", pady=(5, 25), ipady=8)
        self.login_a_entry.bind("<Return>", lambda e: self.do_login())

        ModernButton(container, "Login", self.do_login).pack(fill="x")

    def do_login(self):
        a = self.login_a_entry.get().strip()
        if verify_security_answer(a):
            self.show_toast("Login successful!", SUCCESS_COLOR)
            self.login_a_entry.delete(0, tk.END)
            self.sidebar.pack(side="left", fill="y", before=self.main_content)
            self.show_view("dashboard")
        else:
            self.show_toast("Incorrect answer.", DANGER_COLOR)
            self.login_a_entry.delete(0, tk.END)

    def build_generate_page(self):
        view = tk.Frame(self.main_content, bg=BG_COLOR)
        self.views["generate"] = view

        container = tk.Frame(view, bg=PANEL_COLOR, padx=50, pady=50)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="Generate Password", bg=PANEL_COLOR, fg=TEXT_COLOR, font=FONT_TITLE).pack(pady=(0, 25), anchor="w")

        tk.Label(container, text="Password Length", bg=PANEL_COLOR, fg=TEXT_MUTED, font=FONT_MAIN).pack(anchor="w")
        self.len_var = tk.StringVar(value="8")

        tk.Entry(container, textvariable=self.len_var, bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, font=FONT_LARGE, relief="flat").pack(fill="x", pady=(5, 25), ipady=8)

        self.gen_pwd_lbl = tk.Entry(container, bg=BG_COLOR, fg=SUCCESS_COLOR, font=("Courier", 18, "bold"), justify="center", relief="flat", state="readonly", readonlybackground=BG_COLOR)
        self.gen_pwd_lbl.pack(fill="x", pady=25, ipady=20)

        actions_frame = tk.Frame(container, bg=PANEL_COLOR)
        actions_frame.pack(fill="x")

        ModernButton(actions_frame, "Generate", self.do_generate).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ModernButton(actions_frame, "Copy", self.copy_generated, bg=PANEL_COLOR, hover_bg="#334155").pack(side="left", expand=True, fill="x", padx=5)
        ModernButton(actions_frame, "Use Password", self.use_generated, bg=PANEL_COLOR, hover_bg="#334155").pack(side="left", expand=True, fill="x", padx=(5, 0))

    def do_generate(self):
        try:
            length = int(self.len_var.get())
            if length <= 0:
                raise ValueError
        except ValueError:
            self.show_toast("Invalid length. Defaulting to 8.", DANGER_COLOR)
            length = 8
            self.len_var.set("8")

        pwd = generate_password(length)
        self.gen_pwd_lbl.config(state="normal")
        self.gen_pwd_lbl.delete(0, tk.END)
        self.gen_pwd_lbl.insert(0, pwd)
        self.gen_pwd_lbl.config(state="readonly")

    def copy_generated(self):
        pwd = self.gen_pwd_lbl.get()
        if pwd:
            self.clipboard_clear()
            self.clipboard_append(pwd)
            self.show_toast("Password copied!", SUCCESS_COLOR)

    def use_generated(self):
        pwd = self.gen_pwd_lbl.get()
        if pwd:
            self.show_save_page(prefill_pwd=pwd)

    def show_toast(self, message, color):
        toast = tk.Label(self, text=message, bg=color, fg=TEXT_COLOR, font=FONT_BOLD, padx=25, pady=12)
        toast.place(relx=0.5, rely=0.9, anchor="center")
        self.after(2500, toast.destroy)


if __name__ == "__main__":
    app = App()
    app.mainloop()
