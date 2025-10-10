#!/usr/bin/env python3
"""
Billing History Window for DROP Clothing Shop Billing Application
Displays billing history with filtering and download options
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os
import webbrowser

from src.database.database_manager import DatabaseManager
from src.config.config import Config

class BillingHistoryWindow(ttk.Frame):
    def __init__(self, parent, db_manager: DatabaseManager, config: Config):
        super().__init__(parent)
        self.db_manager = db_manager
        self.config = config
        
        self.create_widgets()
        self.load_bills()
    
    def create_widgets(self):
        """Create billing history widgets"""
        # Title
        title_label = ttk.Label(self, text="Billing History", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Filter frame
        filter_frame = ttk.LabelFrame(self, text="Filters", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Date range selection with calendar buttons
        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        # From Date
        from_date_frame = ttk.Frame(date_frame)
        from_date_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(from_date_frame, text="From Date:").pack(anchor="w")
        from_input_frame = ttk.Frame(from_date_frame)
        from_input_frame.pack(fill=tk.X, pady=(2, 0))
        
        self.from_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        self.from_date_entry = ttk.Entry(from_input_frame, textvariable=self.from_date_var, width=12)
        self.from_date_entry.pack(side=tk.LEFT)
        
        from_cal_button = ttk.Button(
            from_input_frame, 
            text="📅", 
            command=lambda: self.open_date_calendar('from'),
            width=3
        )
        from_cal_button.pack(side=tk.LEFT, padx=(2, 0))
        
        # To Date
        to_date_frame = ttk.Frame(date_frame)
        to_date_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(to_date_frame, text="To Date:").pack(anchor="w")
        to_input_frame = ttk.Frame(to_date_frame)
        to_input_frame.pack(fill=tk.X, pady=(2, 0))
        
        self.to_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.to_date_entry = ttk.Entry(to_input_frame, textvariable=self.to_date_var, width=12)
        self.to_date_entry.pack(side=tk.LEFT)
        
        to_cal_button = ttk.Button(
            to_input_frame, 
            text="📅", 
            command=lambda: self.open_date_calendar('to'),
            width=3
        )
        to_cal_button.pack(side=tk.LEFT, padx=(2, 0))
        
        # Quick date buttons
        quick_dates_frame = ttk.Frame(date_frame)
        quick_dates_frame.pack(side=tk.RIGHT)
        
        ttk.Label(quick_dates_frame, text="Quick Select:", font=("Arial", 9)).pack(anchor="w")
        quick_buttons_frame = ttk.Frame(quick_dates_frame)
        quick_buttons_frame.pack(fill=tk.X, pady=(2, 0))
        
        today_btn = ttk.Button(quick_buttons_frame, text="Today", command=lambda: self.set_quick_date('today'), width=8)
        today_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        week_btn = ttk.Button(quick_buttons_frame, text="This Week", command=lambda: self.set_quick_date('week'), width=8)
        week_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        month_btn = ttk.Button(quick_buttons_frame, text="This Month", command=lambda: self.set_quick_date('month'), width=8)
        month_btn.pack(side=tk.LEFT)
        
        # Filter buttons
        filter_buttons_frame = ttk.Frame(filter_frame)
        filter_buttons_frame.pack(fill=tk.X)
        
        filter_button = ttk.Button(
            filter_buttons_frame,
            text="Filter Bills",
            command=self.filter_bills,
            style="Accent.TButton"
        )
        filter_button.pack(side=tk.LEFT, padx=(0, 10))
        
        export_button = ttk.Button(
            filter_buttons_frame,
            text="Export to CSV",
            command=self.export_to_csv
        )
        export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_button = ttk.Button(
            filter_buttons_frame,
            text="Refresh",
            command=self.load_bills
        )
        refresh_button.pack(side=tk.LEFT)
        
        # Bills table frame
        table_frame = ttk.LabelFrame(self, text="Bills", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for bills
        columns = ("Bill No", "Date", "Time", "Amount", "Payment", "Staff", "Actions")
        self.bills_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        column_widths = {"Bill No": 120, "Date": 100, "Time": 80, "Amount": 100, "Payment": 80, "Staff": 100, "Actions": 100}
        for col in columns:
            self.bills_tree.heading(col, text=col)
            self.bills_tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.bills_tree.yview)
        self.bills_tree.configure(yscrollcommand=scrollbar.set)
        
        self.bills_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.bills_tree.bind('<Double-1>', self.view_bill_details)
        
        # Summary frame
        summary_frame = ttk.LabelFrame(self, text="Summary", padding="10")
        summary_frame.pack(fill=tk.X, pady=(10, 0))
        
        summary_content_frame = ttk.Frame(summary_frame)
        summary_content_frame.pack(fill=tk.X)
        
        self.total_bills_label = ttk.Label(summary_content_frame, text="Total Bills: 0")
        self.total_bills_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.total_amount_label = ttk.Label(summary_content_frame, text="Total Amount: ₹0.00")
        self.total_amount_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.avg_amount_label = ttk.Label(summary_content_frame, text="Average: ₹0.00")
        self.avg_amount_label.pack(side=tk.LEFT)
    
    def load_bills(self):
        """Load bills from database"""
        try:
            # Clear existing items
            for item in self.bills_tree.get_children():
                self.bills_tree.delete(item)
            
            # Get date range
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            
            # Get bills from database
            bills = self.db_manager.get_bills_by_date_range(from_date, to_date)
            
            total_amount = 0
            
            # Add bills to treeview
            for bill in bills:
                # Parse datetime
                bill_datetime = datetime.strptime(bill['created_at'], '%Y-%m-%d %H:%M:%S')
                date_str = bill_datetime.strftime('%d/%m/%Y')
                time_str = bill_datetime.strftime('%H:%M')
                
                # Add to tree
                self.bills_tree.insert("", "end", values=(
                    bill['bill_number'],
                    date_str,
                    time_str,
                    f"₹{bill['total_amount']:.2f}",
                    bill['payment_method'].upper(),
                    bill['staff_username'],
                    "View Details"
                ), tags=(bill['id'],))
                
                total_amount += bill['total_amount']
            
            # Update summary
            self.update_summary(len(bills), total_amount)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bills: {str(e)}")
    
    def filter_bills(self):
        """Filter bills based on date range"""
        try:
            # Validate date inputs
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            
            # Validate date format
            datetime.strptime(from_date, '%Y-%m-%d')
            datetime.strptime(to_date, '%Y-%m-%d')
            
            # Load bills with new filter
            self.load_bills()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter dates in YYYY-MM-DD format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter bills: {str(e)}")
    
    def view_bill_details(self, event):
        """View detailed bill information"""
        try:
            selection = self.bills_tree.selection()
            if not selection:
                return
            
            # Get selected bill ID
            bill_id = int(self.bills_tree.item(selection[0])['tags'][0])
            
            # Get bill details
            bill_details = self.db_manager.get_bill_details(bill_id)
            
            if bill_details:
                self.show_bill_details_window(bill_details)
            else:
                messagebox.showerror("Error", "Failed to load bill details")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view bill details: {str(e)}")
    
    def show_bill_details_window(self, bill_details: dict):
        """Show bill details in a new window"""
        try:
            # Create new window
            details_window = tk.Toplevel(self)
            details_window.title(f"Bill Details - {bill_details['bill_number']}")
            details_window.geometry("600x500")
            details_window.resizable(False, False)
            
            # Main frame
            main_frame = ttk.Frame(details_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Bill header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 20))
            
            ttk.Label(header_frame, text="DROP", font=("Arial", 20, "bold")).pack()
            ttk.Label(header_frame, text="DRESS FOR LESS", font=("Arial", 12, "italic")).pack()
            
            # Bill info
            bill_info_frame = ttk.Frame(main_frame)
            bill_info_frame.pack(fill=tk.X, pady=(0, 20))
            
            bill_date = datetime.strptime(bill_details['created_at'], '%Y-%m-%d %H:%M:%S')
            
            ttk.Label(bill_info_frame, text=f"Bill Number: {bill_details['bill_number']}").pack(anchor="w")
            ttk.Label(bill_info_frame, text=f"Date: {bill_date.strftime('%d/%m/%Y %H:%M')}").pack(anchor="w")
            ttk.Label(bill_info_frame, text=f"Staff: {bill_details['staff_username']}").pack(anchor="w")
            ttk.Label(bill_info_frame, text=f"Payment: {bill_details['payment_method'].upper()}").pack(anchor="w")
            
            # Items table
            items_frame = ttk.LabelFrame(main_frame, text="Items", padding="10")
            items_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            # Create items treeview
            item_columns = ("Item", "Code", "Qty", "Price", "Total")
            items_tree = ttk.Treeview(items_frame, columns=item_columns, show="headings", height=8)
            
            for col in item_columns:
                items_tree.heading(col, text=col)
                items_tree.column(col, width=100)
            
            # Add items
            for item in bill_details['items']:
                items_tree.insert("", "end", values=(
                    item['item_name'],
                    item['item_code'],
                    item['quantity'],
                    f"₹{item['unit_price']:.2f}",
                    f"₹{item['total_price']:.2f}"
                ))
            
            items_tree.pack(fill=tk.BOTH, expand=True)
            
            # Total
            total_frame = ttk.Frame(main_frame)
            total_frame.pack(fill=tk.X)
            
            ttk.Label(total_frame, text=f"TOTAL: ₹{bill_details['total_amount']:.2f}", 
                     font=("Arial", 14, "bold")).pack(side=tk.RIGHT)
            
            # Close button
            ttk.Button(main_frame, text="Close", command=details_window.destroy).pack(pady=(10, 0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show bill details: {str(e)}")
    
    def export_to_csv(self):
        """Export bills to CSV file"""
        try:
            # Get date range
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            
            # Get bills
            bills = self.db_manager.get_bills_by_date_range(from_date, to_date)
            
            if not bills:
                messagebox.showwarning("Warning", "No bills found to export")
                return
            
            # Open file dialog
            filename = f"bills_export_{from_date}_to_{to_date}.csv"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialname=filename
            )
            
            if file_path:
                # Write CSV file
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    import csv
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow(['Bill Number', 'Date', 'Time', 'Total Amount', 'Payment Method', 'Staff'])
                    
                    # Write data
                    for bill in bills:
                        bill_datetime = datetime.strptime(bill['created_at'], '%Y-%m-%d %H:%M:%S')
                        writer.writerow([
                            bill['bill_number'],
                            bill_datetime.strftime('%d/%m/%Y'),
                            bill_datetime.strftime('%H:%M'),
                            bill['total_amount'],
                            bill['payment_method'],
                            bill['staff_username']
                        ])
                
                messagebox.showinfo("Success", f"Bills exported successfully to {file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export bills: {str(e)}")
    
    def open_date_calendar(self, date_type):
        """Open a visual calendar picker dialog"""
        try:
            # Get current date value
            if date_type == 'from':
                current_date = self.from_date_var.get()
            else:
                current_date = self.to_date_var.get()
            
            # Parse current date
            try:
                current_dt = datetime.strptime(current_date, '%Y-%m-%d')
            except ValueError:
                current_dt = datetime.now()
            
            # Create professional calendar window - Much larger for better button visibility
            calendar_window = tk.Toplevel(self.winfo_toplevel())
            calendar_window.title(f"📅 Select {date_type.title()} Date")
            calendar_window.geometry("500x600")
            calendar_window.resizable(False, False)
            calendar_window.configure(bg='#f8f9fa')
            
            # Center the window
            calendar_window.update_idletasks()
            x = (calendar_window.winfo_screenwidth() // 2) - (250)
            y = (calendar_window.winfo_screenheight() // 2) - (300)
            calendar_window.geometry(f"500x600+{x}+{y}")
            
            # Make window modal
            calendar_window.transient(self.winfo_toplevel())
            calendar_window.grab_set()
            
            # Main container with professional styling
            main_container = tk.Frame(calendar_window, bg='#f8f9fa')
            main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            # Calendar card with shadow effect
            cal_card = tk.Frame(main_container, bg='white', relief='raised', bd=2)
            cal_card.pack(fill=tk.BOTH, expand=True)
            
            # Professional header
            header_frame = tk.Frame(cal_card, bg='#2c3e50', height=60)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            # Title with icon
            title_label = tk.Label(
                header_frame, 
                text=f"📅 Select {date_type.title()} Date", 
                font=("Segoe UI", 14, "bold"),
                fg='white',
                bg='#2c3e50'
            )
            title_label.pack(expand=True)
            
            # Calendar content area
            cal_frame = tk.Frame(cal_card, bg='white', padx=20, pady=20)
            cal_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create professional calendar widget
            calendar_widget = self.create_calendar_widget(cal_frame, current_dt)
            calendar_widget.pack(pady=(0, 20))
            
            # Professional buttons frame with better spacing
            buttons_frame = tk.Frame(cal_frame, bg='white')
            buttons_frame.pack(fill=tk.X, pady=(20, 0))
            
            # Button styling - Larger buttons for better visibility
            button_style = {
                'font': ('Arial', 12, 'bold'),
                'relief': 'flat',
                'bd': 0,
                'padx': 30,
                'pady': 12,
                'cursor': 'hand2',
                'width': 10
            }
            
            # Today button (left)
            today_btn = tk.Button(
                buttons_frame, 
                text="📅 Today", 
                command=lambda: self.set_calendar_today(calendar_widget),
                bg='#3498db',
                fg='white',
                **button_style
            )
            today_btn.pack(side=tk.LEFT, padx=(0, 15))
            
            # Spacer to push action buttons to the right
            spacer = tk.Frame(buttons_frame, bg='white')
            spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Cancel button (right)
            cancel_btn = tk.Button(
                buttons_frame, 
                text="❌ Cancel", 
                command=calendar_window.destroy,
                bg='#e74c3c',
                fg='white',
                **button_style
            )
            cancel_btn.pack(side=tk.RIGHT, padx=(15, 0))
            
            # OK button (right of cancel)
            ok_btn = tk.Button(
                buttons_frame, 
                text="✅ OK", 
                command=lambda: self.select_calendar_date(calendar_widget, date_type, calendar_window),
                bg='#27ae60',
                fg='white',
                **button_style
            )
            ok_btn.pack(side=tk.RIGHT, padx=(0, 15))
            
            # Store reference for callbacks
            calendar_widget.date_type = date_type
            calendar_widget.window = calendar_window
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open calendar: {str(e)}")
    
    def create_calendar_widget(self, parent, current_date):
        """Create a professional calendar widget"""
        try:
            # Calendar container with professional styling
            cal_container = tk.Frame(parent, bg='white')
            
            # Professional navigation bar
            nav_frame = tk.Frame(cal_container, bg='#34495e', height=60)
            nav_frame.pack(fill=tk.X, pady=(0, 10))
            nav_frame.pack_propagate(False)
            
            # Navigation buttons container
            nav_buttons_frame = tk.Frame(nav_frame, bg='#34495e')
            nav_buttons_frame.pack(expand=True)
            
            # Previous year button
            prev_year_btn = tk.Button(
                nav_buttons_frame, 
                text="◀◀", 
                font=("Arial", 12, "bold"),
                command=lambda: self.change_year(-1, cal_container, current_date),
                bg='#34495e',
                fg='white',
                relief='flat',
                bd=0,
                width=2,
                height=1
            )
            prev_year_btn.pack(side=tk.LEFT, padx=2)
            
            # Previous month button
            prev_btn = tk.Button(
                nav_buttons_frame, 
                text="◀", 
                font=("Arial", 14, "bold"),
                command=lambda: self.change_month(-1, cal_container, current_date),
                bg='#34495e',
                fg='white',
                relief='flat',
                bd=0,
                width=3,
                height=1
            )
            prev_btn.pack(side=tk.LEFT, padx=2)
            
            # Month/Year label (clickable for quick navigation)
            self.current_cal_date = current_date
            self.month_label = tk.Label(
                nav_buttons_frame, 
                text=current_date.strftime("%B %Y"), 
                font=("Segoe UI", 14, "bold"),
                bg='#34495e',
                fg='white',
                cursor='hand2'
            )
            self.month_label.pack(side=tk.LEFT, padx=10, pady=10)
            self.month_label.bind("<Button-1>", lambda e: self.show_year_picker(cal_container, current_date))
            
            # Next month button
            next_btn = tk.Button(
                nav_buttons_frame, 
                text="▶", 
                font=("Arial", 14, "bold"),
                command=lambda: self.change_month(1, cal_container, current_date),
                bg='#34495e',
                fg='white',
                relief='flat',
                bd=0,
                width=3,
                height=1
            )
            next_btn.pack(side=tk.RIGHT, padx=2)
            
            # Next year button
            next_year_btn = tk.Button(
                nav_buttons_frame, 
                text="▶▶", 
                font=("Arial", 12, "bold"),
                command=lambda: self.change_year(1, cal_container, current_date),
                bg='#34495e',
                fg='white',
                relief='flat',
                bd=0,
                width=2,
                height=1
            )
            next_year_btn.pack(side=tk.RIGHT, padx=2)
            
            # Calendar grid container - Fixed height to ensure buttons are visible
            self.cal_grid_frame = tk.Frame(cal_container, bg='white', height=350)
            self.cal_grid_frame.pack(fill=tk.X, padx=5, pady=5)
            self.cal_grid_frame.pack_propagate(False)
            
            # Build initial calendar
            self.build_calendar_grid(current_date)
            
            return cal_container
            
        except Exception as e:
            print(f"Error creating calendar widget: {e}")
            return tk.Frame(parent, bg='white')
    
    def build_calendar_grid(self, date):
        """Build a professional calendar grid"""
        try:
            # Clear existing grid
            for widget in self.cal_grid_frame.winfo_children():
                widget.destroy()
            
            # Get first day of month and last day of month properly
            first_day = date.replace(day=1)
            
            # Calculate last day of current month properly
            if date.month == 12:
                next_month = first_day.replace(year=first_day.year + 1, month=1)
            else:
                next_month = first_day.replace(month=first_day.month + 1)
            
            last_day = next_month - timedelta(days=1)
            
            # Professional day headers with styling
            day_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for i, day in enumerate(day_headers):
                header_label = tk.Label(
                    self.cal_grid_frame, 
                    text=day, 
                    font=("Segoe UI", 10, "bold"),
                    bg='#ecf0f1',
                    fg='#2c3e50',
                    relief='flat'
                )
                header_label.grid(row=0, column=i, sticky='ew', padx=1, pady=1)
            
            # Configure grid columns to be equal width
            for i in range(7):
                self.cal_grid_frame.grid_columnconfigure(i, weight=1)
            
            # Calculate starting position (Monday = 0)
            start_col = (first_day.weekday()) % 7
            
            # Create professional day buttons
            row = 1
            col = start_col
            
            for day in range(1, last_day.day + 1):
                day_date = first_day.replace(day=day)
                is_today = day_date.date() == datetime.now().date()
                is_weekend = day_date.weekday() >= 5  # Saturday = 5, Sunday = 6
                
                # Professional button styling
                if is_today:
                    btn_bg = '#3498db'  # Blue for today
                    btn_fg = 'white'
                    btn_relief = 'raised'
                elif is_weekend:
                    btn_bg = '#f8f9fa'  # Light gray for weekends
                    btn_fg = '#6c757d'
                    btn_relief = 'flat'
                else:
                    btn_bg = 'white'    # White for weekdays
                    btn_fg = '#2c3e50'
                    btn_relief = 'flat'
                
                # Create professional day button
                day_btn = tk.Button(
                    self.cal_grid_frame,
                    text=str(day),
                    font=("Segoe UI", 10),
                    command=lambda d=day_date: self.select_date(d),
                    bg=btn_bg,
                    fg=btn_fg,
                    relief=btn_relief,
                    bd=1,
                    width=4,
                    height=2,
                    cursor='hand2'
                )
                
                day_btn.grid(row=row, column=col, sticky='ew', padx=1, pady=1)
                
                # Add hover effects (basic)
                day_btn.bind("<Enter>", lambda e, btn=day_btn: btn.configure(bg='#e9ecef' if btn.cget('bg') != '#3498db' else '#2980b9'))
                day_btn.bind("<Leave>", lambda e, btn=day_btn, orig_bg=btn_bg: btn.configure(bg=orig_bg))
                
                # Move to next column
                col += 1
                if col > 6:
                    col = 0
                    row += 1
            
            # Store selected date
            self.selected_calendar_date = None
            
        except Exception as e:
            print(f"Error building calendar grid: {e}")
    
    def change_month(self, direction, container, current_date):
        """Change month in calendar with proper year handling"""
        try:
            # Get the current calendar date
            if hasattr(self, 'current_cal_date'):
                base_date = self.current_cal_date
            else:
                base_date = current_date
            
            if direction == 1:  # Next month
                if base_date.month == 12:
                    new_date = base_date.replace(year=base_date.year + 1, month=1)
                else:
                    new_date = base_date.replace(month=base_date.month + 1)
            else:  # Previous month
                if base_date.month == 1:
                    new_date = base_date.replace(year=base_date.year - 1, month=12)
                else:
                    new_date = base_date.replace(month=base_date.month - 1)
            
            # Update current calendar date
            self.current_cal_date = new_date
            
            # Update month label
            self.month_label.config(text=new_date.strftime("%B %Y"))
            
            # Rebuild calendar grid with new date
            self.build_calendar_grid(new_date)
            
        except Exception as e:
            print(f"Error changing month: {e}")
    
    def change_year(self, direction, container, current_date):
        """Change year in calendar"""
        try:
            # Get the current calendar date
            if hasattr(self, 'current_cal_date'):
                base_date = self.current_cal_date
            else:
                base_date = current_date
            
            # Change year
            new_date = base_date.replace(year=base_date.year + direction)
            
            # Update current calendar date
            self.current_cal_date = new_date
            
            # Update month label
            self.month_label.config(text=new_date.strftime("%B %Y"))
            
            # Rebuild calendar grid with new date
            self.build_calendar_grid(new_date)
            
        except Exception as e:
            print(f"Error changing year: {e}")
    
    def show_year_picker(self, container, current_date):
        """Show year picker dialog"""
        try:
            from tkinter import simpledialog
            
            # Get current year
            current_year = current_date.year
            
            # Ask for year
            new_year = simpledialog.askinteger(
                "Select Year",
                "Enter year:",
                initialvalue=current_year,
                minvalue=1900,
                maxvalue=2100
            )
            
            if new_year:
                # Create new date with selected year
                new_date = current_date.replace(year=new_year)
                
                # Update current calendar date
                self.current_cal_date = new_date
                
                # Update month label
                self.month_label.config(text=new_date.strftime("%B %Y"))
                
                # Rebuild calendar grid
                self.build_calendar_grid(new_date)
                
        except Exception as e:
            print(f"Error showing year picker: {e}")
    
    def set_calendar_today(self, calendar_widget):
        """Set calendar to today's date"""
        try:
            today = datetime.now()
            self.current_cal_date = today
            self.month_label.config(text=today.strftime("%B %Y"))
            self.build_calendar_grid(today)
        except Exception as e:
            print(f"Error setting calendar to today: {e}")
    
    def select_date(self, date):
        """Select a date from calendar with professional highlighting"""
        try:
            self.selected_calendar_date = date
            
            # Reset all buttons to their default styling first
            for widget in self.cal_grid_frame.winfo_children():
                if isinstance(widget, tk.Button):
                    # Get the date for this button
                    try:
                        widget_day = int(widget.cget("text"))
                        widget_date = self.current_cal_date.replace(day=widget_day)
                        
                        # Determine original styling
                        is_today = widget_date.date() == datetime.now().date()
                        is_weekend = widget_date.weekday() >= 5
                        
                        if is_today:
                            widget.configure(bg='#3498db', fg='white', relief='raised')
                        elif is_weekend:
                            widget.configure(bg='#f8f9fa', fg='#6c757d', relief='flat')
                        else:
                            widget.configure(bg='white', fg='#2c3e50', relief='flat')
                            
                    except ValueError:
                        continue
            
            # Highlight selected date
            for widget in self.cal_grid_frame.winfo_children():
                if isinstance(widget, tk.Button) and widget.cget("text") == str(date.day):
                    widget.configure(bg='#e74c3c', fg='white', relief='raised', bd=2)
                    break
            
        except Exception as e:
            print(f"Error selecting date: {e}")
    
    def select_calendar_date(self, calendar_widget, date_type, window):
        """Confirm date selection and close calendar"""
        try:
            if self.selected_calendar_date:
                date_str = self.selected_calendar_date.strftime('%Y-%m-%d')
                
                # Update the appropriate date variable
                if date_type == 'from':
                    self.from_date_var.set(date_str)
                else:
                    self.to_date_var.set(date_str)
                
                # Close calendar window
                window.destroy()
            else:
                messagebox.showwarning("No Date Selected", "Please select a date from the calendar")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select date: {str(e)}")
            window.destroy()
    
    def set_quick_date(self, period):
        """Set quick date ranges"""
        try:
            today = datetime.now()
            
            if period == 'today':
                date_str = today.strftime('%Y-%m-%d')
                self.from_date_var.set(date_str)
                self.to_date_var.set(date_str)
                
            elif period == 'week':
                # Start of week (Monday)
                start_of_week = today - timedelta(days=today.weekday())
                self.from_date_var.set(start_of_week.strftime('%Y-%m-%d'))
                self.to_date_var.set(today.strftime('%Y-%m-%d'))
                
            elif period == 'month':
                # Start of month
                start_of_month = today.replace(day=1)
                self.from_date_var.set(start_of_month.strftime('%Y-%m-%d'))
                self.to_date_var.set(today.strftime('%Y-%m-%d'))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set quick date: {str(e)}")
    
    def update_summary(self, total_bills: int, total_amount: float):
        """Update summary labels"""
        self.total_bills_label.config(text=f"Total Bills: {total_bills}")
        self.total_amount_label.config(text=f"Total Amount: ₹{total_amount:.2f}")
        
        if total_bills > 0:
            avg_amount = total_amount / total_bills
            self.avg_amount_label.config(text=f"Average: ₹{avg_amount:.2f}")
        else:
            self.avg_amount_label.config(text="Average: ₹0.00")
