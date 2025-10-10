#!/usr/bin/env python3
"""
Bill Generator for DROP Clothing Shop Billing Application
Generates PDF bills matching the provided format
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from src.database.database_manager import DatabaseManager
from src.config.config import Config

class BillGenerator:
    def __init__(self, db_manager: DatabaseManager, config: Config):
        self.db_manager = db_manager
        self.config = config
        self.carbon_printer_mode = config.get("carbon_printer_mode", False)
    
    def generate_bill_pdf(self, bill_details: dict) -> str:
        """Generate PDF bill from bill details"""
        try:
            # Create bills directory if it doesn't exist
            bills_dir = "assets/bills"
            os.makedirs(bills_dir, exist_ok=True)
            
            # Generate PDF filename
            pdf_filename = f"bill_{bill_details['bill_number']}.pdf"
            pdf_path = os.path.join(bills_dir, pdf_filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            story = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            shop_title_style = ParagraphStyle(
                'ShopTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=6,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            shop_subtitle_style = ParagraphStyle(
                'ShopSubtitle',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=6,
                alignment=TA_CENTER,
                fontName='Helvetica-Oblique'
            )
            
            shop_address_style = ParagraphStyle(
                'ShopAddress',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=12,
                alignment=TA_CENTER,
                fontName='Helvetica'
            )
            
            bill_info_style = ParagraphStyle(
                'BillInfo',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_LEFT,
                fontName='Helvetica'
            )
            
            # Get shop info
            shop_info = self.db_manager.get_shop_info()
            shop_name = shop_info.get('shop_name', 'DROP')
            shop_tagline = shop_info.get('tagline', 'DRESS FOR LESS')
            shop_address = shop_info.get('address', 'City center, Naikkanal, Thrissur, Kerala 680001')
            
            # Add shop header
            story.append(Paragraph(shop_name.upper(), shop_title_style))
            story.append(Paragraph(shop_tagline.upper(), shop_subtitle_style))
            story.append(Paragraph(shop_address, shop_address_style))
            
            # Add date and bill number
            bill_date = datetime.strptime(bill_details['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
            
            bill_info_data = [
                [f"DATE: {bill_date}", f"BILL NO: {bill_details['bill_number']}"]
            ]
            
            bill_info_table = Table(bill_info_data, colWidths=[3*inch, 3*inch])
            bill_info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, 0), 0),
                ('RIGHTPADDING', (-1, 0), (-1, 0), 0),
            ]))
            
            story.append(bill_info_table)
            story.append(Spacer(1, 20))
            
            # Create items table
            table_data = [['PRODUCT', 'QUANTITY', 'PRICE', 'TOTAL']]
            
            for item in bill_details['items']:
                table_data.append([
                    item['item_name'],
                    str(item['quantity']),
                    f"Rs.{item['unit_price']:.2f}",
                    f"Rs.{item['total_price']:.2f}"
                ])
            
            # Add total row
            table_data.append([
                '',
                '',
                'TOTAL:',
                f"Rs.{bill_details['total_amount']:.2f}"
            ])
            
            items_table = Table(table_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
            items_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
                ('ALIGN', (0, 1), (-1, -2), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                
                # Total row
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
                ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
                ('TOPPADDING', (0, -1), (-1, -1), 12),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
            ]))
            
            story.append(items_table)
            story.append(Spacer(1, 30))
            
            # Add payment method and thank you message
            payment_style = ParagraphStyle(
                'PaymentInfo',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                alignment=TA_CENTER,
                fontName='Helvetica'
            )
            
            story.append(Paragraph(f"Payment Method: {bill_details['payment_method'].upper()}", payment_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph("Thank you for shopping with us!", payment_style))
            story.append(Paragraph("Visit again soon!", payment_style))
            
            # Build PDF
            doc.build(story)
            
            return pdf_path
            
        except Exception as e:
            print(f"Error generating bill PDF: {e}")
            return None
    
    def generate_carbon_printer_bill(self, bill_details: dict) -> str:
        """Generate carbon printer optimized bill (text format)"""
        try:
            # Create bills directory if it doesn't exist
            bills_dir = "assets/bills"
            os.makedirs(bills_dir, exist_ok=True)
            
            # Generate text filename for carbon printer
            txt_filename = f"bill_{bill_details['bill_number']}.txt"
            txt_path = os.path.join(bills_dir, txt_filename)
            
            # Get shop info
            shop_info = self.db_manager.get_shop_info()
            shop_name = shop_info.get('shop_name', 'DROP')
            shop_tagline = shop_info.get('tagline', 'DRESS FOR LESS')
            shop_address = shop_info.get('address', 'City center, Naikkanal, Thrissur, Kerala 680001')
            
            # Format date
            bill_date = datetime.strptime(bill_details['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
            
            # Create carbon printer optimized bill content
            bill_content = []
            
            # Header - centered and bold for carbon printer
            bill_content.append("=" * 50)
            bill_content.append(f"        {shop_name.upper()}")
            bill_content.append(f"      {shop_tagline.upper()}")
            bill_content.append(f"    {shop_address}")
            bill_content.append("=" * 50)
            bill_content.append("")
            
            # Bill info
            bill_content.append(f"Date: {bill_date:<20} Bill No: {bill_details['bill_number']}")
            bill_content.append("-" * 50)
            bill_content.append("")
            
            # Items table - simple format for carbon printer
            bill_content.append("ITEM NAME                QTY   PRICE    TOTAL")
            bill_content.append("-" * 50)
            
            for item in bill_details['items']:
                # Truncate long item names for carbon printer
                item_name = item['item_name'][:20] if len(item['item_name']) > 20 else item['item_name']
                bill_content.append(f"{item_name:<20} {item['quantity']:>3}  Rs.{item['unit_price']:>6.2f}  Rs.{item['total_price']:>6.2f}")
            
            bill_content.append("-" * 50)
            bill_content.append(f"{'TOTAL:':<40} Rs.{bill_details['total_amount']:>6.2f}")
            bill_content.append("")
            
            # Payment method
            bill_content.append(f"Payment Method: {bill_details['payment_method'].upper()}")
            bill_content.append("")
            bill_content.append("Thank you for shopping with us!")
            bill_content.append("Visit again soon!")
            bill_content.append("")
            bill_content.append("=" * 50)
            
            # Write to file
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(bill_content))
            
            print(f"Carbon printer bill generated: {txt_path}")
            return txt_path
            
        except Exception as e:
            print(f"Error generating carbon printer bill: {e}")
            return None
    
    def print_to_carbon_printer(self, bill_path: str, printer_name: str = None) -> bool:
        """Print bill directly to carbon printer"""
        try:
            import subprocess
            import platform
            
            print(f"Printing to carbon printer: {bill_path}")
            
            # Check if file exists
            if not os.path.exists(bill_path):
                print(f"Bill file not found: {bill_path}")
                return False
            
            system = platform.system()
            
            if system == "Windows":
                # Windows - use copy command for carbon printers
                if printer_name:
                    # Print to specific printer
                    cmd = f'copy "{bill_path}" "{printer_name}"'
                else:
                    # Print to default printer (usually LPT1 for carbon printers)
                    cmd = f'copy "{bill_path}" LPT1'
                
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("Successfully printed to carbon printer")
                    return True
                else:
                    print(f"Print error: {result.stderr}")
                    return False
                    
            elif system == "Linux":
                # Linux - use lp command
                if printer_name:
                    cmd = ['lp', '-d', printer_name, bill_path]
                else:
                    cmd = ['lp', bill_path]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("Successfully printed to carbon printer")
                    return True
                else:
                    print(f"Print error: {result.stderr}")
                    return False
                    
            elif system == "Darwin":  # macOS
                # macOS - use lpr command
                if printer_name:
                    cmd = ['lpr', '-P', printer_name, bill_path]
                else:
                    cmd = ['lpr', bill_path]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("Successfully printed to carbon printer")
                    return True
                else:
                    print(f"Print error: {result.stderr}")
                    return False
            
            else:
                print(f"Unsupported operating system: {system}")
                return False
                
        except Exception as e:
            print(f"Error printing to carbon printer: {e}")
            return False
