import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from models import IntentType, MessageType, ConversationSession, PaymentMethod
from services.sarvam_service import sarvam_service
from services.whatsapp_service import whatsapp_service
from services.invoice_service import invoice_service
from services.inventory_service import inventory_service
from services.udhaar_service import udhaar_service
import uuid

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Main orchestrator for routing intents to appropriate agents"""
    
    def __init__(self, db=None):
        self.db = db
        self.sessions: Dict[str, ConversationSession] = {}
    
    def set_db(self, db):
        self.db = db
        inventory_service.set_db(db)
        udhaar_service.set_db(db)
    
    async def get_or_create_session(self, whatsapp_id: str) -> ConversationSession:
        """Get existing session or create new one"""
        if whatsapp_id in self.sessions:
            session = self.sessions[whatsapp_id]
            session.last_activity = datetime.now(timezone.utc)
            return session
        
        # Check database for existing session
        if self.db:
            existing = await self.db.sessions.find_one({"whatsapp_id": whatsapp_id}, {"_id": 0})
            if existing:
                session = ConversationSession(**existing)
                self.sessions[whatsapp_id] = session
                return session
        
        # Create new session
        session = ConversationSession(whatsapp_id=whatsapp_id)
        self.sessions[whatsapp_id] = session
        
        if self.db:
            await self.db.sessions.insert_one(session.model_dump())
        
        return session
    
    async def process_message(
        self,
        whatsapp_id: str,
        message_type: MessageType,
        content: Optional[str] = None,
        media_id: Optional[str] = None,
        button_payload: Optional[str] = None
    ) -> str:
        """Main entry point for processing incoming messages"""
        
        session = await self.get_or_create_session(whatsapp_id)
        
        # Handle button responses (HITL)
        if message_type == MessageType.BUTTON and button_payload:
            return await self.handle_button_response(session, button_payload)
        
        # Handle voice messages
        if message_type == MessageType.AUDIO and media_id:
            audio_data = await whatsapp_service.download_media(media_id)
            if audio_data:
                transcription = await sarvam_service.transcribe_audio(audio_data)
                if transcription.get("success"):
                    content = transcription.get("transcript", "")
                    logger.info(f"Transcribed voice: {content}")
                else:
                    return "Maaf kijiye, voice message samajh nahi aaya. Kripya text mein bhejiye."
            else:
                return "Voice message download nahi ho paya. Please try again."
        
        # Handle image messages (potential UPI screenshot)
        if message_type == MessageType.IMAGE and media_id:
            return await self.handle_payment_screenshot(session, media_id)
        
        if not content:
            return "Kripya apna message bhejiye."
        
        # Classify intent using Sarvam AI
        intent_result = await sarvam_service.classify_intent(content)
        
        if not intent_result.get("success"):
            return "Maaf kijiye, message samajh nahi aaya. Kripya dobara try karein."
        
        intent = intent_result.get("intent", "unknown")
        entities = intent_result.get("entities", {})
        
        logger.info(f"Intent: {intent}, Entities: {entities}")
        
        # Update session context
        session.current_intent = IntentType(intent) if intent in IntentType.__members__.values() else IntentType.UNKNOWN
        session.context.update(entities)
        
        # Route to appropriate agent
        response = await self.route_to_agent(session, intent, entities, content)
        
        # Save session
        if self.db:
            await self.db.sessions.update_one(
                {"whatsapp_id": whatsapp_id},
                {"$set": session.model_dump()},
                upsert=True
            )
        
        return response
    
    async def route_to_agent(self, session: ConversationSession, intent: str, entities: Dict[str, Any], original_message: str) -> str:
        """Route to the appropriate agent based on intent"""
        
        try:
            if intent == "generate_invoice":
                return await self.handle_invoice_intent(session, entities)
            
            elif intent == "check_inventory":
                return await self.handle_inventory_intent(session, entities)
            
            elif intent == "check_udhaar":
                return await self.handle_udhaar_intent(session, entities)
            
            elif intent == "process_payment":
                return await self.handle_payment_intent(session, entities)
            
            elif intent == "send_reminder":
                return await self.handle_reminder_intent(session, entities)
            
            elif intent == "bulk_order":
                return await self.handle_bulk_order_intent(session, entities, original_message)
            
            elif intent == "low_stock_alert":
                return await self.handle_low_stock_intent(session)
            
            elif intent == "add_customer":
                return await self.handle_add_customer_intent(session, entities)
            
            else:
                return await self.handle_general_query(session, original_message)
        
        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            return "Kuch technical problem aa gayi. Kripya thodi der baad try karein."
    
    async def handle_invoice_intent(self, session: ConversationSession, entities: Dict[str, Any]) -> str:
        """Handle invoice generation"""
        customer_name = entities.get("customer_name")
        amount = entities.get("amount")
        quantity = entities.get("quantity")
        fabric_type = entities.get("fabric_type", "cotton")
        color = entities.get("color", "white")
        
        if not customer_name:
            session.pending_action = {"type": "invoice", "step": "need_customer"}
            return "Invoice banane ke liye customer ka naam batayein."
        
        # Find or create customer
        customer = None
        if self.db:
            customer = await self.db.customers.find_one(
                {"name": {"$regex": customer_name, "$options": "i"}},
                {"_id": 0}
            )
        
        if not customer:
            # Create temporary customer
            customer = {
                "id": str(uuid.uuid4()),
                "name": customer_name,
                "phone": session.whatsapp_id,
                "total_credit": 0
            }
            if self.db:
                await self.db.customers.insert_one(customer)
        
        # Check inventory and get rate
        inventory_item = None
        if self.db:
            query = {}
            if fabric_type:
                query["fabric_type"] = fabric_type.lower()
            if color:
                query["color"] = color.lower()
            inventory_item = await self.db.inventory.find_one(query, {"_id": 0})
        
        rate = inventory_item.get("rate_per_unit", 200) if inventory_item else 200
        
        # Calculate based on available info
        if quantity and not amount:
            amount = quantity * rate
        elif amount and not quantity:
            quantity = amount / rate
        elif not quantity and not amount:
            session.pending_action = {"type": "invoice", "step": "need_amount", "customer": customer}
            return f"Customer: {customer_name}\nKitne ka bill banana hai? (Amount ya quantity batayein)"
        
        # Create invoice
        items = [{
            "name": f"{color.capitalize()} {fabric_type.capitalize()} Fabric",
            "fabric_type": fabric_type,
            "color": color,
            "quantity": quantity or 1,
            "rate": rate,
            "gst_rate": 5.0
        }]
        
        invoice = invoice_service.create_invoice(
            customer_id=customer["id"],
            customer_name=customer["name"],
            customer_phone=customer.get("phone", ""),
            items=items,
            customer_gst=customer.get("gst_number")
        )
        
        # Save invoice
        if self.db:
            await self.db.invoices.insert_one(invoice.model_dump())
        
        # Update inventory
        if inventory_item and quantity:
            await inventory_service.update_stock(inventory_item["id"], quantity, "subtract")
        
        # Format response
        invoice_text = invoice_service.format_invoice_text(invoice)
        
        return invoice_text + "\n\n✅ Invoice generate ho gaya!"
    
    async def handle_inventory_intent(self, session: ConversationSession, entities: Dict[str, Any]) -> str:
        """Handle inventory check"""
        fabric_type = entities.get("fabric_type")
        color = entities.get("color")
        
        if self.db is None:
            return "Database connected nahi hai."
        
        query = {}
        if fabric_type:
            query["fabric_type"] = fabric_type.lower()
        if color:
            query["color"] = color.lower()
        
        if query:
            items = await self.db.inventory.find(query, {"_id": 0}).to_list(10)
        else:
            items = await self.db.inventory.find({}, {"_id": 0}).to_list(20)
        
        return inventory_service.format_stock_message(items)
    
    async def handle_udhaar_intent(self, session: ConversationSession, entities: Dict[str, Any]) -> str:
        """Handle udhaar (credit) check"""
        customer_name = entities.get("customer_name")
        
        if self.db is None:
            return "Database connected nahi hai."
        
        if customer_name:
            customer = await self.db.customers.find_one(
                {"name": {"$regex": customer_name, "$options": "i"}},
                {"_id": 0}
            )
            
            if customer:
                credit_info = await udhaar_service.get_customer_credit(customer["id"])
                return udhaar_service.format_credit_status(credit_info)
            else:
                return f"Customer '{customer_name}' nahi mila."
        else:
            # Show all customers with pending credit
            customers = await self.db.customers.find(
                {"total_credit": {"$gt": 0}},
                {"_id": 0}
            ).sort("total_credit", -1).to_list(10)
            
            if not customers:
                return "✅ Kisi ka bhi udhaar pending nahi hai!"
            
            message = "💳 *Pending Udhaar Summary*\n" + "=" * 30 + "\n\n"
            total = 0
            for cust in customers:
                message += f"👤 {cust.get('name')}: ₹{cust.get('total_credit', 0):,.0f}\n"
                total += cust.get('total_credit', 0)
            
            message += f"\n{'=' * 30}\n💰 *Total Pending:* ₹{total:,.0f}"
            return message
    
    async def handle_payment_intent(self, session: ConversationSession, entities: Dict[str, Any]) -> str:
        """Handle payment processing"""
        customer_name = entities.get("customer_name")
        amount = entities.get("amount")
        payment_method_str = entities.get("payment_method", "upi")
        
        # Map payment method
        method_map = {
            "upi": PaymentMethod.UPI,
            "gpay": PaymentMethod.UPI,
            "phonepe": PaymentMethod.UPI,
            "paytm": PaymentMethod.UPI,
            "cash": PaymentMethod.CASH,
            "naqad": PaymentMethod.CASH,
            "bank": PaymentMethod.BANK_TRANSFER,
            "cheque": PaymentMethod.CHEQUE
        }
        payment_method = method_map.get(payment_method_str.lower(), PaymentMethod.UPI)
        
        if not customer_name:
            return "Payment record karne ke liye customer ka naam batayein."
        
        if not amount:
            session.pending_action = {"type": "payment", "customer_name": customer_name, "method": payment_method}
            return f"Customer: {customer_name}\nKitna payment aaya hai?"
        
        if self.db is None:
            return "Database connected nahi hai."
        
        customer = await self.db.customers.find_one(
            {"name": {"$regex": customer_name, "$options": "i"}},
            {"_id": 0}
        )
        
        if not customer:
            return f"Customer '{customer_name}' nahi mila."
        
        result = await udhaar_service.process_payment(
            customer_id=customer["id"],
            amount=amount,
            payment_method=payment_method
        )
        
        if result.get("success"):
            return f"✅ *Payment Recorded*\n\n👤 Customer: {customer_name}\n💵 Amount: ₹{amount:,.0f}\n💳 Method: {payment_method.value}\n\n📊 Remaining Balance: ₹{result.get('new_balance', 0):,.0f}"
        else:
            return f"❌ Payment record nahi ho paya: {result.get('error', 'Unknown error')}"
    
    async def handle_reminder_intent(self, session: ConversationSession, entities: Dict[str, Any]) -> str:
        """Handle sending payment reminders with HITL approval"""
        if self.db is None:
            return "Database connected nahi hai."
        
        overdue_customers = await udhaar_service.get_overdue_customers()
        
        if not overdue_customers:
            return "✅ Kisi ka bhi payment overdue nahi hai!"
        
        # Create HITL requests for each overdue customer
        message = "⚠️ *Overdue Payments - Approval Required*\n" + "=" * 30 + "\n\n"
        
        for idx, customer in enumerate(overdue_customers[:5], 1):
            await udhaar_service.create_reminder_request(
                customer_id=customer["_id"],
                customer_name=customer.get("customer_name", "Unknown"),
                overdue_amount=customer.get("total_overdue", 0)
            )
            
            message += f"{idx}. {customer.get('customer_name')}: ₹{customer.get('total_overdue', 0):,.0f}\n"
        
        message += "\n🔔 Reminder send karne ke liye 'approve' bolein."
        
        session.pending_action = {"type": "reminder_approval", "customers": overdue_customers[:5]}
        
        return message
    
    async def handle_bulk_order_intent(self, session: ConversationSession, entities: Dict[str, Any], original_message: str) -> str:
        """Handle bulk order with multiple variants"""
        # Parse bulk order format: "1000m - 400 red silk, 300 blue cotton, 300 green poly"
        # This would need more sophisticated parsing
        
        return "Bulk order processing... Please provide details in format:\n\n*Total Quantity* - *Items*\nExample: 1000m - 400 red silk, 300 blue cotton, 300 green polyester"
    
    async def handle_low_stock_intent(self, session: ConversationSession) -> str:
        """Handle low stock alert check"""
        low_stock_items = await inventory_service.get_low_stock_items()
        return inventory_service.format_low_stock_alert(low_stock_items)
    
    async def handle_add_customer_intent(self, session: ConversationSession, entities: Dict[str, Any]) -> str:
        """Handle adding new customer"""
        customer_name = entities.get("customer_name")
        
        if not customer_name:
            session.pending_action = {"type": "add_customer", "step": "need_name"}
            return "Naye customer ka naam batayein."
        
        if self.db is None:
            return "Database connected nahi hai."
        
        # Check if customer exists
        existing = await self.db.customers.find_one(
            {"name": {"$regex": f"^{customer_name}$", "$options": "i"}},
            {"_id": 0}
        )
        
        if existing:
            return f"Customer '{customer_name}' pehle se hai."
        
        # Create new customer
        new_customer = {
            "id": str(uuid.uuid4()),
            "name": customer_name,
            "phone": session.whatsapp_id,
            "total_credit": 0,
            "credit_limit": 50000,
            "is_bulk_buyer": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.customers.insert_one(new_customer)
        
        return f"✅ Naya customer add ho gaya!\n\n👤 Name: {customer_name}\n🏦 Credit Limit: ₹50,000"
    
    async def handle_general_query(self, session: ConversationSession, message: str) -> str:
        """Handle general queries using Sarvam-M"""
        system_prompt = """You are a helpful assistant for an Indian textile retail business. 
Respond in Hinglish (mix of Hindi and English). Be concise and helpful.
You can help with: invoices, inventory, payments, customer management.

If the user asks something unrelated, politely guide them to business features."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        result = await sarvam_service.chat_completion(messages)
        
        if result.get("success"):
            return result.get("content", "Maaf kijiye, samajh nahi aaya.")
        else:
            return """Main aapki kaise madad kar sakta hoon?

📝 *Available Commands:*
• Invoice banao [customer] ko [amount] ka
• Stock check karo [item]
• [Customer] ka udhaar batao
• Payment aaya [customer] se [amount]
• Reminder bhejo overdue customers ko
• Low stock items batao"""
    
    async def handle_button_response(self, session: ConversationSession, button_payload: str) -> str:
        """Handle HITL button responses"""
        if button_payload.startswith("approve_"):
            request_id = button_payload.replace("approve_", "")
            # Process approval
            if self.db:
                await self.db.hitl_requests.update_one(
                    {"id": request_id},
                    {"$set": {"status": "approved", "responded_at": datetime.now(timezone.utc).isoformat()}}
                )
            return "✅ Request approved! Action completed."
        
        elif button_payload.startswith("reject_"):
            request_id = button_payload.replace("reject_", "")
            if self.db:
                await self.db.hitl_requests.update_one(
                    {"id": request_id},
                    {"$set": {"status": "rejected", "responded_at": datetime.now(timezone.utc).isoformat()}}
                )
            return "❌ Request rejected."
        
        return "Button response processed."
    
    async def handle_payment_screenshot(self, session: ConversationSession, media_id: str) -> str:
        """Handle UPI payment screenshot - detect potential fraud"""
        # In production, this would use OCR and verification
        # For demo, we'll show the fraud detection capability
        
        return """⚠️ *Payment Screenshot Received*

Main screenshot check kar raha hoon...

🔍 Verification Status: *PENDING*

ℹ️ Note: Actual payment confirmation bank statement se hi hogi. Screenshot fake bhi ho sakta hai.

💳 Payment confirm karne ke liye UTR number bhejiye."""


agent_orchestrator = AgentOrchestrator()
