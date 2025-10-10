#!/usr/bin/env python3
"""
Settings Window for DROP Clothing Shop Billing Application
Handles application settings and shop information management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict

from src.database.database_manager import DatabaseManager
from src.config.config import Config

class SettingsWindow(ttk.Frame):
    def __init__(self, parent, db_manager: DatabaseManager, config: Config):
        super().__init__(parent)
        self.db_manager = db_manager
        self.config = config
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Create settings widgets"""
        # Title
        title_label = ttk.Label(self, text="Settings", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Main content frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - General Settings
        left_frame = ttk.LabelFrame(main_frame, text="General Settings", padding="20")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Theme settings
        theme_frame = ttk.LabelFrame(left_frame, text="Theme", padding="10")
        theme_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.theme_var = tk.StringVar()
        
        ttk.Radiobutton(theme_frame, text="Light Theme", variable=self.theme_var, value="light").pack(anchor="w")
        ttk.Radiobutton(theme_frame, text="Dark Theme", variable=self.theme_var, value="dark").pack(anchor="w")
        
        # Auto-save settings
        auto_save_frame = ttk.LabelFrame(left_frame, text="Auto Save", padding="10")
        auto_save_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.auto_save_var = tk.BooleanVar()
        ttk.Checkbutton(auto_save_frame, text="Enable auto-save", variable=self.auto_save_var).pack(anchor="w")
        
        # Carbon Printer settings
        printer_frame = ttk.LabelFrame(left_frame, text="Carbon Printer Settings", padding="10")
        printer_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.carbon_printer_var = tk.BooleanVar()
        ttk.Checkbutton(printer_frame, text="Enable Carbon Printer Mode", variable=self.carbon_printer_var).pack(anchor="w")
        
        # Printer name entry
        printer_name_frame = ttk.Frame(printer_frame)
        printer_name_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(printer_name_frame, text="Printer Name:").pack(side=tk.LEFT, padx=(0, 5))
        self.printer_name_var = tk.StringVar()
        printer_entry = ttk.Entry(printer_name_frame, textvariable=self.printer_name_var, width=20)
        printer_entry.pack(side=tk.LEFT)
        
        # Help text
        help_label = ttk.Label(printer_frame, text="Leave empty for default printer (LPT1)", font=("Arial", 8), foreground="gray")
        help_label.pack(anchor="w", pady=(5, 0))
        
        # Window settings
        window_frame = ttk.LabelFrame(left_frame, text="Window Settings", padding="10")
        window_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Window size
        size_frame = ttk.Frame(window_frame)
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(size_frame, text="Width:").pack(side=tk.LEFT, padx=(0, 5))
        self.width_var = tk.StringVar()
        width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=10)
        width_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(size_frame, text="Height:").pack(side=tk.LEFT, padx=(0, 5))
        self.height_var = tk.StringVar()
        height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=10)
        height_entry.pack(side=tk.LEFT)
        
        # Right side - Shop Information
        right_frame = ttk.LabelFrame(main_frame, text="Shop Information", padding="20", width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)
        
        # Shop name
        ttk.Label(right_frame, text="Shop Name:").pack(anchor="w", pady=(0, 5))
        self.shop_name_var = tk.StringVar()
        shop_name_entry = ttk.Entry(right_frame, textvariable=self.shop_name_var)
        shop_name_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Shop tagline
        ttk.Label(right_frame, text="Tagline:").pack(anchor="w", pady=(0, 5))
        self.tagline_var = tk.StringVar()
        tagline_entry = ttk.Entry(right_frame, textvariable=self.tagline_var)
        tagline_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Shop address
        ttk.Label(right_frame, text="Address:").pack(anchor="w", pady=(0, 5))
        self.address_var = tk.StringVar()
        address_text = tk.Text(right_frame, height=3, wrap=tk.WORD)
        address_text.pack(fill=tk.X, pady=(0, 10))
        self.address_text = address_text
        
        # Phone
        ttk.Label(right_frame, text="Phone:").pack(anchor="w", pady=(0, 5))
        self.phone_var = tk.StringVar()
        phone_entry = ttk.Entry(right_frame, textvariable=self.phone_var)
        phone_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Email
        ttk.Label(right_frame, text="Email:").pack(anchor="w", pady=(0, 5))
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(right_frame, textvariable=self.email_var)
        email_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Save button
        save_button = ttk.Button(
            buttons_frame,
            text="Save Settings",
            command=self.save_settings,
            style="Accent.TButton"
        )
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Reset button
        reset_button = ttk.Button(
            buttons_frame,
            text="Reset to Defaults",
            command=self.reset_to_defaults
        )
        reset_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Apply theme button
        apply_theme_button = ttk.Button(
            buttons_frame,
            text="Apply Theme",
            command=self.apply_theme
        )
        apply_theme_button.pack(side=tk.LEFT)
    
    def load_settings(self):
        """Load current settings"""
        try:
            # Load general settings
            self.theme_var.set(self.config.get("theme", "light"))
            self.auto_save_var.set(self.config.get("auto_save", True))
            self.carbon_printer_var.set(self.config.get("carbon_printer_mode", False))
            self.printer_name_var.set(self.config.get("carbon_printer_name", ""))
            self.width_var.set(str(self.config.get("window_width", 1200)))
            self.height_var.set(str(self.config.get("window_height", 800)))
            
            # Load shop information
            shop_info = self.db_manager.get_shop_info()
            
            self.shop_name_var.set(shop_info.get('shop_name', 'DROP'))
            self.tagline_var.set(shop_info.get('tagline', 'DRESS FOR LESS'))
            self.address_var.set(shop_info.get('address', 'City center, Naikkanal, Thrissur, Kerala 680001'))
            self.phone_var.set(shop_info.get('phone', ''))
            self.email_var.set(shop_info.get('email', ''))
            
            # Set address text
            self.address_text.delete(1.0, tk.END)
            self.address_text.insert(1.0, shop_info.get('address', 'City center, Naikkanal, Thrissur, Kerala 680001'))
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {str(e)}")
    
    def save_settings(self):
        """Save settings to config and database"""
        try:
            # Validate inputs
            try:
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                if width < 800 or height < 600:
                    raise ValueError("Window size too small")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid window dimensions (minimum 800x600)")
                return
            
            # Save general settings to config
            self.config.set("theme", self.theme_var.get())
            self.config.set("auto_save", self.auto_save_var.get())
            self.config.set("carbon_printer_mode", self.carbon_printer_var.get())
            self.config.set("carbon_printer_name", self.printer_name_var.get().strip())
            self.config.set("window_width", width)
            self.config.set("window_height", height)
            
            # Save shop information to database
            shop_name = self.shop_name_var.get().strip()
            tagline = self.tagline_var.get().strip()
            address = self.address_text.get(1.0, tk.END).strip()
            phone = self.phone_var.get().strip()
            email = self.email_var.get().strip()
            
            if not shop_name or not tagline or not address:
                messagebox.showerror("Error", "Please fill in shop name, tagline, and address")
                return
            
            if self.db_manager.update_shop_info(shop_name, tagline, address, phone, email):
                messagebox.showinfo("Success", "Settings saved successfully")
            else:
                messagebox.showerror("Error", "Failed to save shop information")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset settings to default values"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            try:
                # Reset general settings
                self.theme_var.set("light")
                self.auto_save_var.set(True)
                self.carbon_printer_var.set(False)
                self.printer_name_var.set("")
                self.width_var.set("1200")
                self.height_var.set("800")
                
                # Reset shop information
                self.shop_name_var.set("DROP")
                self.tagline_var.set("DRESS FOR LESS")
                self.address_var.set("City center, Naikkanal, Thrissur, Kerala 680001")
                self.phone_var.set("")
                self.email_var.set("")
                
                # Reset address text
                self.address_text.delete(1.0, tk.END)
                self.address_text.insert(1.0, "City center, Naikkanal, Thrissur, Kerala 680001")
                
                messagebox.showinfo("Success", "Settings reset to defaults")
            
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {str(e)}")
    
    def apply_theme(self):
        """Apply selected theme immediately"""
        try:
            new_theme = self.theme_var.get()
            self.config.set("theme", new_theme)
            
            # Apply theme to current window
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
            style.configure('Text', background=colors['bg_secondary'], foreground=colors['text_primary'])
            
            messagebox.showinfo("Theme Applied", f"Switched to {new_theme} theme")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply theme: {str(e)}")
