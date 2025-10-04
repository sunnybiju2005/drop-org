# DROP Clothing Shop Billing Application

A comprehensive desktop billing application for clothing shops built with Python and Tkinter.

## Features

### Admin Features
- **Login System**: Secure admin and staff authentication
- **Dashboard**: Overview with sales statistics and recent bills
- **Item Management**: Add, edit, delete items with barcode generation
- **Billing History**: View, filter, and export billing data
- **Settings**: Configure shop information and application preferences
- **Theme Support**: Light and dark mode themes
- **Data Persistence**: All data stored in SQLite database

### Staff Features
- **Barcode Scanner**: Automatic item addition to cart by scanning barcodes
- **Item Search**: Search items by code for quick billing
- **Shopping Cart**: Add multiple items with quantities
- **Payment Methods**: Support for Cash, UPI, and Card payments
- **Bill Generation**: Generate and print professional bills
- **Real-time Calculations**: Automatic total calculations

### Technical Features
- **Barcode Generation**: Generate and download barcodes for items
- **Barcode Scanning**: Support for USB barcode scanners with auto-add to cart
- **Manual Code Entry**: Type item codes manually with instant cart addition
- **PDF Bill Generation**: Professional bill format matching shop requirements
- **Instant Bill Processing**: Automatic save and print without confirmations
- **Easy Date Selection**: Calendar picker with quick date buttons
- **Data Export**: Export billing data to CSV format
- **Responsive UI**: Modern, user-friendly interface
- **Database Management**: Robust SQLite database with proper relationships

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd drop-org
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## Barcode Scanner Setup

### Hardware Requirements
- USB Barcode Scanner (keyboard wedge type)
- Generated barcodes printed and attached to items

### Scanner Configuration
Most USB barcode scanners work as "keyboard wedge" devices, meaning they input scanned data as if typed from a keyboard. No additional drivers are needed.

### Usage Instructions
1. **Connect Scanner**: Plug USB barcode scanner into computer
2. **Generate Barcodes**: Use Admin → Item Management → Generate Barcode for each item
3. **Print & Attach**: Print barcodes and attach to clothing items
4. **Scan Items**: In Staff Billing, focus is automatically on barcode input field
5. **Auto-Add**: Scanned items are automatically added to cart with quantity 1
6. **Multiple Scans**: Scanning the same item multiple times increases quantity

### Scanner Features
- **Auto-Detection**: Automatically detects when barcode scanning is complete
- **Manual Entry**: Enter item codes manually and click "Add to Cart" button
- **Real-time Status**: Shows scanning progress and item addition status
- **Error Handling**: Displays clear messages for invalid/unfound barcodes
- **Focus Management**: Automatically returns focus to scanner input after each scan

## Professional Desktop Application

This is a professional desktop application that opens with a main selection window offering two clear options: Admin Login or Staff Billing.

### Login Credentials

- **Admin Username**: `drop`
- **Admin Password**: `drop`
- **Staff Access**: No login required - direct access to billing

*Note: Please change the default admin password after first use for security.*

## Usage Guide

### First Time Setup

1. **Launch Application**: Opens with "DROP" main selection window
2. **Choose Access Type**: Click "ADMIN LOGIN" or "STAFF BILLING"
3. **Admin Setup**: Login with credentials → Configure shop info, add items, generate barcodes
4. **Staff Setup**: Direct access to billing interface - no setup needed

### Daily Operations

1. **Admin Workflow**: Admin Login → Enter credentials → Full management dashboard
2. **Staff Workflow**: Staff Billing → Direct access to sales and billing interface
3. **Item Search**: Enter item codes to add items to cart
4. **Cart Management**: Adjust quantities and remove items as needed
5. **Payment Processing**: Select payment method and generate bill
6. **Bill Printing**: Bills are automatically saved as PDF files

### Admin Features

1. **Dashboard**: Monitor daily and monthly sales
2. **Item Management**: Add new items, update prices, generate barcodes
3. **Billing History**: Check billing history and export data
4. **Settings**: Configure themes and application preferences
5. **Reports**: View and export sales reports

### Staff Features

1. **Direct Access**: No login required for immediate billing
2. **Barcode Scanning**: Connect USB barcode scanner for automatic item addition
3. **Manual Entry**: Type item codes and click "Add to Cart" for manual entry
4. **Item Search**: Quick item lookup by code (manual fallback)
5. **Cart Management**: Add/remove items and adjust quantities
6. **Payment Processing**: Support for Cash, UPI, and Card payments
7. **Instant Bill Generation**: Bills save automatically and open for printing
8. **Professional PDF Bills**: Shop-branded bills with automatic printing

## File Structure

```
drop-org/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── config.json            # Application configuration (auto-generated)
├── drop_billing.db        # SQLite database (auto-generated)
├── src/                   # Source code
│   ├── config/           # Configuration management
│   ├── database/         # Database operations
│   ├── models/           # Data models
│   ├── ui/              # User interface components
│   └── utils/           # Utility functions
└── assets/              # Generated files
    ├── bills/           # Generated bill PDFs
    └── qr_codes/        # Generated barcode images
```

## Database Schema

The application uses SQLite with the following main tables:

- **users**: Admin and staff user accounts
- **items**: Clothing items with codes, names, and prices
- **bills**: Bill records with totals and payment methods
- **bill_items**: Individual items within each bill
- **settings**: Application configuration
- **shop_info**: Shop details and contact information

## Customization

### Shop Information
- Update shop name, tagline, and address in Settings
- Customize contact details (phone, email)
- Modify bill format as needed

### Item Management
- Add custom item codes
- Set individual prices
- Generate barcodes for inventory management

### Theme Customization
- Switch between light and dark themes
- Theme settings are automatically saved

## Troubleshooting

### Common Issues

1. **Database Errors**: Delete `drop_billing.db` to reset the database
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **Permission Errors**: Ensure write permissions for the project directory
4. **PDF Generation Issues**: Check if assets/bills directory exists

### Support

For technical support or feature requests, please contact the development team.

## Security Notes

- Change default admin password immediately
- Keep the application updated
- Backup database regularly
- Use strong passwords for production environments

## License

This project is proprietary software. All rights reserved.

## Version History

- **v1.0.0**: Initial release with core billing functionality
- Complete admin and staff interfaces
- Barcode generation and management
- PDF bill generation
- Database persistence
- Theme support
