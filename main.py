#!/usr/bin/env python3
"""
DROP Clothing Shop Billing Application
Main entry point for the application
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.database_manager import DatabaseManager
from src.ui.login_window import LoginWindow
from src.ui.admin_dashboard import AdminDashboard
from src.config.config import Config

class DropBillingApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DROP - Dress for Less")
        
        # Make window responsive and full-screen friendly
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Set minimum window size
        self.root.minsize(800, 600)
        
        # Add window state management
        self.root.state('normal')  # Ensure window is not maximized initially
        
        # Center window on screen
        self.center_window()
        
        # Bind resize event for responsive behavior
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Initialize database
        self.db_manager = DatabaseManager()
        self.db_manager.initialize_database()
        
        # Initialize config
        self.config = Config()
        
        # Initialize dashboard reference
        self.admin_dashboard = None
        
        # Set application icon and styling
        self.setup_styling()
        
        # Show main selection window
        self.show_main_selection()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_window_resize(self, event):
        """Handle window resize events for responsive behavior"""
        if event.widget == self.root:
            # Update window title to show current size (optional, for debugging)
            current_size = f"{event.width}x{event.height}"
            if hasattr(self, 'admin_dashboard') and self.admin_dashboard:
                # Handle admin dashboard resize
                pass
            elif hasattr(self, 'staff_dashboard') and self.staff_dashboard:
                # Handle staff dashboard resize
                pass
        
    def setup_styling(self):
        """Setup application styling and theme"""
        self.root.configure(bg='#f0f0f0')
        
        # Set window icon (you can add an icon file later)
        try:
            # self.root.iconbitmap('assets/icon.ico')  # Uncomment when icon is available
            pass
        except (OSError, IOError):
            pass
    
    def show_main_selection(self):
        """Show main selection window"""
        try:
            # Clear any existing widgets
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Update window title and size - make it more responsive
            self.root.title("DROP - Dress for Less")
            self.root.geometry("600x450")
            self.root.resizable(True, True)
            self.root.minsize(500, 400)
            
            # Center window
            self.center_window()
            
            # Main frame
            main_frame = ttk.Frame(self.root, padding="40")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(pady=(0, 50))
            
            title_label = ttk.Label(
                header_frame,
                text="DROP",
                font=("Arial", 36, "bold")
            )
            title_label.pack()
            
            subtitle_label = ttk.Label(
                header_frame,
                text="DRESS FOR LESS",
                font=("Arial", 16, "italic")
            )
            subtitle_label.pack()
            
            # Selection frame
            selection_frame = ttk.LabelFrame(main_frame, text="Select Access Type", padding="30")
            selection_frame.pack(fill=tk.BOTH, expand=True)
            
            # Admin button
            admin_button = ttk.Button(
                selection_frame,
                text="ADMIN LOGIN",
                command=self.open_admin_login,
                width=25,
                style="Accent.TButton"
            )
            admin_button.pack(pady=(0, 20))
            
            # Staff button
            staff_button = ttk.Button(
                selection_frame,
                text="STAFF BILLING",
                command=self.open_staff_billing,
                width=25
            )
            staff_button.pack()
            
            # Info label
            info_label = ttk.Label(
                selection_frame,
                text="Admin: Manage items, settings, and reports\nStaff: Process sales and generate bills",
                font=("Arial", 10),
                foreground="gray",
                justify=tk.CENTER
            )
            info_label.pack(pady=(20, 0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open selection window: {str(e)}")
    
    def open_admin_login(self):
        """Open admin login window"""
        try:
            # Clear main window
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Create login window
            from src.ui.login_window import LoginWindow
            self.login_window = LoginWindow(self.root, self.db_manager, self.config)
            self.login_window.set_login_success_callback(self.on_admin_login_success)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open admin login: {str(e)}")
    
    def on_admin_login_success(self, user):
        """Handle successful admin login"""
        try:
            # Clear login window
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Make window larger for admin dashboard
            self.root.geometry("1200x800")
            self.center_window()
            
            # Show admin dashboard with reference to main app
            self.admin_dashboard = AdminDashboard(self.root, self.db_manager, self.config, user)
            # Store reference to main app in the dashboard
            self.admin_dashboard.main_app = self
            # Pack the admin dashboard to make it visible
            self.admin_dashboard.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open admin dashboard: {str(e)}")
    
    def open_staff_billing(self):
        """Open staff billing interface directly"""
        try:
            # Create a default staff user object
            staff_user = {
                'id': 1,
                'username': 'staff',
                'user_type': 'staff',
                'last_login': None
            }
            
            # Clear main window
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Update window title and size - make it much larger for full visibility
            self.root.title("DROP - Staff Billing")
            self.root.geometry("1600x1000")
            self.root.resizable(True, True)
            self.root.minsize(1200, 800)
            
            # Center window
            self.center_window()
            
            # Create staff dashboard with reference to main app
            from src.ui.staff_dashboard import StaffDashboard
            self.staff_dashboard = StaffDashboard(self.root, self.db_manager, self.config, staff_user)
            # Store reference to main app in the dashboard
            self.staff_dashboard.main_app = self
            # Pack the staff dashboard to make it visible
            self.staff_dashboard.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open staff billing: {str(e)}")
    
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources before closing"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        self.root.quit()

def main():
    """Main function to start the application"""
    try:
        app = DropBillingApp()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
