import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from models import UdhaarTransaction, PaymentStatus, PaymentMethod, HITLRequest
import uuid

logger = logging.getLogger(__name__)

class UdhaarService:
    """Service for Udhaar (credit) management with HITL safety"""
    
    def __init__(self, db=None):
        self.db = db
        self.large_credit_threshold = 10000  # Requires approval above this
        self.overdue_days = 30
    
    def set_db(self, db):
        self.db = db
    
    async def get_customer_credit(self, customer_id: str) -> Dict[str, Any]:
        """Get customer's credit status"""
        if self.db is None:
            return {"error": "Database not connected"}
        
        customer = await self.db.customers.find_one({"id": customer_id}, {"_id": 0})
        if not customer:
            return {"error": "Customer not found"}
        
        # Get recent transactions
        transactions = await self.db.udhaar_transactions.find(
            {"customer_id": customer_id}
        ).sort("created_at", -1).limit(10).to_list(10)
        
        # Get overdue invoices
        overdue_date = datetime.now(timezone.utc) - timedelta(days=self.overdue_days)
        overdue_invoices = await self.db.invoices.find({
            "customer_id": customer_id,
            "payment_status": {"$in": ["pending", "partial"]},
            "created_at": {"$lt": overdue_date.isoformat()}
        }, {"_id": 0}).to_list(100)
        
        return {
            "customer": customer,
            "total_credit": customer.get("total_credit", 0),
            "credit_limit": customer.get("credit_limit", 50000),
            "available_credit": customer.get("credit_limit", 50000) - customer.get("total_credit", 0),
            "recent_transactions": transactions,
            "overdue_invoices": overdue_invoices,
            "overdue_amount": sum(inv.get("balance_due", 0) for inv in overdue_invoices)
        }
    
    async def add_credit(
        self,
        customer_id: str,
        amount: float,
        invoice_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add credit (Udhaar) for a customer - may require HITL approval"""
        if self.db is None:
            return {"success": False, "error": "Database not connected"}
        
        customer = await self.db.customers.find_one({"id": customer_id}, {"_id": 0})
        if not customer:
            return {"success": False, "error": "Customer not found"}
        
        current_credit = customer.get("total_credit", 0)
        credit_limit = customer.get("credit_limit", 50000)
        new_balance = current_credit + amount
        
        # Check if HITL approval is needed
        requires_approval = (
            amount > self.large_credit_threshold or
            new_balance > credit_limit
        )
        
        if requires_approval:
            # Create HITL request
            hitl_request = HITLRequest(
                request_type="large_credit",
                customer_id=customer_id,
                customer_name=customer.get("name", "Unknown"),
                amount=amount,
                details={
                    "current_credit": current_credit,
                    "credit_limit": credit_limit,
                    "new_balance": new_balance,
                    "invoice_id": invoice_id,
                    "notes": notes
                }
            )
            
            await self.db.hitl_requests.insert_one(hitl_request.model_dump())
            
            return {
                "success": False,
                "requires_approval": True,
                "hitl_request_id": hitl_request.id,
                "message": f"Credit of ₹{amount} requires owner approval. Current balance: ₹{current_credit}, Limit: ₹{credit_limit}"
            }
        
        # Process credit directly
        transaction = UdhaarTransaction(
            customer_id=customer_id,
            customer_name=customer.get("name", "Unknown"),
            invoice_id=invoice_id,
            amount=amount,
            transaction_type="credit",
            balance_after=new_balance,
            notes=notes
        )
        
        await self.db.udhaar_transactions.insert_one(transaction.model_dump())
        
        # Update customer credit
        await self.db.customers.update_one(
            {"id": customer_id},
            {
                "$set": {
                    "total_credit": new_balance,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {
            "success": True,
            "transaction_id": transaction.id,
            "new_balance": new_balance,
            "message": f"Credit of ₹{amount} added. New balance: ₹{new_balance}"
        }
    
    async def process_payment(
        self,
        customer_id: str,
        amount: float,
        payment_method: PaymentMethod,
        invoice_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process payment received from customer"""
        if self.db is None:
            return {"success": False, "error": "Database not connected"}
        
        customer = await self.db.customers.find_one({"id": customer_id}, {"_id": 0})
        if not customer:
            return {"success": False, "error": "Customer not found"}
        
        current_credit = customer.get("total_credit", 0)
        new_balance = max(0, current_credit - amount)
        
        transaction = UdhaarTransaction(
            customer_id=customer_id,
            customer_name=customer.get("name", "Unknown"),
            invoice_id=invoice_id,
            amount=amount,
            transaction_type="payment",
            payment_method=payment_method,
            balance_after=new_balance,
            notes=notes
        )
        
        await self.db.udhaar_transactions.insert_one(transaction.model_dump())
        
        # Update customer credit
        await self.db.customers.update_one(
            {"id": customer_id},
            {
                "$set": {
                    "total_credit": new_balance,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Update invoice if specified
        if invoice_id:
            invoice = await self.db.invoices.find_one({"id": invoice_id}, {"_id": 0})
            if invoice:
                new_paid = invoice.get("amount_paid", 0) + amount
                new_due = invoice.get("grand_total", 0) - new_paid
                status = "paid" if new_due <= 0 else "partial"
                
                await self.db.invoices.update_one(
                    {"id": invoice_id},
                    {
                        "$set": {
                            "amount_paid": new_paid,
                            "balance_due": max(0, new_due),
                            "payment_status": status
                        }
                    }
                )
        
        return {
            "success": True,
            "transaction_id": transaction.id,
            "amount_received": amount,
            "new_balance": new_balance,
            "message": f"Payment of ₹{amount} received. Remaining balance: ₹{new_balance}"
        }
    
    async def get_overdue_customers(self) -> List[Dict[str, Any]]:
        """Get list of customers with overdue payments"""
        if self.db is None:
            return []
        
        overdue_date = datetime.now(timezone.utc) - timedelta(days=self.overdue_days)
        
        pipeline = [
            {
                "$match": {
                    "payment_status": {"$in": ["pending", "partial"]},
                    "created_at": {"$lt": overdue_date.isoformat()}
                }
            },
            {
                "$group": {
                    "_id": "$customer_id",
                    "customer_name": {"$first": "$customer_name"},
                    "customer_phone": {"$first": "$customer_phone"},
                    "total_overdue": {"$sum": "$balance_due"},
                    "invoice_count": {"$sum": 1},
                    "oldest_invoice": {"$min": "$created_at"}
                }
            },
            {"$sort": {"total_overdue": -1}}
        ]
        
        overdue_list = await self.db.invoices.aggregate(pipeline).to_list(100)
        return overdue_list
    
    async def create_reminder_request(
        self,
        customer_id: str,
        customer_name: str,
        overdue_amount: float
    ) -> Dict[str, Any]:
        """Create HITL request for sending payment reminder"""
        if self.db is None:
            return {"success": False, "error": "Database not connected"}
        
        hitl_request = HITLRequest(
            request_type="credit_reminder",
            customer_id=customer_id,
            customer_name=customer_name,
            amount=overdue_amount,
            details={
                "message_template": f"Namaste {customer_name} ji, aapka ₹{overdue_amount} ka payment pending hai. Kripya jaldi payment kar dijiye. Dhanyavaad!"
            }
        )
        
        await self.db.hitl_requests.insert_one(hitl_request.model_dump())
        
        return {
            "success": True,
            "hitl_request_id": hitl_request.id,
            "requires_approval": True
        }
    
    def format_credit_status(self, credit_info: Dict[str, Any]) -> str:
        """Format credit status as WhatsApp message"""
        customer = credit_info.get("customer", {})
        
        status_emoji = "✅" if credit_info.get("total_credit", 0) == 0 else "💳"
        overdue_emoji = "⚠️" if credit_info.get("overdue_amount", 0) > 0 else ""
        
        message = f"""
{status_emoji} *Udhaar Status: {customer.get('name', 'Customer')}*
{'=' * 30}

💰 *Total Pending:* ₹{credit_info.get('total_credit', 0):,.0f}
🏦 *Credit Limit:* ₹{credit_info.get('credit_limit', 0):,.0f}
✅ *Available:* ₹{credit_info.get('available_credit', 0):,.0f}
"""
        
        if credit_info.get("overdue_amount", 0) > 0:
            message += f"\n{overdue_emoji} *Overdue (30+ days):* ₹{credit_info.get('overdue_amount', 0):,.0f}"
        
        # Recent transactions
        transactions = credit_info.get("recent_transactions", [])[:5]
        if transactions:
            message += "\n\n📝 *Recent Transactions:*\n"
            for txn in transactions:
                txn_type = "⬆️" if txn.get("transaction_type") == "credit" else "⬇️"
                message += f"{txn_type} ₹{txn.get('amount', 0):,.0f} - {txn.get('transaction_type', '')}\n"
        
        return message.strip()

udhaar_service = UdhaarService()
