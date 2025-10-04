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
        
        # Date range selection
        date_frame = ttk.Frame(filter_frame)
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(date_frame, text="From Date:").pack(side=tk.LEFT, padx=(0, 5))
        self.from_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        self.from_date_entry = ttk.Entry(date_frame, textvariable=self.from_date_var, width=12)
        self.from_date_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(date_frame, text="To Date:").pack(side=tk.LEFT, padx=(0, 5))
        self.to_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.to_date_entry = ttk.Entry(date_frame, textvariable=self.to_date_var, width=12)
        self.to_date_entry.pack(side=tk.LEFT, padx=(0, 20))
        
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
    
    def update_summary(self, total_bills: int, total_amount: float):
        """Update summary labels"""
        self.total_bills_label.config(text=f"Total Bills: {total_bills}")
        self.total_amount_label.config(text=f"Total Amount: ₹{total_amount:.2f}")
        
        if total_bills > 0:
            avg_amount = total_amount / total_bills
            self.avg_amount_label.config(text=f"Average: ₹{avg_amount:.2f}")
        else:
            self.avg_amount_label.config(text="Average: ₹0.00")
