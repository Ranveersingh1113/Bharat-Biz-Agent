import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from models import Invoice, InvoiceLineItem, InvoiceType, PaymentStatus
from config import settings
import uuid
import os

logger = logging.getLogger(__name__)

class InvoiceService:
    """Service for generating GST-compliant invoices"""
    
    def __init__(self):
        self.business_name = settings.business_name
        self.business_address = settings.business_address
        self.business_phone = settings.business_phone
        self.gst_number = settings.gst_number
        self.state_code = settings.business_state_code
        self.invoice_counter = 1000  # Will be loaded from DB
    
    def generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        date_str = datetime.now().strftime("%Y%m%d")
        self.invoice_counter += 1
        return f"KT/{date_str}/{self.invoice_counter}"
    
    def calculate_gst(self, taxable_amount: float, gst_rate: float, is_inter_state: bool = False) -> Dict[str, float]:
        """Calculate GST (CGST + SGST for intra-state, IGST for inter-state)"""
        if is_inter_state:
            igst = round(taxable_amount * gst_rate / 100, 2)
            return {"cgst": 0, "sgst": 0, "igst": igst}
        else:
            half_rate = gst_rate / 2
            cgst = round(taxable_amount * half_rate / 100, 2)
            sgst = round(taxable_amount * half_rate / 100, 2)
            return {"cgst": cgst, "sgst": sgst, "igst": 0}
    
    def get_hsn_code(self, fabric_type: str) -> str:
        """Get HSN code for fabric type"""
        hsn_map = {
            "silk": "5007",
            "cotton": "5208",
            "polyester": "5407",
            "synthetic": "5407",
            "wool": "5111",
            "linen": "5309"
        }
        return hsn_map.get(fabric_type.lower(), "5007")
    
    def create_invoice(
        self,
        customer_id: str,
        customer_name: str,
        customer_phone: str,
        items: List[Dict[str, Any]],
        invoice_type: InvoiceType = InvoiceType.PUCCA,
        customer_gst: Optional[str] = None,
        customer_address: Optional[str] = None,
        is_inter_state: bool = False,
        place_of_supply: str = "Delhi"
    ) -> Invoice:
        """Create a new invoice with line items and GST calculations"""
        
        invoice_number = self.generate_invoice_number()
        line_items = []
        subtotal = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0
        
        for item in items:
            quantity = item.get("quantity", 1)
            rate = item.get("rate", 0)
            gst_rate = item.get("gst_rate", 5.0)  # Default 5% for textiles
            
            taxable_amount = round(quantity * rate, 2)
            gst = self.calculate_gst(taxable_amount, gst_rate, is_inter_state)
            
            line_item = InvoiceLineItem(
                item_id=item.get("item_id", str(uuid.uuid4())),
                name=item.get("name", "Fabric"),
                fabric_type=item.get("fabric_type", "cotton"),
                color=item.get("color", "white"),
                width=item.get("width", 44),
                hsn_code=self.get_hsn_code(item.get("fabric_type", "cotton")),
                quantity=quantity,
                unit=item.get("unit", "meter"),
                rate=rate,
                gst_rate=gst_rate,
                taxable_amount=taxable_amount,
                cgst_amount=gst["cgst"],
                sgst_amount=gst["sgst"],
                igst_amount=gst["igst"],
                total_amount=round(taxable_amount + gst["cgst"] + gst["sgst"] + gst["igst"], 2)
            )
            
            line_items.append(line_item)
            subtotal += taxable_amount
            total_cgst += gst["cgst"]
            total_sgst += gst["sgst"]
            total_igst += gst["igst"]
        
        grand_total = round(subtotal + total_cgst + total_sgst + total_igst, 2)
        
        invoice = Invoice(
            invoice_number=invoice_number,
            invoice_type=invoice_type,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_gst=customer_gst,
            customer_address=customer_address,
            items=line_items,
            subtotal=round(subtotal, 2),
            total_cgst=round(total_cgst, 2),
            total_sgst=round(total_sgst, 2),
            total_igst=round(total_igst, 2),
            grand_total=grand_total,
            balance_due=grand_total,
            is_inter_state=is_inter_state,
            place_of_supply=place_of_supply,
            due_date=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        return invoice
    
    def generate_invoice_html(self, invoice: Invoice) -> str:
        """Generate HTML for invoice PDF"""
        
        items_html = ""
        for idx, item in enumerate(invoice.items, 1):
            items_html += f"""
            <tr>
                <td>{idx}</td>
                <td>{item.name}<br><small>{item.color} {item.fabric_type} {item.width}"</small></td>
                <td>{item.hsn_code}</td>
                <td>{item.quantity} {item.unit}</td>
                <td>₹{item.rate:.2f}</td>
                <td>₹{item.taxable_amount:.2f}</td>
                <td>{item.gst_rate}%</td>
                <td>₹{item.cgst_amount:.2f}</td>
                <td>₹{item.sgst_amount:.2f}</td>
                <td>₹{item.total_amount:.2f}</td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; font-size: 12px; }}
                .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; }}
                .header h1 {{ margin: 0; color: #8B4513; }}
                .gst-info {{ font-size: 11px; color: #666; }}
                .invoice-info {{ display: flex; justify-content: space-between; margin: 20px 0; }}
                .customer-info, .invoice-details {{ width: 48%; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #8B4513; color: white; }}
                .totals {{ float: right; width: 300px; }}
                .totals table {{ border: none; }}
                .totals td {{ border: none; padding: 5px; }}
                .grand-total {{ font-weight: bold; font-size: 14px; background-color: #f0f0f0; }}
                .footer {{ margin-top: 40px; text-align: center; font-size: 10px; color: #666; }}
                .invoice-type {{ background-color: {'#4CAF50' if invoice.invoice_type == InvoiceType.PUCCA else '#FF9800'}; 
                                 color: white; padding: 5px 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{self.business_name}</h1>
                <p>{self.business_address}</p>
                <p class="gst-info">GSTIN: {self.gst_number} | Phone: {self.business_phone}</p>
            </div>
            
            <div class="invoice-info">
                <div class="customer-info">
                    <h3>Bill To:</h3>
                    <p><strong>{invoice.customer_name}</strong></p>
                    <p>{invoice.customer_address or 'N/A'}</p>
                    <p>Phone: {invoice.customer_phone}</p>
                    {'<p>GSTIN: ' + invoice.customer_gst + '</p>' if invoice.customer_gst else ''}
                </div>
                <div class="invoice-details">
                    <p><span class="invoice-type">{'GST Invoice' if invoice.invoice_type == InvoiceType.PUCCA else 'Kacha Bill'}</span></p>
                    <p><strong>Invoice No:</strong> {invoice.invoice_number}</p>
                    <p><strong>Date:</strong> {invoice.created_at.strftime('%d-%m-%Y')}</p>
                    <p><strong>Due Date:</strong> {invoice.due_date.strftime('%d-%m-%Y') if invoice.due_date else 'N/A'}</p>
                    <p><strong>Place of Supply:</strong> {invoice.place_of_supply}</p>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Description</th>
                        <th>HSN</th>
                        <th>Qty</th>
                        <th>Rate</th>
                        <th>Taxable</th>
                        <th>GST</th>
                        <th>CGST</th>
                        <th>SGST</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            
            <div class="totals">
                <table>
                    <tr><td>Subtotal:</td><td align="right">₹{invoice.subtotal:.2f}</td></tr>
                    <tr><td>CGST:</td><td align="right">₹{invoice.total_cgst:.2f}</td></tr>
                    <tr><td>SGST:</td><td align="right">₹{invoice.total_sgst:.2f}</td></tr>
                    {'<tr><td>IGST:</td><td align="right">₹' + f'{invoice.total_igst:.2f}' + '</td></tr>' if invoice.total_igst > 0 else ''}
                    <tr class="grand-total"><td>Grand Total:</td><td align="right">₹{invoice.grand_total:.2f}</td></tr>
                </table>
            </div>
            
            <div style="clear: both;"></div>
            
            <div class="footer">
                <p>Thank you for your business! | This is a computer-generated invoice.</p>
                <p>Terms: Payment due within 30 days | E&OE</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def format_invoice_text(self, invoice: Invoice) -> str:
        """Format invoice as WhatsApp-friendly text message"""
        
        items_text = ""
        for idx, item in enumerate(invoice.items, 1):
            items_text += f"{idx}. {item.name} ({item.color} {item.fabric_type})\n"
            items_text += f"   {item.quantity} {item.unit} @ ₹{item.rate:.0f} = ₹{item.total_amount:.0f}\n"
        
        text = f"""
🧵 *{self.business_name}*
{'=' * 30}

📄 *Invoice: {invoice.invoice_number}*
📅 Date: {invoice.created_at.strftime('%d-%m-%Y')}

👤 *Customer:* {invoice.customer_name}
📞 Phone: {invoice.customer_phone}

*Items:*
{items_text}
{'=' * 30}
💰 Subtotal: ₹{invoice.subtotal:.0f}
🏛️ GST (CGST+SGST): ₹{(invoice.total_cgst + invoice.total_sgst):.0f}
{'=' * 30}
💵 *GRAND TOTAL: ₹{invoice.grand_total:.0f}*

✅ Payment Status: {invoice.payment_status.value.upper()}
"""
        return text.strip()

invoice_service = InvoiceService()
