#!/usr/bin/env python3
"""
Configuration Manager for DROP Clothing Shop Billing Application
Handles application settings and theme management
"""

import os
import json
from typing import Dict, Any

class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.config_data = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        default_config = {
            "theme": "light",
            "window_width": 1200,
            "window_height": 800,
            "auto_save": True,
            "printer_name": "",
            "shop_info": {
                "name": "DROP",
                "tagline": "DRESS FOR LESS",
                "address": "City center, Naikkanal, Thrissur, Kerala 680001",
                "phone": "",
                "email": ""
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with default to ensure all keys exist
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except (json.JSONDecodeError, IOError):
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config_data: Dict[str, Any] = None) -> bool:
        """Save configuration to file"""
        try:
            if config_data is None:
                config_data = self.config_data
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
            
            self.config_data = config_data
            return True
            
        except (IOError, TypeError) as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        try:
            self.config_data[key] = value
            return self.save_config()
        except Exception as e:
            print(f"Error setting config: {e}")
            return False
    
    def get_theme_colors(self) -> Dict[str, str]:
        """Get theme colors based on current theme"""
        theme = self.get("theme", "light")
        
        if theme == "dark":
            return {
                "bg_primary": "#2b2b2b",
                "bg_secondary": "#3c3c3c",
                "bg_tertiary": "#4a4a4a",
                "text_primary": "#ffffff",
                "text_secondary": "#cccccc",
                "accent": "#007acc",
                "accent_hover": "#005a9e",
                "success": "#28a745",
                "warning": "#ffc107",
                "danger": "#dc3545",
                "border": "#555555"
            }
        else:  # light theme
            return {
                "bg_primary": "#ffffff",
                "bg_secondary": "#f8f9fa",
                "bg_tertiary": "#e9ecef",
                "text_primary": "#212529",
                "text_secondary": "#6c757d",
                "accent": "#007bff",
                "accent_hover": "#0056b3",
                "success": "#28a745",
                "warning": "#ffc107",
                "danger": "#dc3545",
                "border": "#dee2e6"
            }
    
    def toggle_theme(self) -> str:
        """Toggle between light and dark theme"""
        current_theme = self.get("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"
        self.set("theme", new_theme)
        return new_theme
    
    def get_shop_info(self) -> Dict[str, str]:
        """Get shop information"""
        return self.get("shop_info", {})
    
    def set_shop_info(self, shop_info: Dict[str, str]) -> bool:
        """Set shop information"""
        return self.set("shop_info", shop_info)
