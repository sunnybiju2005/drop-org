#!/usr/bin/env python3
"""
Login Window for DROP Clothing Shop Billing Application
Handles user authentication and role-based access
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict
from src.database.database_manager import DatabaseManager
from src.config.config import Config

class LoginWindow:
    def __init__(self, root: tk.Tk, db_manager: DatabaseManager, config: Config):
        self.root = root
        self.db_manager = db_manager
        self.config = config
        self.login_success_callback: Optional[Callable] = None
        self.current_user: Optional[Dict] = None
        
        self.setup_window()
        self.create_widgets()
        self.apply_theme()
    
    def setup_window(self):
        """Setup login window properties"""
        self.root.title("DROP - Login")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        self.root.minsize(450, 350)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
    
    def create_widgets(self):
        """Create login form widgets"""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(pady=(0, 30))
        
        self.title_label = ttk.Label(
            header_frame,
            text="DROP",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack()
        
        self.subtitle_label = ttk.Label(
            header_frame,
            text="DRESS FOR LESS",
            font=("Arial", 12, "italic")
        )
        self.subtitle_label.pack()
        
        # Login form
        self.form_frame = ttk.LabelFrame(self.main_frame, text="Login", padding="20")
        self.form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Username
        ttk.Label(self.form_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self.form_frame, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=0, column=1, sticky=tk.EW, pady=(0, 10))
        
        # Password
        ttk.Label(self.form_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=(0, 20))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.form_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=1, column=1, sticky=tk.EW, pady=(0, 20))
        
        # Configure grid weights
        self.form_frame.columnconfigure(1, weight=1)
        
        # Login button
        self.login_button = ttk.Button(
            self.form_frame,
            text="Login",
            command=self.handle_login,
            style="Accent.TButton"
        )
        self.login_button.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.handle_login())
        
        # Default credentials info
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill=tk.X)
        
        self.info_label = ttk.Label(
            info_frame,
            text="Default Admin: admin / admin",
            font=("Arial", 9),
            foreground="gray"
        )
        self.info_label.pack()
    
    def apply_theme(self):
        """Apply current theme to the login window"""
        colors = self.config.get_theme_colors()
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=colors['bg_primary'])
        style.configure('TLabel', background=colors['bg_primary'], foreground=colors['text_primary'])
        style.configure('TLabelFrame', background=colors['bg_primary'], foreground=colors['text_primary'])
        style.configure('TLabelFrame.Label', background=colors['bg_primary'], foreground=colors['text_primary'])
        style.configure('TEntry', fieldbackground=colors['bg_secondary'], foreground=colors['text_primary'])
        style.configure('TButton', background=colors['accent'], foreground='white')
        
        # Accent button style
        style.configure('Accent.TButton', background=colors['accent'], foreground='white')
        style.map('Accent.TButton', 
                  background=[('active', colors['accent_hover']),
                             ('pressed', colors['accent_hover'])])
        
        # Apply background color to root
        self.root.configure(bg=colors['bg_primary'])
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        # Authenticate user
        user = self.db_manager.authenticate_user(username, password)
        
        if user:
            # Store current user info
            self.current_user = user
            
            # Call success callback if set (no welcome message needed)
            if self.login_success_callback:
                self.login_success_callback(user)
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_var.set("")  # Clear password field
    
    def set_login_success_callback(self, callback: Callable):
        """Set callback function to call on successful login"""
        self.login_success_callback = callback
    
    def clear_form(self):
        """Clear login form"""
        self.username_var.set("")
        self.password_var.set("")
        self.username_entry.focus()
