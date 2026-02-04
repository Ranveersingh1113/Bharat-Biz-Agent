import logging
import re
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Create invoices directory
INVOICE_DIR = Path("/app/backend/invoices")
INVOICE_DIR.mkdir(exist_ok=True)

class PDFGenerator:
    """Generate PDF invoices using WeasyPrint"""
    
    def __init__(self):
        self.invoice_dir = INVOICE_DIR
    
    def generate_pdf(self, html_content: str, filename: str) -> Optional[str]:
        """Generate PDF from HTML content"""
        try:
            from weasyprint import HTML, CSS
            
            pdf_path = self.invoice_dir / filename
            
            # Custom CSS for better PDF rendering
            css = CSS(string='''
                @page {
                    size: A4;
                    margin: 1cm;
                }
                body {
                    font-family: Arial, sans-serif;
                    font-size: 11px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 6px;
                    text-align: left;
                }
                th {
                    background-color: #8B4513;
                    color: white;
                }
            ''')
            
            HTML(string=html_content).write_pdf(str(pdf_path), stylesheets=[css])
            logger.info(f"PDF generated: {pdf_path}")
            return str(pdf_path)
            
        except ImportError:
            logger.warning("WeasyPrint not available, using HTML fallback")
            # Save as HTML if WeasyPrint not available
            html_path = self.invoice_dir / filename.replace('.pdf', '.html')
            with open(html_path, 'w') as f:
                f.write(html_content)
            return str(html_path)
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            return None

pdf_generator = PDFGenerator()
