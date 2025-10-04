#!/usr/bin/env python3
"""
Item Management Window for DROP Clothing Shop Billing Application
Handles CRUD operations for items with barcode generation
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageTk

from src.database.database_manager import DatabaseManager
from src.config.config import Config

class ItemManagementWindow(ttk.Frame):
    def __init__(self, parent, db_manager: DatabaseManager, config: Config):
        super().__init__(parent)
        self.db_manager = db_manager
        self.config = config
        self.current_item = None
        
        self.create_widgets()
        self.load_items()
    
    def create_widgets(self):
        """Create item management widgets"""
        # Title
        title_label = ttk.Label(self, text="Item Management", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Main content frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Items list
        left_frame = ttk.LabelFrame(main_frame, text="Items List", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.search_entry.bind('<KeyRelease>', self.filter_items)
        
        # Items treeview
        columns = ("Code", "Name", "Price", "Barcode")
        self.items_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.items_tree.heading(col, text=col)
            if col == "Name":
                self.items_tree.column(col, width=200)
            else:
                self.items_tree.column(col, width=100)
        
        # Scrollbar for items
        items_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=items_scrollbar.set)
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        items_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.items_tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        # Right side - Item details form
        right_frame = ttk.LabelFrame(main_frame, text="Item Details", padding="10", width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)
        
        # Item form
        self.create_item_form(right_frame)
        
        # Barcode preview frame
        barcode_frame = ttk.LabelFrame(right_frame, text="Barcode Preview", padding="10")
        barcode_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.barcode_label = ttk.Label(barcode_frame, text="No item selected")
        self.barcode_label.pack()
        
        # Barcode buttons
        barcode_buttons_frame = ttk.Frame(barcode_frame)
        barcode_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.generate_barcode_button = ttk.Button(
            barcode_buttons_frame,
            text="Generate Barcode",
            command=self.generate_barcode,
            state=tk.DISABLED
        )
        self.generate_barcode_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.download_barcode_button = ttk.Button(
            barcode_buttons_frame,
            text="Download Barcode",
            command=self.download_barcode,
            state=tk.DISABLED
        )
        self.download_barcode_button.pack(side=tk.LEFT)
    
    def create_item_form(self, parent):
        """Create item form widgets"""
        # Item Code
        ttk.Label(parent, text="Item Code:").pack(anchor="w", pady=(0, 5))
        self.item_code_var = tk.StringVar()
        self.item_code_entry = ttk.Entry(parent, textvariable=self.item_code_var)
        self.item_code_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Item Name
        ttk.Label(parent, text="Item Name:").pack(anchor="w", pady=(0, 5))
        self.item_name_var = tk.StringVar()
        self.item_name_entry = ttk.Entry(parent, textvariable=self.item_name_var)
        self.item_name_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Price
        ttk.Label(parent, text="Price (₹):").pack(anchor="w", pady=(0, 5))
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(parent, textvariable=self.price_var)
        self.price_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X)
        
        self.add_button = ttk.Button(
            buttons_frame,
            text="Add Item",
            command=self.add_item,
            style="Accent.TButton"
        )
        self.add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.update_button = ttk.Button(
            buttons_frame,
            text="Update",
            command=self.update_item,
            state=tk.DISABLED
        )
        self.update_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_button = ttk.Button(
            buttons_frame,
            text="Delete",
            command=self.delete_item,
            state=tk.DISABLED
        )
        self.delete_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_button = ttk.Button(
            buttons_frame,
            text="Clear",
            command=self.clear_form
        )
        self.clear_button.pack(side=tk.LEFT)
    
    def load_items(self):
        """Load items from database"""
        try:
            # Clear existing items
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            
            # Get all items
            items = self.db_manager.get_all_items()
            
            # Add items to treeview
            for item in items:
                has_barcode = "✓" if item['qr_code_path'] else "✗"
                self.items_tree.insert("", "end", values=(
                    item['item_code'],
                    item['item_name'],
                    f"₹{item['price']:.2f}",
                    has_barcode
                ), tags=(item['id'],))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load items: {str(e)}")
    
    def filter_items(self, event=None):
        """Filter items based on search term"""
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Get all items
        items = self.db_manager.get_all_items()
        
        # Filter and add items
        for item in items:
            if (search_term in item['item_code'].lower() or 
                search_term in item['item_name'].lower()):
                has_barcode = "✓" if item['qr_code_path'] else "✗"
                self.items_tree.insert("", "end", values=(
                    item['item_code'],
                    item['item_name'],
                    f"₹{item['price']:.2f}",
                    has_barcode
                ), tags=(item['id'],))
    
    def on_item_select(self, event):
        """Handle item selection"""
        selection = self.items_tree.selection()
        if not selection:
            return
        
        # Get selected item ID
        item_id = int(self.items_tree.item(selection[0])['tags'][0])
        
        # Get item details
        items = self.db_manager.get_all_items()
        self.current_item = next((item for item in items if item['id'] == item_id), None)
        
        if self.current_item:
            self.populate_form()
            self.update_buttons_state(update=True, delete=True)
            self.generate_barcode_button.config(state=tk.NORMAL)
            
            # Show existing barcode if available
            if self.current_item['qr_code_path'] and os.path.exists(self.current_item['qr_code_path']):
                self.show_barcode(self.current_item['qr_code_path'])
                self.download_barcode_button.config(state=tk.NORMAL)
            else:
                self.barcode_label.config(text="No barcode generated")
                self.download_barcode_button.config(state=tk.DISABLED)
    
    def populate_form(self):
        """Populate form with selected item data"""
        if not self.current_item:
            return
        
        self.item_code_var.set(self.current_item['item_code'])
        self.item_name_var.set(self.current_item['item_name'])
        self.price_var.set(str(self.current_item['price']))
    
    def update_buttons_state(self, add=False, update=False, delete=False):
        """Update button states"""
        self.add_button.config(state=tk.NORMAL if add else tk.DISABLED)
        self.update_button.config(state=tk.NORMAL if update else tk.DISABLED)
        self.delete_button.config(state=tk.NORMAL if delete else tk.DISABLED)
    
    def add_item(self):
        """Add new item"""
        try:
            item_code = self.item_code_var.get().strip()
            item_name = self.item_name_var.get().strip()
            price_str = self.price_var.get().strip()
            
            # Validate input
            if not item_code or not item_name or not price_str:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            try:
                price = float(price_str)
                if price <= 0:
                    raise ValueError("Price must be positive")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid price")
                return
            
            # Check if item code already exists
            existing_item = self.db_manager.get_item_by_code(item_code)
            if existing_item:
                messagebox.showerror("Error", "Item code already exists")
                return
            
            # Add item to database
            if self.db_manager.add_item(item_code, item_name, price):
                messagebox.showinfo("Success", "Item added successfully")
                self.clear_form()
                self.load_items()
            else:
                messagebox.showerror("Error", "Failed to add item")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")
    
    def update_item(self):
        """Update selected item"""
        try:
            if not self.current_item:
                messagebox.showerror("Error", "No item selected")
                return
            
            item_code = self.item_code_var.get().strip()
            item_name = self.item_name_var.get().strip()
            price_str = self.price_var.get().strip()
            
            # Validate input
            if not item_code or not item_name or not price_str:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            try:
                price = float(price_str)
                if price <= 0:
                    raise ValueError("Price must be positive")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid price")
                return
            
            # Check if item code already exists (excluding current item)
            existing_item = self.db_manager.get_item_by_code(item_code)
            if existing_item and existing_item['id'] != self.current_item['id']:
                messagebox.showerror("Error", "Item code already exists")
                return
            
            # Update item in database
            if self.db_manager.update_item(
                self.current_item['id'], item_code, item_name, price, self.current_item['qr_code_path']
            ):
                messagebox.showinfo("Success", "Item updated successfully")
                self.load_items()
                # Update current item reference
                updated_item = self.db_manager.get_item_by_code(item_code)
                if updated_item:
                    self.current_item = updated_item
            else:
                messagebox.showerror("Error", "Failed to update item")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update item: {str(e)}")
    
    def delete_item(self):
        """Delete selected item"""
        try:
            if not self.current_item:
                messagebox.showerror("Error", "No item selected")
                return
            
            if messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete item '{self.current_item['item_name']}'?"):
                
                if self.db_manager.delete_item(self.current_item['id']):
                    messagebox.showinfo("Success", "Item deleted successfully")
                    self.clear_form()
                    self.load_items()
                else:
                    messagebox.showerror("Error", "Failed to delete item")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {str(e)}")
    
    def clear_form(self):
        """Clear form fields"""
        self.item_code_var.set("")
        self.item_name_var.set("")
        self.price_var.set("")
        self.current_item = None
        self.update_buttons_state(add=True)
        self.generate_barcode_button.config(state=tk.DISABLED)
        self.download_barcode_button.config(state=tk.DISABLED)
        self.barcode_label.config(text="No item selected")
        self.items_tree.selection_remove(self.items_tree.selection())
    
    def generate_barcode(self):
        """Generate barcode for selected item"""
        try:
            if not self.current_item:
                messagebox.showerror("Error", "No item selected")
                return
            
            # Create barcode directory if it doesn't exist
            barcode_dir = "assets/qr_codes"  # Keep same directory for compatibility
            os.makedirs(barcode_dir, exist_ok=True)
            
            # Generate Code128 barcode
            barcode_code = Code128(self.current_item['item_code'], writer=ImageWriter())
            
            # Save barcode
            barcode_filename = f"qr_{self.current_item['item_code']}.png"  # Keep same naming for compatibility
            barcode_path = os.path.join(barcode_dir, barcode_filename)
            barcode_code.save(barcode_path.replace('.png', ''))  # Save without extension, writer adds .png
            
            # The actual file will have .png extension added by the writer
            actual_barcode_path = barcode_path  # This is the correct path with .png
            
            # Update database with barcode path
            self.db_manager.update_item(
                self.current_item['id'],
                self.current_item['item_code'],
                self.current_item['item_name'],
                self.current_item['price'],
                actual_barcode_path
            )
            
            # Update current item reference
            self.current_item['qr_code_path'] = actual_barcode_path
            
            # Show barcode
            self.show_barcode(actual_barcode_path)
            self.download_barcode_button.config(state=tk.NORMAL)
            
            # Refresh items list
            self.load_items()
            
            messagebox.showinfo("Success", "Barcode generated successfully")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate barcode: {str(e)}")
    
    def show_barcode(self, barcode_path):
        """Show barcode in the preview label"""
        try:
            # Load and resize barcode image
            barcode_image = Image.open(barcode_path)
            # Resize to fit preview (barcodes are typically wider than tall)
            barcode_image = barcode_image.resize((200, 100), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            barcode_photo = ImageTk.PhotoImage(barcode_image)
            
            # Update label
            self.barcode_label.config(image=barcode_photo, text="")
            self.barcode_label.image = barcode_photo  # Keep a reference
            
        except Exception as e:
            print(f"Error showing barcode: {e}")
            self.barcode_label.config(text="Error loading barcode")
    
    def download_barcode(self):
        """Download barcode file"""
        try:
            if not self.current_item or not self.current_item['qr_code_path']:
                messagebox.showerror("Error", "No barcode available")
                return
            
            if not os.path.exists(self.current_item['qr_code_path']):
                messagebox.showerror("Error", "Barcode file not found")
                return
            
            # Open file dialog for save location
            filename = f"barcode_{self.current_item['item_code']}.png"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile=filename
            )
            
            if file_path:
                # Copy barcode file to selected location
                import shutil
                shutil.copy2(self.current_item['qr_code_path'], file_path)
                messagebox.showinfo("Success", f"Barcode saved to {file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download barcode: {str(e)}")
