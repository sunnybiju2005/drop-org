#!/usr/bin/env python3
"""
Database Manager for DROP Clothing Shop Billing Application
Handles all database operations including users, items, and bills
"""

import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "drop_billing.db"):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def initialize_database(self):
        """Initialize database with all required tables"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    user_type TEXT NOT NULL CHECK (user_type IN ('admin', 'staff')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Create items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_code TEXT UNIQUE NOT NULL,
                    item_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    qr_code_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create bills table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_number TEXT UNIQUE NOT NULL,
                    total_amount REAL NOT NULL,
                    payment_method TEXT NOT NULL CHECK (payment_method IN ('cash', 'upi', 'card')),
                    staff_username TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create bill_items table (many-to-many relationship)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bill_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    FOREIGN KEY (bill_id) REFERENCES bills (id) ON DELETE CASCADE,
                    FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
                )
            ''')
            
            # Create settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create shop_info table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shop_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shop_name TEXT NOT NULL DEFAULT 'DROP',
                    tagline TEXT NOT NULL DEFAULT 'DRESS FOR LESS',
                    address TEXT NOT NULL DEFAULT 'City center, Naikkanal, Thrissur, Kerala 680001',
                    phone TEXT,
                    email TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.connection.commit()
            
            # Insert default users if not exists
            self.create_default_users()
            
            # Insert default shop info if not exists
            self.create_default_shop_info()
            
            return True
            
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            return False
    
    def create_default_users(self):
        """Create default users"""
        try:
            cursor = self.connection.cursor()
            
            # Check if any users exist
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                # Create default admin user
                admin_password = "admin"  # Default password
                password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
                
                cursor.execute('''
                    INSERT INTO users (username, password_hash, user_type)
                    VALUES (?, ?, ?)
                ''', ('admin', password_hash, 'admin'))
                
                self.connection.commit()
                print("Default admin user created with username: admin, password: admin")
            
        except sqlite3.Error as e:
            print(f"Error creating default users: {e}")
    
    def create_default_shop_info(self):
        """Create default shop information"""
        try:
            cursor = self.connection.cursor()
            
            # Check if shop info exists
            cursor.execute("SELECT id FROM shop_info LIMIT 1")
            if cursor.fetchone():
                return
            
            # Insert default shop info
            cursor.execute('''
                INSERT INTO shop_info (shop_name, tagline, address)
                VALUES (?, ?, ?)
            ''', ('DROP', 'DRESS FOR LESS', 'City center, Naikkanal, Thrissur, Kerala 680001'))
            
            self.connection.commit()
            
        except sqlite3.Error as e:
            print(f"Error creating default shop info: {e}")
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        try:
            cursor = self.connection.cursor()
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute('''
                SELECT id, username, user_type, last_login
                FROM users
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            if user:
                # Update last login
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (user['id'],))
                self.connection.commit()
                
                return dict(user)
            return None
            
        except sqlite3.Error as e:
            print(f"Authentication error: {e}")
            return None
    
    def add_item(self, item_code: str, item_name: str, price: float, qr_code_path: str = None) -> bool:
        """Add new item to inventory"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO items (item_code, item_name, price, qr_code_path)
                VALUES (?, ?, ?, ?)
            ''', (item_code, item_name, price, qr_code_path))
            
            self.connection.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Error adding item: {e}")
            return False
    
    def get_all_items(self) -> List[Dict]:
        """Get all items from inventory"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT id, item_code, item_name, price, qr_code_path, created_at
                FROM items
                ORDER BY item_name
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            print(f"Error getting items: {e}")
            return []
    
    def get_item_by_code(self, item_code: str) -> Optional[Dict]:
        """Get item by item code"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT id, item_code, item_name, price, qr_code_path
                FROM items
                WHERE item_code = ?
            ''', (item_code,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
            
        except sqlite3.Error as e:
            print(f"Error getting item by code: {e}")
            return None
    
    def update_item(self, item_id: int, item_code: str, item_name: str, price: float, qr_code_path: str = None) -> bool:
        """Update existing item"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE items
                SET item_code = ?, item_name = ?, price = ?, qr_code_path = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (item_code, item_name, price, qr_code_path, item_id))
            
            self.connection.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Error updating item: {e}")
            return False
    
    def delete_item(self, item_id: int) -> bool:
        """Delete item from inventory"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
            self.connection.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Error deleting item: {e}")
            return False
    
    def create_bill(self, bill_number: str, items: List[Dict], total_amount: float, payment_method: str, staff_username: str) -> bool:
        """Create new bill with items"""
        try:
            cursor = self.connection.cursor()
            
            # Use exact system time
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Insert bill with exact system time
            cursor.execute('''
                INSERT INTO bills (bill_number, total_amount, payment_method, staff_username, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (bill_number, total_amount, payment_method, staff_username, current_time))
            
            bill_id = cursor.lastrowid
            
            # Insert bill items
            for item in items:
                cursor.execute('''
                    INSERT INTO bill_items (bill_id, item_id, quantity, unit_price, total_price)
                    VALUES (?, ?, ?, ?, ?)
                ''', (bill_id, item['item_id'], item['quantity'], item['unit_price'], item['total_price']))
            
            self.connection.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Error creating bill: {e}")
            return False
    
    def get_bills_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get bills within date range"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT b.id, b.bill_number, b.total_amount, b.payment_method, 
                       b.staff_username, b.created_at
                FROM bills b
                WHERE DATE(b.created_at) BETWEEN ? AND ?
                ORDER BY b.created_at DESC
            ''', (start_date, end_date))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            print(f"Error getting bills by date range: {e}")
            return []
    
    def get_bill_details(self, bill_id: int) -> Optional[Dict]:
        """Get detailed bill information including items"""
        try:
            cursor = self.connection.cursor()
            
            # Get bill info
            cursor.execute('''
                SELECT b.id, b.bill_number, b.total_amount, b.payment_method,
                       b.staff_username, b.created_at
                FROM bills b
                WHERE b.id = ?
            ''', (bill_id,))
            
            bill = cursor.fetchone()
            if not bill:
                return None
            
            # Get bill items
            cursor.execute('''
                SELECT bi.quantity, bi.unit_price, bi.total_price,
                       i.item_code, i.item_name
                FROM bill_items bi
                JOIN items i ON bi.item_id = i.id
                WHERE bi.bill_id = ?
                ORDER BY i.item_name
            ''', (bill_id,))
            
            items = [dict(row) for row in cursor.fetchall()]
            
            bill_dict = dict(bill)
            bill_dict['items'] = items
            
            return bill_dict
            
        except sqlite3.Error as e:
            print(f"Error getting bill details: {e}")
            return None
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get application setting"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT setting_value FROM settings WHERE setting_key = ?', (key,))
            row = cursor.fetchone()
            return row['setting_value'] if row else None
            
        except sqlite3.Error as e:
            print(f"Error getting setting: {e}")
            return None
    
    def set_setting(self, key: str, value: str) -> bool:
        """Set application setting"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (setting_key, setting_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            
            self.connection.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Error setting setting: {e}")
            return False
    
    def get_shop_info(self) -> Dict:
        """Get shop information"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM shop_info LIMIT 1')
            row = cursor.fetchone()
            return dict(row) if row else {}
            
        except sqlite3.Error as e:
            print(f"Error getting shop info: {e}")
            return {}
    
    def update_shop_info(self, shop_name: str, tagline: str, address: str, phone: str = None, email: str = None) -> bool:
        """Update shop information"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE shop_info
                SET shop_name = ?, tagline = ?, address = ?, phone = ?, email = ?, updated_at = CURRENT_TIMESTAMP
            ''', (shop_name, tagline, address, phone, email))
            
            self.connection.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Error updating shop info: {e}")
            return False
    
    def get_next_bill_number(self) -> str:
        """Generate next bill number"""
        try:
            cursor = self.connection.cursor()
            
            # Use exact system date for consistency
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COUNT(*) as count FROM bills
                WHERE DATE(created_at) = ?
            ''', (today,))
            
            count = cursor.fetchone()['count']
            today_formatted = datetime.now().strftime('%Y%m%d')
            return f"BILL{today_formatted}{count + 1:04d}"
            
        except sqlite3.Error as e:
            print(f"Error generating bill number: {e}")
            return f"BILL{datetime.now().strftime('%Y%m%d')}0001"
    
    def clear_items(self):
        """Clear all items from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM items')
            self.connection.commit()
            print("All items cleared from database")
            return True
        except sqlite3.Error as e:
            print(f"Error clearing items: {e}")
            return False
    
    def clear_bills(self):
        """Clear all bills from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM bills')
            cursor.execute('DELETE FROM bill_items')
            self.connection.commit()
            print("All bills cleared from database")
            return True
        except sqlite3.Error as e:
            print(f"Error clearing bills: {e}")
            return False
    
    def clear_users(self):
        """Clear all users except admin"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM users WHERE username != ?', ('admin',))
            self.connection.commit()
            print("All non-admin users cleared from database")
            return True
        except sqlite3.Error as e:
            print(f"Error clearing users: {e}")
            return False
    
    def get_all_users(self):
        """Get all users from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM users')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting users: {e}")
            return []
    
    def delete_user(self, user_id):
        """Delete a specific user"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting user: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
