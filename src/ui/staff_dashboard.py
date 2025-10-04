#!/usr/bin/env python3
"""
Staff Dashboard for DROP Clothing Shop Billing Application
Provides billing interface with cart functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict
from datetime import datetime

from src.database.database_manager import DatabaseManager
from src.config.config import Config
from src.ui.bill_generator import BillGenerator

class StaffDashboard(ttk.Frame):
    def __init__(self, parent, db_manager: DatabaseManager, config: Config, current_user: Dict):
        super().__init__(parent)
        self.db_manager = db_manager
        self.config = config
        self.current_user = current_user
        self.cart_items = []
        
        # Initialize bill generator
        try:
            self.bill_generator = BillGenerator(db_manager, config)
        except Exception as e:
            print(f"Warning: Could not initialize bill generator: {e}")
            self.bill_generator = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create staff dashboard widgets"""
        try:
            # Configure the frame
            self.configure(relief="flat", borderwidth=0)
            
            # Create main scrollable frame
            self.main_scrollable_frame = ttk.Frame(self)
            self.main_scrollable_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create canvas for scrolling
            self.canvas = tk.Canvas(self.main_scrollable_frame, highlightthickness=0)
            self.scrollbar = ttk.Scrollbar(self.main_scrollable_frame, orient=tk.VERTICAL, command=self.canvas.yview)
            self.scrollable_frame = ttk.Frame(self.canvas)
            
            # Configure scrolling
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            )
            
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            
            # Pack canvas and scrollbar
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Bind mousewheel to canvas
            self.bind_mousewheel()
            
            # Header with title and back button
            header_frame = ttk.Frame(self.scrollable_frame)
            header_frame.pack(fill=tk.X, padx=20, pady=10)
            
            # Back to main button
            back_button = ttk.Button(
                header_frame,
                text="← Back to Main",
                command=self.go_back_to_main,
                width=15
            )
            back_button.pack(side=tk.LEFT)
            
            # Title
            title_label = ttk.Label(header_frame, text="DROP - Staff Billing", font=("Arial", 18, "bold"))
            title_label.pack(side=tk.LEFT, padx=(20, 0))
            
            # Spacer
            ttk.Frame(header_frame).pack(side=tk.RIGHT, expand=True)
            
            # Main content frame with left and right sections
            main_frame = ttk.Frame(self.scrollable_frame)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20)
            
            # Left main content area
            left_main_frame = ttk.Frame(main_frame)
            left_main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            
            # Right sidebar for additional information
            right_sidebar = ttk.Frame(main_frame, width=300)
            right_sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
            right_sidebar.pack_propagate(False)
            
            # Recent Transactions Panel
            recent_frame = ttk.LabelFrame(right_sidebar, text="Recent Transactions", padding="10")
            recent_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Recent transactions list
            recent_columns = ("Date/Time", "Amount", "Items")
            self.recent_tree = ttk.Treeview(recent_frame, columns=recent_columns, show="headings", height=8)
            
            # Configure recent transactions columns
            recent_column_widths = {"Date/Time": 90, "Amount": 80, "Items": 100}
            for col in recent_columns:
                self.recent_tree.heading(col, text=col)
                self.recent_tree.column(col, width=recent_column_widths.get(col, 80))
            
            # Recent transactions scrollbar
            recent_scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=self.recent_tree.yview)
            self.recent_tree.configure(yscrollcommand=recent_scrollbar.set)
            
            self.recent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            recent_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Quick Stats Panel
            stats_frame = ttk.LabelFrame(right_sidebar, text="Today's Stats", padding="10")
            stats_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Stats labels
            self.today_bills_label = ttk.Label(stats_frame, text="Bills Today: 0", font=("Arial", 10))
            self.today_bills_label.pack(anchor="w", pady=2)
            
            self.today_amount_label = ttk.Label(stats_frame, text="Amount Today: ₹0.00", font=("Arial", 10))
            self.today_amount_label.pack(anchor="w", pady=2)
            
            self.today_items_label = ttk.Label(stats_frame, text="Items Sold: 0", font=("Arial", 10))
            self.today_items_label.pack(anchor="w", pady=2)
            
            # Quick Actions Panel
            actions_frame = ttk.LabelFrame(right_sidebar, text="Quick Actions", padding="10")
            actions_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Quick action buttons
            refresh_stats_btn = ttk.Button(actions_frame, text="🔄 Refresh Stats", command=self.refresh_stats, width=20)
            refresh_stats_btn.pack(fill=tk.X, pady=2)
            
            view_recent_btn = ttk.Button(actions_frame, text="📋 View All Bills", command=self.view_all_bills, width=20)
            view_recent_btn.pack(fill=tk.X, pady=2)
            
            # Payment Summary Panel
            payment_summary_frame = ttk.LabelFrame(right_sidebar, text="Payment Summary", padding="10")
            payment_summary_frame.pack(fill=tk.X)
            
            # Payment method counters
            self.cash_count_label = ttk.Label(payment_summary_frame, text="💵 Cash: 0", font=("Arial", 9))
            self.cash_count_label.pack(anchor="w", pady=1)
            
            self.upi_count_label = ttk.Label(payment_summary_frame, text="📱 UPI: 0", font=("Arial", 9))
            self.upi_count_label.pack(anchor="w", pady=1)
            
            self.card_count_label = ttk.Label(payment_summary_frame, text="💳 Card: 0", font=("Arial", 9))
            self.card_count_label.pack(anchor="w", pady=1)
            
            # Add separator
            ttk.Separator(payment_summary_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(10, 10))
            
            # Bill Summary Label - Moved to right sidebar
            self.bill_summary_label = ttk.Label(
                payment_summary_frame, 
                text="Cart is empty", 
                font=("Arial", 10), 
                foreground="gray"
            )
            self.bill_summary_label.pack(fill=tk.X, pady=(0, 10))
            
            # Generate Bill Button - Moved to right sidebar
            self.bill_button = ttk.Button(
                payment_summary_frame,
                text="🧾 GENERATE BILL & SAVE TO DATABASE",
                command=self.generate_bill,
                state=tk.DISABLED,
                width=25
            )
            self.bill_button.pack(fill=tk.X, pady=(0, 10))
        
            # Top section - Item search and barcode scanning
            search_section = ttk.LabelFrame(left_main_frame, text="Item Search & Barcode Scanner", padding="15")
            search_section.pack(fill=tk.X, pady=(0, 20))
            
            # Barcode Scanner Section
            barcode_frame = ttk.LabelFrame(search_section, text="📱 Barcode Scanner (Auto-Add to Cart)", padding="10")
            barcode_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(barcode_frame, text="Scan barcode with scanner device:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 5))
            
            # Barcode input field - this will receive scanner input
            self.barcode_var = tk.StringVar()
            self.barcode_entry = ttk.Entry(
                barcode_frame, 
                textvariable=self.barcode_var, 
                font=("Arial", 14),
                foreground="blue"
            )
            self.barcode_entry.pack(fill=tk.X, pady=(0, 5))
            self.barcode_entry.bind('<KeyRelease>', self.on_barcode_input)
            self.barcode_entry.bind('<FocusIn>', lambda e: self.barcode_entry.select_range(0, tk.END))
            
            # Barcode status label
            self.barcode_status_label = ttk.Label(
                barcode_frame, 
                text="Ready to scan barcode...", 
                font=("Arial", 10),
                foreground="gray"
            )
            self.barcode_status_label.pack(anchor="w")
            
            # Manual add button for barcode entry
            manual_add_frame = ttk.Frame(barcode_frame)
            manual_add_frame.pack(fill=tk.X, pady=(5, 0))
            
            manual_add_button = ttk.Button(
                manual_add_frame,
                text="Add to Cart",
                command=self.manual_add_barcode_item,
                width=12
            )
            manual_add_button.pack(side=tk.RIGHT)
            
            # Separator
            ttk.Separator(search_section, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
            
            # Manual Search Section
            search_frame = ttk.Frame(search_section)
            search_frame.pack(fill=tk.X)
            
            ttk.Label(search_frame, text="Or manually enter Item Code:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
            
            # Large search input with button
            search_input_frame = ttk.Frame(search_frame)
            search_input_frame.pack(fill=tk.X, pady=(0, 10))
            
            self.search_var = tk.StringVar()
            self.search_entry = ttk.Entry(search_input_frame, textvariable=self.search_var, font=("Arial", 14))
            self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            self.search_entry.bind('<Return>', self.search_item)
            
            search_button = ttk.Button(
                search_input_frame, 
                text="SEARCH", 
                command=self.search_item,
                width=10
            )
            search_button.pack(side=tk.RIGHT)
            
            # Item details frame
            item_details_frame = ttk.Frame(search_section)
            item_details_frame.pack(fill=tk.X, pady=(10, 0))
            
            self.item_info_label = ttk.Label(
                item_details_frame, 
                text="Enter item code above to search", 
                font=("Arial", 11),
                foreground="gray"
            )
            self.item_info_label.pack(anchor="w")
            
            # Quantity and add to cart frame
            quantity_frame = ttk.Frame(item_details_frame)
            quantity_frame.pack(fill=tk.X, pady=(15, 0))
            
            ttk.Label(quantity_frame, text="Quantity:", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=(0, 10))
            
            # Quantity controls with plus/minus buttons
            qty_control_frame = ttk.Frame(quantity_frame)
            qty_control_frame.pack(side=tk.LEFT, padx=(0, 20))
            
            minus_button = ttk.Button(qty_control_frame, text="-", width=3, command=self.decrease_quantity)
            minus_button.pack(side=tk.LEFT)
            
            self.quantity_var = tk.StringVar(value="1")
            self.quantity_entry = ttk.Entry(qty_control_frame, textvariable=self.quantity_var, width=5, font=("Arial", 12), justify="center")
            self.quantity_entry.pack(side=tk.LEFT, padx=5)
            
            plus_button = ttk.Button(qty_control_frame, text="+", width=3, command=self.increase_quantity)
            plus_button.pack(side=tk.LEFT)
            
            # Add to cart button
            self.add_to_cart_button = ttk.Button(
                quantity_frame,
                text="ADD TO CART",
                command=self.add_to_cart,
                state=tk.DISABLED,
                width=15
            )
            self.add_to_cart_button.pack(side=tk.LEFT)
            
            # Total amount section - Move it up for better visibility
            total_section = ttk.LabelFrame(left_main_frame, text="Total Amount", padding="15")
            total_section.pack(fill=tk.X, pady=(0, 20))
            
            # Total amount display - Large and prominent
            total_display_frame = ttk.Frame(total_section)
            total_display_frame.pack(fill=tk.X)
            
            ttk.Label(total_display_frame, text="TOTAL AMOUNT:", font=("Arial", 16, "bold")).pack()
            self.total_label = ttk.Label(total_display_frame, text="₹0.00", font=("Arial", 32, "bold"), foreground="green")
            self.total_label.pack(pady=(5, 0))
            
            # Cart section - Big cart space
            cart_section = ttk.LabelFrame(left_main_frame, text="Shopping Cart", padding="15")
            cart_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

            # Cart items list with larger space
            cart_columns = ("Item Name", "Item Code", "Quantity", "Unit Price", "Total")
            self.cart_tree = ttk.Treeview(cart_section, columns=cart_columns, show="headings", height=15)
            
            # Configure columns with better widths - more responsive and spacious
            column_widths = {"Item Name": 300, "Item Code": 180, "Quantity": 120, "Unit Price": 150, "Total": 160}
            for col in cart_columns:
                self.cart_tree.heading(col, text=col)
                self.cart_tree.column(col, width=column_widths.get(col, 100))
            
            # Cart scrollbar
            cart_scrollbar = ttk.Scrollbar(cart_section, orient=tk.VERTICAL, command=self.cart_tree.yview)
            self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
            
            self.cart_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            cart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Bind cart selection
            self.cart_tree.bind('<<TreeviewSelect>>', self.on_cart_item_select)
            
            # Bottom section - Controls and payment
            bottom_section = ttk.Frame(left_main_frame)
            bottom_section.pack(fill=tk.X, pady=(10, 0))
            bottom_section.configure(height=300)
            bottom_section.pack_propagate(False)
            
            # Left side - Cart controls
            controls_frame = ttk.LabelFrame(bottom_section, text="Cart Controls", padding="10")
            controls_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            
            controls_buttons_frame = ttk.Frame(controls_frame)
            controls_buttons_frame.pack(fill=tk.X)
            
            self.remove_item_button = ttk.Button(
                controls_buttons_frame,
                text="Remove Selected",
                command=self.remove_from_cart,
                state=tk.DISABLED,
                width=15
            )
            self.remove_item_button.pack(side=tk.LEFT, padx=(0, 10))
            
            clear_cart_button = ttk.Button(
                controls_buttons_frame,
                text="Clear All",
                command=self.clear_cart,
                width=15
            )
            clear_cart_button.pack(side=tk.LEFT)
            
            # Right side - Payment and bill generation
            payment_frame = ttk.LabelFrame(bottom_section, text="Payment & Billing", padding="15")
            payment_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
            payment_frame.configure(width=500)
            payment_frame.pack_propagate(False)
            
            # Payment method selection - Enhanced
            payment_method_frame = ttk.LabelFrame(payment_frame, text="💰 PAYMENT METHOD", padding="10")
            payment_method_frame.pack(fill=tk.X, pady=(0, 20))
            
            self.payment_var = tk.StringVar(value="cash")
            
            # Create payment method buttons with better styling
            cash_btn = ttk.Radiobutton(
                payment_method_frame, 
                text="💵 CASH", 
                variable=self.payment_var, 
                value="cash", 
                command=self.on_payment_method_change
            )
            cash_btn.pack(anchor="w", pady=8, fill=tk.X)
            
            upi_btn = ttk.Radiobutton(
                payment_method_frame, 
                text="📱 UPI", 
                variable=self.payment_var, 
                value="upi", 
                command=self.on_payment_method_change
            )
            upi_btn.pack(anchor="w", pady=8, fill=tk.X)
            
            card_btn = ttk.Radiobutton(
                payment_method_frame, 
                text="💳 CARD", 
                variable=self.payment_var, 
                value="card", 
                command=self.on_payment_method_change
            )
            card_btn.pack(anchor="w", pady=8, fill=tk.X)
            
            # Payment method status
            self.payment_status_label = ttk.Label(
                payment_method_frame,
                text="Selected: 💵 CASH",
                font=("Arial", 10),
                foreground="darkgreen"
            )
            self.payment_status_label.pack(anchor="w", pady=(10, 0))
            
            
            # Add a separator
            ttk.Separator(payment_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(15, 10))
            
            
            # Add some bottom spacing for scrolling
            bottom_spacer = ttk.Frame(main_frame, height=50)
            bottom_spacer.pack(fill=tk.X)
            
            # Store references
            self.current_selected_item = None
            self.barcode_scan_timer = None
            self.barcode_input_buffer = ""
            
            # Initialize stats
            self.refresh_stats()
            
            # Focus on barcode entry for immediate scanning
            self.barcode_entry.focus()
            
        except Exception as e:
            print(f"Error creating staff dashboard widgets: {e}")
            # Create a simple error display
            error_label = ttk.Label(self, text=f"Error loading staff dashboard: {str(e)}", font=("Arial", 12))
            error_label.pack(pady=50)
    
    def bind_mousewheel(self):
        """Bind mousewheel scrolling to canvas"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def on_payment_method_change(self):
        """Handle payment method selection change"""
        try:
            payment_method = self.payment_var.get()
            payment_names = {
                "cash": "💵 CASH",
                "upi": "📱 UPI", 
                "card": "💳 CARD"
            }
            
            payment_name = payment_names.get(payment_method, "💵 CASH")
            self.payment_status_label.config(
                text=f"Selected: {payment_name}",
                foreground="darkgreen"
            )
        except Exception as e:
            print(f"Error updating payment method status: {e}")
    
    def go_back_to_main(self):
        """Go back to main selection window"""
        try:
            # Use the main app reference if available
            if hasattr(self, 'main_app') and self.main_app:
                self.main_app.show_main_selection()
            else:
                # Fallback: get the root window and clear it
                root = self.winfo_toplevel()
                for widget in root.winfo_children():
                    widget.destroy()
                
                # Import and show main selection
                from main import DropBillingApp
                app = DropBillingApp()
                app.show_main_selection()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to go back to main: {str(e)}")
    
    def increase_quantity(self):
        """Increase quantity by 1"""
        try:
            current_qty = int(self.quantity_var.get())
            self.quantity_var.set(str(current_qty + 1))
        except ValueError:
            self.quantity_var.set("1")
    
    def decrease_quantity(self):
        """Decrease quantity by 1 (minimum 1)"""
        try:
            current_qty = int(self.quantity_var.get())
            if current_qty > 1:
                self.quantity_var.set(str(current_qty - 1))
        except ValueError:
            self.quantity_var.set("1")
    
    def on_barcode_input(self, event=None):
        """Handle barcode scanner input - detect when barcode is scanned"""
        try:
            # Get current input
            current_input = self.barcode_var.get()
            
            # If input is empty, reset buffer
            if not current_input:
                self.barcode_input_buffer = ""
                self.barcode_scan_timer = None
                return
            
            # Add to buffer
            self.barcode_input_buffer = current_input
            
            # Clear any existing timer
            if self.barcode_scan_timer:
                self.after_cancel(self.barcode_scan_timer)
            
            # Set timer to detect end of barcode scan (typically 100ms after last input)
            self.barcode_scan_timer = self.after(100, self.process_barcode_scan)
            
            # Update status
            self.barcode_status_label.config(
                text=f"Scanning... ({len(current_input)} characters)", 
                foreground="orange"
            )
            
        except Exception as e:
            print(f"Error in barcode input: {e}")
    
    def process_barcode_scan(self):
        """Process the scanned barcode and add item to cart automatically"""
        try:
            if not self.barcode_input_buffer:
                return
            
            item_code = self.barcode_input_buffer.strip()
            
            # Clear the input field
            self.barcode_var.set("")
            self.barcode_input_buffer = ""
            
            # Update status
            self.barcode_status_label.config(
                text=f"Processing barcode: {item_code}", 
                foreground="blue"
            )
            
            # Search item in database
            item = self.db_manager.get_item_by_code(item_code)
            
            if item:
                # Automatically add to cart with quantity 1
                cart_item = {
                    'item_id': item['id'],
                    'item_code': item['item_code'],
                    'item_name': item['item_name'],
                    'quantity': 1,
                    'unit_price': item['price'],
                    'total_price': item['price']
                }
                
                # Check if item already in cart
                item_already_in_cart = False
                for i, existing_item in enumerate(self.cart_items):
                    if existing_item['item_id'] == item['id']:
                        # Update existing item quantity
                        self.cart_items[i]['quantity'] += 1
                        self.cart_items[i]['total_price'] = (
                            self.cart_items[i]['quantity'] * self.cart_items[i]['unit_price']
                        )
                        item_already_in_cart = True
                        break
                
                if not item_already_in_cart:
                    # Add new item to cart
                    self.cart_items.append(cart_item)
                
                # Update cart display
                self.update_cart_display()
                
                # Update status
                self.barcode_status_label.config(
                    text=f"✅ Added: {item['item_name']} (₹{item['price']:.2f})", 
                    foreground="green"
                )
                
                # Reset status after 3 seconds
                self.after(3000, lambda: self.barcode_status_label.config(
                    text="Ready to scan barcode...", 
                    foreground="gray"
                ))
                
                # Focus back to barcode entry for next scan
                self.barcode_entry.focus()
                
            else:
                # Item not found
                self.barcode_status_label.config(
                    text=f"❌ Item not found: {item_code}", 
                    foreground="red"
                )
                
                # Reset status after 3 seconds
                self.after(3000, lambda: self.barcode_status_label.config(
                    text="Ready to scan barcode...", 
                    foreground="gray"
                ))
                
                # Focus back to barcode entry
                self.barcode_entry.focus()
        
        except Exception as e:
            print(f"Error processing barcode scan: {e}")
            self.barcode_status_label.config(
                text=f"Error: {str(e)}", 
                foreground="red"
            )
            # Focus back to barcode entry
            self.barcode_entry.focus()
    
    def manual_add_barcode_item(self):
        """Manually add item from barcode input field"""
        try:
            item_code = self.barcode_var.get().strip()
            if not item_code:
                messagebox.showerror("Error", "Please enter an item code")
                return
            
            # Clear the input field
            self.barcode_var.set("")
            self.barcode_input_buffer = ""
            
            # Update status
            self.barcode_status_label.config(
                text=f"Processing: {item_code}", 
                foreground="blue"
            )
            
            # Search item in database
            item = self.db_manager.get_item_by_code(item_code)
            
            if item:
                # Automatically add to cart with quantity 1
                cart_item = {
                    'item_id': item['id'],
                    'item_code': item['item_code'],
                    'item_name': item['item_name'],
                    'quantity': 1,
                    'unit_price': item['price'],
                    'total_price': item['price']
                }
                
                # Check if item already in cart
                item_already_in_cart = False
                for i, existing_item in enumerate(self.cart_items):
                    if existing_item['item_id'] == item['id']:
                        # Update existing item quantity
                        self.cart_items[i]['quantity'] += 1
                        self.cart_items[i]['total_price'] = (
                            self.cart_items[i]['quantity'] * self.cart_items[i]['unit_price']
                        )
                        item_already_in_cart = True
                        break
                
                if not item_already_in_cart:
                    # Add new item to cart
                    self.cart_items.append(cart_item)
                
                # Update cart display
                self.update_cart_display()
                
                # Update status
                self.barcode_status_label.config(
                    text=f"✅ Added: {item['item_name']} (₹{item['price']:.2f})", 
                    foreground="green"
                )
                
                # Reset status after 3 seconds
                self.after(3000, lambda: self.barcode_status_label.config(
                    text="Ready to scan barcode...", 
                    foreground="gray"
                ))
                
                # Focus back to barcode entry for next scan
                self.barcode_entry.focus()
                
            else:
                # Item not found
                self.barcode_status_label.config(
                    text=f"❌ Item not found: {item_code}", 
                    foreground="red"
                )
                
                # Reset status after 3 seconds
                self.after(3000, lambda: self.barcode_status_label.config(
                    text="Ready to scan barcode...", 
                    foreground="gray"
                ))
                
                # Focus back to barcode entry
                self.barcode_entry.focus()
        
        except Exception as e:
            print(f"Error in manual barcode add: {e}")
            self.barcode_status_label.config(
                text=f"Error: {str(e)}", 
                foreground="red"
            )
            # Focus back to barcode entry
            self.barcode_entry.focus()
    
    def search_item(self, event=None):
        """Search for item by code"""
        try:
            item_code = self.search_var.get().strip()
            if not item_code:
                messagebox.showerror("Error", "Please enter item code")
                return
            
            # Search item in database
            item = self.db_manager.get_item_by_code(item_code)
            
            if item:
                self.current_selected_item = item
                self.item_info_label.config(
                    text=f"Name: {item['item_name']}\nPrice: ₹{item['price']:.2f}"
                )
                self.add_to_cart_button.config(state=tk.NORMAL)
                self.quantity_entry.focus()
            else:
                self.item_info_label.config(text="Item not found")
                self.add_to_cart_button.config(state=tk.DISABLED)
                self.current_selected_item = None
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search item: {str(e)}")
    
    def add_to_cart(self):
        """Add item to cart"""
        try:
            if not self.current_selected_item:
                messagebox.showerror("Error", "No item selected")
                return
            
            # Get quantity
            try:
                quantity = int(self.quantity_var.get())
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity")
                return
            
            # Check if item already in cart
            for i, cart_item in enumerate(self.cart_items):
                if cart_item['item_id'] == self.current_selected_item['id']:
                    # Update existing item quantity
                    self.cart_items[i]['quantity'] += quantity
                    self.cart_items[i]['total_price'] = (
                        self.cart_items[i]['quantity'] * self.cart_items[i]['unit_price']
                    )
                    break
            else:
                # Add new item to cart
                cart_item = {
                    'item_id': self.current_selected_item['id'],
                    'item_code': self.current_selected_item['item_code'],
                    'item_name': self.current_selected_item['item_name'],
                    'quantity': quantity,
                    'unit_price': self.current_selected_item['price'],
                    'total_price': quantity * self.current_selected_item['price']
                }
                self.cart_items.append(cart_item)
            
            # Update cart display
            self.update_cart_display()
            
            # Store item name for success message
            item_name = self.current_selected_item['item_name']
            
            # Clear search
            self.search_var.set("")
            self.quantity_var.set("1")
            self.item_info_label.config(text="Enter item code to search")
            self.add_to_cart_button.config(state=tk.DISABLED)
            self.current_selected_item = None
            
            # Focus back to search
            self.search_entry.focus()
            
            # Show success message
            messagebox.showinfo("Item Added", f"Added {quantity} x {item_name} to cart")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item to cart: {str(e)}")
    
    def update_cart_display(self):
        """Update cart display and total"""
        try:
            # Clear existing items
            for item in self.cart_tree.get_children():
                self.cart_tree.delete(item)
            
            # Add cart items
            total_amount = 0
            for item in self.cart_items:
                self.cart_tree.insert("", "end", values=(
                    item['item_name'],
                    item['item_code'],
                    item['quantity'],
                    f"₹{item['unit_price']:.2f}",
                    f"₹{item['total_price']:.2f}"
                ))
                total_amount += item['total_price']
            
            # Update total
            self.total_label.config(text=f"₹{total_amount:.2f}")
            
            # Enable/disable bill button and update summary
            if self.cart_items:
                self.bill_button.config(state=tk.NORMAL)
                item_count = len(self.cart_items)
                total_qty = sum(item['quantity'] for item in self.cart_items)
                self.bill_summary_label.config(
                    text=f"📦 {item_count} item(s) | 🔢 {total_qty} qty | 💰 ₹{total_amount:.2f}",
                    foreground="darkgreen"
                )
            else:
                self.bill_button.config(state=tk.DISABLED)
                self.bill_summary_label.config(text="Cart is empty", foreground="gray")
        
        except Exception as e:
            print(f"Error updating cart display: {e}")
    
    def on_cart_item_select(self, event):
        """Handle cart item selection"""
        selection = self.cart_tree.selection()
        if selection:
            self.remove_item_button.config(state=tk.NORMAL)
        else:
            self.remove_item_button.config(state=tk.DISABLED)
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        try:
            selection = self.cart_tree.selection()
            if not selection:
                return
            
            # Get selected item index
            selected_index = self.cart_tree.index(selection[0])
            
            # Remove from cart
            if 0 <= selected_index < len(self.cart_items):
                self.cart_items.pop(selected_index)
                self.update_cart_display()
                self.remove_item_button.config(state=tk.DISABLED)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove item: {str(e)}")
    
    def clear_cart(self):
        """Clear all items from cart"""
        if messagebox.askyesno("Clear Cart", "Are you sure you want to clear all items from cart?"):
            self.cart_items = []
            self.update_cart_display()
            self.remove_item_button.config(state=tk.DISABLED)
            # Reset barcode status
            self.barcode_status_label.config(
                text="Ready to scan barcode...", 
                foreground="gray"
            )
            # Focus back to barcode entry
            self.barcode_entry.focus()
    
    def generate_bill(self):
        """Generate bill for cart items - automatically save and print"""
        try:
            if not self.cart_items:
                messagebox.showerror("Error", "Cart is empty")
                return
            
            # Get payment method
            payment_method = self.payment_var.get()
            
            # Calculate totals
            total_amount = sum(item['total_price'] for item in self.cart_items)
            total_items = len(self.cart_items)
            total_quantity = sum(item['quantity'] for item in self.cart_items)
            
            # Show processing message (brief)
            payment_icons = {"cash": "💵", "upi": "📱", "card": "💳"}
            payment_icon = payment_icons.get(payment_method, "💰")
            
            # Update status immediately
            self.barcode_status_label.config(
                text=f"Generating bill... ₹{total_amount:.2f}", 
                foreground="blue"
            )
            
            # Generate bill number
            bill_number = self.db_manager.get_next_bill_number()
            
            # Prepare bill items for database
            bill_items = []
            for item in self.cart_items:
                bill_items.append({
                    'item_id': item['item_id'],
                    'quantity': item['quantity'],
                    'unit_price': item['unit_price'],
                    'total_price': item['total_price']
                })
            
            # Create bill in database
            print(f"Saving bill to database: {bill_number}")
            if self.db_manager.create_bill(
                bill_number, bill_items, total_amount, payment_method, self.current_user['username']
            ):
                print(f"Bill {bill_number} saved to database successfully")
                # Generate and show bill
                bill_details = self.db_manager.get_bill_details(
                    self.db_manager.get_bills_by_date_range(
                        datetime.now().strftime('%Y-%m-%d'),
                        datetime.now().strftime('%Y-%m-%d')
                    )[-1]['id']  # Get the latest bill
                )
                
                if bill_details:
                    # Generate bill PDF
                    pdf_path = self.bill_generator.generate_bill_pdf(bill_details)
                    
                    if pdf_path:
                        # Clear cart first (without confirmation)
                        self.cart_items = []
                        self.update_cart_display()
                        self.remove_item_button.config(state=tk.DISABLED)
                        
                        # Reset barcode status
                        self.barcode_status_label.config(
                            text="Ready to scan barcode...", 
                            foreground="gray"
                        )
                        
                        # Automatically print and open the bill
                        self.print_and_open_bill(pdf_path, bill_number, total_amount, payment_method, payment_icon)
                        
                        # Refresh stats after bill generation
                        self.refresh_stats()
                        
                        # Focus back to barcode entry for next transaction
                        self.barcode_entry.focus()
                    else:
                        messagebox.showerror("Error", "Bill generated but PDF creation failed")
                else:
                    messagebox.showerror("Error", "Failed to retrieve bill details")
            else:
                messagebox.showerror("Error", "Failed to create bill in database")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")
    
    def print_and_open_bill(self, pdf_path, bill_number, total_amount, payment_method, payment_icon):
        """Automatically open bill for printing and show success message"""
        try:
            import subprocess
            import platform
            import os
            
            print(f"Auto-opening bill: {pdf_path}")
            
            # Check if file exists
            if not os.path.exists(pdf_path):
                messagebox.showerror("Print Error", "Bill file not found!")
                return
            
            # Get the operating system
            system = platform.system()
            
            # Always open the PDF for printing/viewing
            if system == "Windows":
                try:
                    # Open PDF with default application for printing
                    subprocess.run(['start', '/min', pdf_path], shell=True, check=True)
                    
                    # Show success message
                    messagebox.showinfo("Bill Generated Successfully", f"""
✅ BILL GENERATED & SAVED TO DATABASE!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully
📄 File: {os.path.basename(pdf_path)}

The bill has been opened for printing.
                    """)
                    
                except subprocess.CalledProcessError:
                    # Fallback: open with default PDF viewer
                    import webbrowser
                    webbrowser.open(pdf_path)
                    messagebox.showinfo("Bill Generated Successfully", f"""
✅ BILL GENERATED & SAVED TO DATABASE!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully
📄 PDF: Opened in viewer

File: {os.path.basename(pdf_path)}
                    """)
                    
            elif system == "Darwin":  # macOS
                subprocess.run(['open', pdf_path], check=True)
                messagebox.showinfo("Bill Generated Successfully", f"""
✅ BILL GENERATED & SAVED TO DATABASE!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully
📄 File: {os.path.basename(pdf_path)}

The bill has been opened for printing.
                """)
                
            elif system == "Linux":
                subprocess.run(['xdg-open', pdf_path], check=True)
                messagebox.showinfo("Bill Generated Successfully", f"""
✅ BILL GENERATED & SAVED TO DATABASE!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully
📄 File: {os.path.basename(pdf_path)}

The bill has been opened for printing.
                """)
                
            else:
                # Fallback for other systems
                import webbrowser
                webbrowser.open(pdf_path)
                messagebox.showinfo("Bill Generated Successfully", f"""
✅ BILL GENERATED & SAVED TO DATABASE!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully
📄 PDF: Opened in viewer

File: {os.path.basename(pdf_path)}
                """)
                
        except Exception as e:
            print(f"Auto-open error: {e}")
            # Fallback: open PDF viewer
            try:
                import webbrowser
                webbrowser.open(pdf_path)
                messagebox.showinfo("Bill Generated Successfully", f"""
✅ BILL GENERATED & SAVED TO DATABASE!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully
📄 PDF: Opened in viewer

File: {os.path.basename(pdf_path)}
                """)
            except Exception as fallback_error:
                messagebox.showinfo("Bill Generated Successfully", f"""
✅ BILL GENERATED & SAVED TO DATABASE!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully

File: {os.path.basename(pdf_path)}
                """)

    def print_bill_automatically(self, pdf_path, bill_number, total_amount, payment_method, payment_icon):
        """Automatically print bill to connected printer"""
        try:
            import subprocess
            import platform
            import os
            
            print(f"Auto-printing bill: {pdf_path}")
            
            # Check if file exists
            if not os.path.exists(pdf_path):
                messagebox.showerror("Print Error", "Bill file not found!")
                return
            
            # Get the operating system
            system = platform.system()
            
            if system == "Windows":
                # Windows - try to print directly
                try:
                    # Try to print using Windows print command
                    subprocess.run(['powershell', '-Command', f'Start-Process -FilePath "{pdf_path}" -Verb Print'], check=True)
                    
                    # Show success message
                    messagebox.showinfo("Bill Generated & Printed", f"""
✅ BILL GENERATED & PRINTED SUCCESSFULLY!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully
🖨️ Printer: Bill sent to connected printer
📄 File: {os.path.basename(pdf_path)}
                    """)
                    
                except subprocess.CalledProcessError:
                    # Fallback: open with default PDF viewer
                    import webbrowser
                    webbrowser.open(pdf_path)
                    messagebox.showinfo("Bill Generated", f"""
✅ BILL GENERATED & SAVED TO DATABASE!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully
📄 PDF: Opened in viewer (please print manually)

File: {os.path.basename(pdf_path)}
                    """)
                    
            elif system == "Darwin":  # macOS
                subprocess.run(['lpr', pdf_path], check=True)
                messagebox.showinfo("Bill Generated & Printed", f"""
✅ BILL GENERATED & PRINTED SUCCESSFULLY!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully
🖨️ Printer: Bill sent to connected printer
📄 File: {os.path.basename(pdf_path)}
                """)
                
            elif system == "Linux":
                subprocess.run(['lp', pdf_path], check=True)
                messagebox.showinfo("Bill Generated & Printed", f"""
✅ BILL GENERATED & PRINTED SUCCESSFULLY!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully
🖨️ Printer: Bill sent to connected printer
📄 File: {os.path.basename(pdf_path)}
                """)
                
            else:
                # Fallback for other systems
                import webbrowser
                webbrowser.open(pdf_path)
                messagebox.showinfo("Bill Generated", f"""
✅ BILL GENERATED & SAVED TO DATABASE!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully
📄 PDF: Opened in viewer (please print manually)

File: {os.path.basename(pdf_path)}
                """)
                
        except Exception as e:
            print(f"Auto-print error: {e}")
            # Fallback: open PDF viewer
            try:
                import webbrowser
                webbrowser.open(pdf_path)
                messagebox.showwarning("Bill Generated", f"""
✅ BILL GENERATED & SAVED TO DATABASE!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully
📄 PDF: Opened in viewer (please print manually)

Print Error: {str(e)}
                """)
            except Exception as fallback_error:
                messagebox.showerror("Bill Generated", f"""
✅ BILL GENERATED & SAVED TO DATABASE!

🧾 Bill Number: {bill_number}
💰 Amount: ₹{total_amount:.2f}
{payment_icon} Payment: {payment_method.upper()}
💾 Database: Bill saved successfully

Print Error: {str(e)}
                """)
    
    def refresh_stats(self):
        """Refresh today's statistics"""
        try:
            # Get today's bills
            today = datetime.now().strftime('%Y-%m-%d')
            bills = self.db_manager.get_bills_by_date_range(today, today)
            
            # Calculate stats
            total_bills = len(bills)
            total_amount = sum(bill['total_amount'] for bill in bills)
            total_items = 0
            payment_counts = {'cash': 0, 'upi': 0, 'card': 0}
            
            for bill in bills:
                bill_details = self.db_manager.get_bill_details(bill['id'])
                if bill_details:
                    total_items += len(bill_details['items'])
                    payment_method = bill.get('payment_method', 'cash').lower()
                    if payment_method in payment_counts:
                        payment_counts[payment_method] += 1
            
            # Update labels
            self.today_bills_label.config(text=f"Bills Today: {total_bills}")
            self.today_amount_label.config(text=f"Amount Today: ₹{total_amount:.2f}")
            self.today_items_label.config(text=f"Items Sold: {total_items}")
            
            # Update payment counts
            self.cash_count_label.config(text=f"💵 Cash: {payment_counts['cash']}")
            self.upi_count_label.config(text=f"📱 UPI: {payment_counts['upi']}")
            self.card_count_label.config(text=f"💳 Card: {payment_counts['card']}")
            
            # Update recent transactions
            self.update_recent_transactions()
            
        except Exception as e:
            print(f"Error refreshing stats: {e}")
    
    def update_recent_transactions(self):
        """Update recent transactions list"""
        try:
            # Clear existing items
            for item in self.recent_tree.get_children():
                self.recent_tree.delete(item)
            
            # Get recent bills (last 10)
            today = datetime.now().strftime('%Y-%m-%d')
            bills = self.db_manager.get_bills_by_date_range(today, today)
            
            # Sort by creation time (most recent first)
            bills.sort(key=lambda x: x['created_at'], reverse=True)
            
            # Add recent transactions (limit to 10)
            for bill in bills[:10]:
                # Show date and time to match system time exactly
                bill_datetime = datetime.strptime(bill['created_at'], '%Y-%m-%d %H:%M:%S')
                time_str = bill_datetime.strftime('%d/%m %H:%M')
                amount = f"₹{bill['total_amount']:.0f}"
                
                # Get item count
                bill_details = self.db_manager.get_bill_details(bill['id'])
                item_count = len(bill_details['items']) if bill_details else 0
                items_str = f"{item_count} items"
                
                self.recent_tree.insert("", "end", values=(time_str, amount, items_str))
                
        except Exception as e:
            print(f"Error updating recent transactions: {e}")
    
    def view_all_bills(self):
        """Open billing history window"""
        try:
            from src.ui.billing_history import BillingHistoryWindow
            
            history_window = tk.Toplevel(self.winfo_toplevel())
            history_window.title("Billing History")
            history_window.geometry("1000x600")
            
            # Center the window
            history_window.update_idletasks()
            x = (history_window.winfo_screenwidth() // 2) - (500)
            y = (history_window.winfo_screenheight() // 2) - (300)
            history_window.geometry(f"1000x600+{x}+{y}")
            
            billing_history = BillingHistoryWindow(history_window, self.db_manager, self.config)
            billing_history.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open billing history: {str(e)}")
