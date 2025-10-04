#!/usr/bin/env python3
"""
Admin Dashboard for DROP Clothing Shop Billing Application
Provides admin functionality including settings, item management, and billing history
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict
from datetime import datetime, timedelta

from src.database.database_manager import DatabaseManager
from src.config.config import Config
from src.ui.item_management import ItemManagementWindow
from src.ui.billing_history import BillingHistoryWindow
from src.ui.settings_window import SettingsWindow
from src.ui.staff_dashboard import StaffDashboard

class AdminDashboard(ttk.Frame):
    def __init__(self, root: tk.Tk, db_manager: DatabaseManager, config: Config, current_user: Dict):
        super().__init__(root)
        self.root = root
        self.db_manager = db_manager
        self.config = config
        self.current_user = current_user
        
        self.setup_window()
        self.create_widgets()
        self.apply_theme()
        self.load_dashboard_data()
    
    def setup_window(self):
        """Setup admin dashboard window"""
        # Configure the frame
        self.configure(relief="flat", borderwidth=0)
        
        # Update root window properties - make it responsive
        self.root.title("DROP - Admin Dashboard")
        self.root.geometry("1300x850")
        self.root.resizable(True, True)
        self.root.minsize(1000, 700)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (650)
        y = (self.root.winfo_screenheight() // 2) - (425)
        self.root.geometry(f"1300x850+{x}+{y}")
    
    def create_widgets(self):
        """Create admin dashboard widgets"""
        # Main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header()
        
        # Content area
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left sidebar
        self.create_sidebar()
        
        # Main content area
        self.main_content = ttk.Frame(self.content_frame)
        self.main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Default content
        self.show_dashboard_overview()
    
    def create_header(self):
        """Create dashboard header"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Left side - Back button and Title
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side=tk.LEFT)
        
        # Back to main button
        back_button = ttk.Button(
            left_frame,
            text="← Back to Main",
            command=self.go_back_to_main,
            width=15
        )
        back_button.pack(side=tk.LEFT, padx=(0, 20))
        
        self.title_label = ttk.Label(
            left_frame,
            text="DROP - Admin Dashboard",
            font=("Arial", 18, "bold")
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Right side - User info and theme toggle
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # Theme toggle button
        self.theme_button = ttk.Button(
            right_frame,
            text="🌙 Dark" if self.config.get("theme") == "light" else "☀️ Light",
            command=self.toggle_theme,
            width=10
        )
        self.theme_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # User info
        user_label = ttk.Label(
            right_frame,
            text=f"Welcome, {self.current_user['username']}",
            font=("Arial", 10)
        )
        user_label.pack(side=tk.RIGHT)
        
        # Logout button
        logout_button = ttk.Button(
            right_frame,
            text="Logout",
            command=self.logout,
            width=8
        )
        logout_button.pack(side=tk.RIGHT, padx=(10, 0))
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        sidebar_frame = ttk.LabelFrame(self.content_frame, text="Navigation", width=200)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar_frame.pack_propagate(False)
        
        # Navigation buttons
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard_overview),
            ("📦 Manage Items", self.open_item_management),
            ("📋 Billing History", self.open_billing_history),
            ("⚙️ Settings", self.open_settings),
            ("👥 Staff Billing", self.open_staff_login),
        ]
        
        for text, command in nav_buttons:
            btn = ttk.Button(
                sidebar_frame,
                text=text,
                command=command,
                width=20
            )
            btn.pack(fill=tk.X, padx=5, pady=2)
        
        # Separator
        ttk.Separator(sidebar_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=10)
        
        # Database Management Section
        db_mgmt_frame = ttk.LabelFrame(sidebar_frame, text="Database Management")
        db_mgmt_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Delete selected data button
        delete_selected_btn = ttk.Button(
            db_mgmt_frame,
            text="🗑️ Delete Selected Data",
            command=self.delete_selected_data,
            width=18
        )
        delete_selected_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # Delete all data button
        delete_all_btn = ttk.Button(
            db_mgmt_frame,
            text="⚠️ Delete All Data",
            command=self.delete_all_data,
            width=18
        )
        delete_all_btn.pack(fill=tk.X, padx=5, pady=2)
        
        # Separator
        ttk.Separator(sidebar_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=10)
        
        # Quick stats
        self.stats_frame = ttk.LabelFrame(sidebar_frame, text="Quick Stats")
        self.stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.total_items_label = ttk.Label(self.stats_frame, text="Total Items: 0")
        self.total_items_label.pack(anchor="w", padx=5, pady=2)
        
        self.today_sales_label = ttk.Label(self.stats_frame, text="Today's Sales: ₹0")
        self.today_sales_label.pack(anchor="w", padx=5, pady=2)
        
        self.month_sales_label = ttk.Label(self.stats_frame, text="Month's Sales: ₹0")
        self.month_sales_label.pack(anchor="w", padx=5, pady=2)
    
    def show_dashboard_overview(self):
        """Show dashboard overview content"""
        # Clear main content
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Overview title
        title_label = ttk.Label(
            self.main_content,
            text="Dashboard Overview",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Stats cards
        stats_frame = ttk.Frame(self.main_content)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Today's sales card
        today_card = ttk.LabelFrame(stats_frame, text="Today's Sales", padding="10")
        today_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.today_sales_value = ttk.Label(today_card, text="₹0", font=("Arial", 20, "bold"))
        self.today_sales_value.pack()
        
        # This month's sales card
        month_card = ttk.LabelFrame(stats_frame, text="This Month's Sales", padding="10")
        month_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.month_sales_value = ttk.Label(month_card, text="₹0", font=("Arial", 20, "bold"))
        self.month_sales_value.pack()
        
        # Total items card
        items_card = ttk.LabelFrame(stats_frame, text="Total Items", padding="10")
        items_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.total_items_value = ttk.Label(items_card, text="0", font=("Arial", 20, "bold"))
        self.total_items_value.pack()
        
        # Recent bills table
        recent_frame = ttk.LabelFrame(self.main_content, text="Recent Bills", padding="10")
        recent_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for recent bills
        columns = ("Bill No", "Date", "Amount", "Payment", "Staff")
        self.recent_bills_tree = ttk.Treeview(recent_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        for col in columns:
            self.recent_bills_tree.heading(col, text=col)
            self.recent_bills_tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=self.recent_bills_tree.yview)
        self.recent_bills_tree.configure(yscrollcommand=scrollbar.set)
        
        self.recent_bills_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load data
        self.load_dashboard_data()
    
    def load_dashboard_data(self):
        """Load dashboard data and statistics"""
        try:
            # Get total items count
            items = self.db_manager.get_all_items()
            total_items = len(items)
            
            # Get today's date
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Get this month's date range
            first_day = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            last_day = datetime.now().strftime('%Y-%m-%d')
            
            # Get today's sales
            today_bills = self.db_manager.get_bills_by_date_range(today, today)
            today_sales = sum(bill['total_amount'] for bill in today_bills)
            
            # Get month's sales
            month_bills = self.db_manager.get_bills_by_date_range(first_day, last_day)
            month_sales = sum(bill['total_amount'] for bill in month_bills)
            
            # Update labels
            if hasattr(self, 'total_items_value'):
                self.total_items_value.config(text=str(total_items))
            if hasattr(self, 'today_sales_value'):
                self.today_sales_value.config(text=f"₹{today_sales:.2f}")
            if hasattr(self, 'month_sales_value'):
                self.month_sales_value.config(text=f"₹{month_sales:.2f}")
            
            # Update sidebar stats
            if hasattr(self, 'total_items_label'):
                self.total_items_label.config(text=f"Total Items: {total_items}")
            if hasattr(self, 'today_sales_label'):
                self.today_sales_label.config(text=f"Today's Sales: ₹{today_sales:.2f}")
            if hasattr(self, 'month_sales_label'):
                self.month_sales_label.config(text=f"Month's Sales: ₹{month_sales:.2f}")
            
            # Load recent bills
            if hasattr(self, 'recent_bills_tree'):
                # Clear existing items
                for item in self.recent_bills_tree.get_children():
                    self.recent_bills_tree.delete(item)
                
                # Add recent bills (last 10)
                recent_bills = self.db_manager.get_bills_by_date_range(
                    (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                    datetime.now().strftime('%Y-%m-%d')
                )
                
                for bill in recent_bills[:10]:  # Show only last 10
                    self.recent_bills_tree.insert("", "end", values=(
                        bill['bill_number'],
                        bill['created_at'][:10],
                        f"₹{bill['total_amount']:.2f}",
                        bill['payment_method'].upper(),
                        bill['staff_username']
                    ))
        
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    def open_item_management(self):
        """Open item management window"""
        try:
            # Clear main content
            for widget in self.main_content.winfo_children():
                widget.destroy()
            
            # Create item management widget
            item_management = ItemManagementWindow(
                self.main_content,
                self.db_manager,
                self.config
            )
            item_management.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open item management: {str(e)}")
    
    def open_billing_history(self):
        """Open billing history window"""
        try:
            # Clear main content
            for widget in self.main_content.winfo_children():
                widget.destroy()
            
            # Create billing history widget
            billing_history = BillingHistoryWindow(
                self.main_content,
                self.db_manager,
                self.config
            )
            billing_history.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open billing history: {str(e)}")
    
    def open_settings(self):
        """Open settings window"""
        try:
            # Clear main content
            for widget in self.main_content.winfo_children():
                widget.destroy()
            
            # Create settings widget
            settings = SettingsWindow(
                self.main_content,
                self.db_manager,
                self.config
            )
            settings.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open settings: {str(e)}")
    
    def open_staff_login(self):
        """Open staff billing interface directly"""
        try:
            # Create a default staff user object
            staff_user = {
                'id': 1,
                'username': 'staff',
                'user_type': 'staff',
                'last_login': None
            }
            
            # Create new window for staff billing
            staff_window = tk.Toplevel(self.root)
            staff_window.title("DROP - Staff Billing")
            staff_window.geometry("1600x1000")
            staff_window.resizable(True, True)
            staff_window.minsize(1200, 800)
            
            # Center staff window
            staff_window.update_idletasks()
            x = (staff_window.winfo_screenwidth() // 2) - (800)
            y = (staff_window.winfo_screenheight() // 2) - (500)
            staff_window.geometry(f"1600x1000+{x}+{y}")
            
            # Create staff dashboard
            staff_dashboard = StaffDashboard(
                staff_window,
                self.db_manager,
                self.config,
                staff_user
            )
            staff_dashboard.pack(fill=tk.BOTH, expand=True)
            
            # Store reference for cleanup
            staff_window.staff_dashboard = staff_dashboard
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open staff billing: {str(e)}")
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        new_theme = self.config.toggle_theme()
        self.theme_button.config(
            text="🌙 Dark" if new_theme == "light" else "☀️ Light"
        )
        self.apply_theme()
        messagebox.showinfo("Theme Changed", f"Switched to {new_theme} theme")
    
    def apply_theme(self):
        """Apply current theme to the dashboard"""
        colors = self.config.get_theme_colors()
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=colors['bg_primary'])
        style.configure('TLabel', background=colors['bg_primary'], foreground=colors['text_primary'])
        style.configure('TLabelFrame', background=colors['bg_primary'], foreground=colors['text_primary'])
        style.configure('TLabelFrame.Label', background=colors['bg_primary'], foreground=colors['text_primary'])
        style.configure('TButton', background=colors['accent'], foreground='white')
        style.configure('Treeview', background=colors['bg_secondary'], foreground=colors['text_primary'])
        style.configure('Treeview.Heading', background=colors['bg_tertiary'], foreground=colors['text_primary'])
        
        # Apply background color to root
        self.root.configure(bg=colors['bg_primary'])
    
    def go_back_to_main(self):
        """Go back to main selection window"""
        try:
            # Use the main app reference if available
            if hasattr(self, 'main_app'):
                self.main_app.show_main_selection()
            else:
                # Fallback: clear current content
                for widget in self.root.winfo_children():
                    widget.destroy()
                
                # Import and show main selection
                from main import DropBillingApp
                app = DropBillingApp()
                app.show_main_selection()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to go back to main: {str(e)}")
    
    def logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.go_back_to_main()
    
    def delete_selected_data(self):
        """Delete selected data from database"""
        try:
            # Show options for what to delete
            delete_options = [
                "Selected Items",
                "Selected Bills", 
                "Selected Users",
                "All Items",
                "All Bills",
                "All Users"
            ]
            
            # Create a simple dialog to select what to delete
            dialog = tk.Toplevel(self.root)
            dialog.title("Delete Selected Data")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (200)
            y = (dialog.winfo_screenheight() // 2) - (150)
            dialog.geometry(f"400x300+{x}+{y}")
            
            ttk.Label(dialog, text="Select data to delete:", font=("Arial", 12, "bold")).pack(pady=10)
            
            # Create radio buttons for selection
            selected_option = tk.StringVar(value="")
            
            for option in delete_options:
                ttk.Radiobutton(
                    dialog, 
                    text=option, 
                    variable=selected_option, 
                    value=option
                ).pack(anchor="w", padx=20, pady=5)
            
            def confirm_delete():
                option = selected_option.get()
                if not option:
                    messagebox.showwarning("No Selection", "Please select what to delete.")
                    return
                
                # Confirm deletion
                if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {option}?\n\nThis action cannot be undone!"):
                    if option == "All Items":
                        self.db_manager.clear_items()
                        messagebox.showinfo("Success", "All items deleted successfully!")
                    elif option == "All Bills":
                        self.db_manager.clear_bills()
                        messagebox.showinfo("Success", "All bills deleted successfully!")
                    elif option == "All Users":
                        # Don't delete admin user
                        users = self.db_manager.get_all_users()
                        for user in users:
                            if user['username'] != 'admin':
                                self.db_manager.delete_user(user['id'])
                        messagebox.showinfo("Success", "All non-admin users deleted successfully!")
                    else:
                        messagebox.showinfo("Info", f"Selected deletion for {option} - implementation needed")
                    
                    self.refresh_data()
                    dialog.destroy()
            
            # Buttons
            button_frame = ttk.Frame(dialog)
            button_frame.pack(pady=20)
            
            ttk.Button(button_frame, text="Delete", command=confirm_delete).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete selected data: {str(e)}")
    
    def delete_all_data(self):
        """Delete all data from database (except admin user)"""
        try:
            # Show warning dialog
            warning_msg = """
⚠️ DANGER: DELETE ALL DATA ⚠️

This will permanently delete:
• All items
• All bills  
• All users (except admin)

This action CANNOT be undone!

Are you absolutely sure you want to continue?
            """
            
            if messagebox.askyesno("⚠️ DANGER: Delete All Data", warning_msg):
                # Second confirmation
                if messagebox.askyesno("Final Confirmation", "LAST WARNING!\n\nThis will delete EVERYTHING except admin user.\n\nType 'DELETE ALL' to confirm or click No to cancel."):
                    
                    # Clear all data
                    self.db_manager.clear_items()
                    self.db_manager.clear_bills()
                    
                    # Delete all users except admin
                    users = self.db_manager.get_all_users()
                    for user in users:
                        if user['username'] != 'admin':
                            self.db_manager.delete_user(user['id'])
                    
                    messagebox.showinfo("Success", "✅ All data deleted successfully!\n\nAdmin user preserved.")
                    self.refresh_data()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete all data: {str(e)}")
    
    def refresh_data(self):
        """Refresh dashboard data"""
        self.load_dashboard_data()
