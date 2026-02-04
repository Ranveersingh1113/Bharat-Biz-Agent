from fastapi import FastAPI, APIRouter, Request, HTTPException, Query, UploadFile, File, Body
from fastapi.responses import JSONResponse, HTMLResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import json

from config import settings
from models import (
    Customer, CustomerCreate, InventoryItem, InventoryItemCreate,
    Invoice, MessageType, IntentType, FabricType
)
from agents.agent_orchestrator import agent_orchestrator
from services.whatsapp_service import whatsapp_service
from services.sarvam_service import sarvam_service
from services.invoice_service import invoice_service
from services.inventory_service import inventory_service
from services.udhaar_service import udhaar_service

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'bharat_biz_agent')]

# Create the main app
app = FastAPI(
    title="Bharat Biz-Agent API",
    description="AI Co-pilot for Indian SMBs - Textile Retail",
    version="1.0.0"
)

# Create routers
api_router = APIRouter(prefix="/api")
webhook_router = APIRouter(prefix="/api/webhook", tags=["WhatsApp Webhook"])

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== WHATSAPP WEBHOOK ====================

@webhook_router.get("")
async def verify_webhook(
    request: Request
):
    """WhatsApp webhook verification endpoint"""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    logger.info(f"Webhook verification: mode={mode}, token={token}")
    
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logger.info("Webhook verified successfully!")
        return int(challenge)
    else:
        logger.warning(f"Webhook verification failed. Expected token: {settings.whatsapp_verify_token}")
        raise HTTPException(status_code=403, detail="Verification failed")

@webhook_router.post("")
async def receive_webhook(request: Request):
    """Receive incoming WhatsApp messages"""
    try:
        body = await request.json()
        logger.info(f"Webhook received: {json.dumps(body, indent=2)}")
        
        # Verify it's a WhatsApp Business Account message
        if body.get("object") != "whatsapp_business_account":
            return JSONResponse(status_code=200, content={"status": "ignored"})
        
        entries = body.get("entry", [])
        
        for entry in entries:
            changes = entry.get("changes", [])
            
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                
                for message in messages:
                    await process_incoming_message(message, value)
                
                # Process status updates
                statuses = value.get("statuses", [])
                for status in statuses:
                    await process_status_update(status)
        
        return JSONResponse(status_code=200, content={"status": "ok"})
    
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JSONResponse(status_code=200, content={"status": "error", "message": str(e)})

async def process_incoming_message(message: dict, metadata: dict):
    """Process incoming WhatsApp message"""
    try:
        message_id = message.get("id")
        from_number = message.get("from")
        timestamp = message.get("timestamp")
        message_type = message.get("type")
        
        logger.info(f"Processing message from {from_number}: type={message_type}")
        
        # Mark as read
        await whatsapp_service.mark_as_read(message_id)
        
        # Extract content based on message type
        content = None
        media_id = None
        button_payload = None
        
        if message_type == "text":
            content = message.get("text", {}).get("body", "")
            msg_type = MessageType.TEXT
        
        elif message_type == "audio":
            media_id = message.get("audio", {}).get("id")
            msg_type = MessageType.AUDIO
        
        elif message_type == "image":
            media_id = message.get("image", {}).get("id")
            msg_type = MessageType.IMAGE
        
        elif message_type == "button":
            content = message.get("button", {}).get("text", "")
            button_payload = message.get("button", {}).get("payload", "")
            msg_type = MessageType.BUTTON
        
        elif message_type == "interactive":
            interactive = message.get("interactive", {})
            if interactive.get("type") == "button_reply":
                button_payload = interactive.get("button_reply", {}).get("id", "")
                content = interactive.get("button_reply", {}).get("title", "")
            elif interactive.get("type") == "list_reply":
                button_payload = interactive.get("list_reply", {}).get("id", "")
                content = interactive.get("list_reply", {}).get("title", "")
            msg_type = MessageType.INTERACTIVE
        
        else:
            logger.info(f"Unsupported message type: {message_type}")
            await whatsapp_service.send_text_message(
                from_number,
                "Maaf kijiye, is type ka message support nahi hai. Text ya voice message bhejiye."
            )
            return
        
        # Save incoming message to DB
        msg_doc = {
            "id": str(uuid.uuid4()),
            "message_id": message_id,
            "from_number": from_number,
            "message_type": message_type,
            "content": content,
            "media_id": media_id,
            "direction": "inbound",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.messages.insert_one(msg_doc)
        
        # Process with agent orchestrator
        response = await agent_orchestrator.process_message(
            whatsapp_id=from_number,
            message_type=msg_type,
            content=content,
            media_id=media_id,
            button_payload=button_payload
        )
        
        # Send response
        if response:
            await whatsapp_service.send_text_message(from_number, response)
            
            # Save outgoing message
            out_msg_doc = {
                "id": str(uuid.uuid4()),
                "from_number": settings.whatsapp_phone_number_id,
                "to_number": from_number,
                "message_type": "text",
                "content": response,
                "direction": "outbound",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.messages.insert_one(out_msg_doc)
    
    except Exception as e:
        logger.error(f"Message processing error: {str(e)}")
        # Try to send error message
        try:
            await whatsapp_service.send_text_message(
                message.get("from"),
                "Kuch problem aa gayi. Kripya thodi der baad try karein."
            )
        except:
            pass

async def process_status_update(status: dict):
    """Process message status update"""
    message_id = status.get("id")
    status_value = status.get("status")  # sent, delivered, read, failed
    
    logger.info(f"Status update: {message_id} -> {status_value}")
    
    # Update message status in DB
    await db.messages.update_one(
        {"message_id": message_id},
        {"$set": {"status": status_value, "status_updated_at": datetime.now(timezone.utc).isoformat()}}
    )

# ==================== API ROUTES ====================

@api_router.get("/")
async def root():
    return {
        "message": "Bharat Biz-Agent API",
        "version": "1.0.0",
        "status": "running"
    }

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "connected",
        "whatsapp": "configured" if settings.whatsapp_access_token else "not_configured",
        "sarvam": "configured" if settings.sarvam_api_key else "not_configured"
    }

# ==================== CUSTOMER ROUTES ====================

@api_router.get("/customers")
async def get_customers(limit: int = 50, skip: int = 0):
    """Get all customers"""
    customers = await db.customers.find({}, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    return {"customers": customers, "count": len(customers)}

@api_router.post("/customers")
async def create_customer(customer: CustomerCreate):
    """Create new customer"""
    customer_doc = {
        "id": str(uuid.uuid4()),
        **customer.model_dump(),
        "total_credit": 0,
        "credit_limit": 50000,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.customers.insert_one(customer_doc)
    return {"success": True, "customer": customer_doc}

@api_router.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get customer by ID"""
    customer = await db.customers.find_one({"id": customer_id}, {"_id": 0})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@api_router.get("/customers/{customer_id}/credit")
async def get_customer_credit(customer_id: str):
    """Get customer credit status"""
    credit_info = await udhaar_service.get_customer_credit(customer_id)
    if "error" in credit_info:
        raise HTTPException(status_code=404, detail=credit_info["error"])
    return credit_info

# ==================== INVENTORY ROUTES ====================

@api_router.get("/inventory")
async def get_inventory(
    fabric_type: Optional[str] = None,
    color: Optional[str] = None,
    limit: int = 50
):
    """Get inventory items with optional filters"""
    query = {}
    if fabric_type:
        query["fabric_type"] = fabric_type.lower()
    if color:
        query["color"] = color.lower()
    
    items = await db.inventory.find(query, {"_id": 0}).limit(limit).to_list(limit)
    return {"items": items, "count": len(items)}

@api_router.post("/inventory")
async def create_inventory_item(item: InventoryItemCreate):
    """Add new inventory item"""
    item_doc = {
        "id": str(uuid.uuid4()),
        **item.model_dump(),
        "wastage_percent": 0.0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.inventory.insert_one(item_doc)
    return {"success": True, "item": item_doc}

@api_router.get("/inventory/low-stock")
async def get_low_stock():
    """Get items below reorder level"""
    items = await inventory_service.get_low_stock_items()
    return {"items": items, "count": len(items)}

@api_router.get("/inventory/summary")
async def get_inventory_summary():
    """Get inventory summary by fabric type"""
    summary = await inventory_service.get_inventory_summary()
    return summary

# ==================== INVOICE ROUTES ====================

@api_router.get("/invoices")
async def get_invoices(
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """Get invoices with optional filters"""
    query = {}
    if customer_id:
        query["customer_id"] = customer_id
    if status:
        query["payment_status"] = status
    
    invoices = await db.invoices.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"invoices": invoices, "count": len(invoices)}

@api_router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Get invoice by ID"""
    invoice = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@api_router.get("/invoices/{invoice_id}/html")
async def get_invoice_html(invoice_id: str):
    """Get invoice as HTML"""
    invoice_data = await db.invoices.find_one({"id": invoice_id}, {"_id": 0})
    if not invoice_data:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    from models import Invoice, InvoiceLineItem
    
    # Reconstruct Invoice object
    line_items = [InvoiceLineItem(**item) for item in invoice_data.get("items", [])]
    invoice_data["items"] = line_items
    invoice = Invoice(**invoice_data)
    
    html = invoice_service.generate_invoice_html(invoice)
    return HTMLResponse(content=html)

# ==================== UDHAAR ROUTES ====================

@api_router.get("/udhaar/overdue")
async def get_overdue_customers():
    """Get customers with overdue payments"""
    overdue = await udhaar_service.get_overdue_customers()
    return {"overdue_customers": overdue, "count": len(overdue)}

@api_router.get("/udhaar/summary")
async def get_udhaar_summary():
    """Get overall udhaar summary"""
    pipeline = [
        {"$match": {"total_credit": {"$gt": 0}}},
        {"$group": {
            "_id": None,
            "total_pending": {"$sum": "$total_credit"},
            "customer_count": {"$sum": 1}
        }}
    ]
    result = await db.customers.aggregate(pipeline).to_list(1)
    
    if result:
        return {
            "total_pending": result[0].get("total_pending", 0),
            "customer_count": result[0].get("customer_count", 0)
        }
    return {"total_pending": 0, "customer_count": 0}

# ==================== HITL ROUTES ====================

@api_router.get("/hitl/pending")
async def get_pending_hitl_requests():
    """Get pending HITL approval requests"""
    requests = await db.hitl_requests.find(
        {"status": "pending"},
        {"_id": 0}
    ).sort("requested_at", -1).to_list(50)
    return {"requests": requests, "count": len(requests)}

@api_router.post("/hitl/{request_id}/approve")
async def approve_hitl_request(request_id: str):
    """Approve HITL request"""
    result = await db.hitl_requests.update_one(
        {"id": request_id},
        {"$set": {
            "status": "approved",
            "responded_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"success": True, "status": "approved"}

@api_router.post("/hitl/{request_id}/reject")
async def reject_hitl_request(request_id: str):
    """Reject HITL request"""
    result = await db.hitl_requests.update_one(
        {"id": request_id},
        {"$set": {
            "status": "rejected",
            "responded_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"success": True, "status": "rejected"}

# ==================== MESSAGES/CONVERSATIONS ====================

@api_router.get("/conversations")
async def get_conversations(limit: int = 20):
    """Get recent conversations"""
    pipeline = [
        {"$match": {"direction": "inbound"}},
        {"$group": {
            "_id": "$from_number",
            "last_message": {"$last": "$content"},
            "last_activity": {"$max": "$created_at"},
            "message_count": {"$sum": 1}
        }},
        {"$sort": {"last_activity": -1}},
        {"$limit": limit}
    ]
    conversations = await db.messages.aggregate(pipeline).to_list(limit)
    return {"conversations": conversations}

@api_router.get("/conversations/{phone_number}")
async def get_conversation_history(phone_number: str, limit: int = 50):
    """Get conversation history with a specific number"""
    messages = await db.messages.find(
        {"$or": [{"from_number": phone_number}, {"to_number": phone_number}]},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    messages.reverse()  # Chronological order
    return {"messages": messages}

# ==================== DASHBOARD STATS ====================

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    # Today's date range
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Total customers
    total_customers = await db.customers.count_documents({})
    
    # Total pending udhaar
    udhaar_pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$total_credit"}}}
    ]
    udhaar_result = await db.customers.aggregate(udhaar_pipeline).to_list(1)
    total_udhaar = udhaar_result[0]["total"] if udhaar_result else 0
    
    # Today's invoices
    today_invoices = await db.invoices.count_documents({
        "created_at": {"$gte": today_start.isoformat()}
    })
    
    # Today's sales
    sales_pipeline = [
        {"$match": {"created_at": {"$gte": today_start.isoformat()}}},
        {"$group": {"_id": None, "total": {"$sum": "$grand_total"}}}
    ]
    sales_result = await db.invoices.aggregate(sales_pipeline).to_list(1)
    today_sales = sales_result[0]["total"] if sales_result else 0
    
    # Low stock count
    low_stock_items = await inventory_service.get_low_stock_items()
    
    # Pending HITL
    pending_hitl = await db.hitl_requests.count_documents({"status": "pending"})
    
    return {
        "total_customers": total_customers,
        "total_pending_udhaar": total_udhaar,
        "today_invoices": today_invoices,
        "today_sales": today_sales,
        "low_stock_count": len(low_stock_items),
        "pending_approvals": pending_hitl
    }

# ==================== TEST ENDPOINTS ====================

@api_router.post("/test/send-message")
async def test_send_message(to_number: str = Body(...), message: str = Body(...)):
    """Test endpoint to send WhatsApp message"""
    result = await whatsapp_service.send_text_message(to_number, message)
    return result

@api_router.post("/test/process-text")
async def test_process_text(text: str = Body(...), phone: str = Body(default="test_user")):
    """Test endpoint to process text through agent"""
    response = await agent_orchestrator.process_message(
        whatsapp_id=phone,
        message_type=MessageType.TEXT,
        content=text
    )
    return {"input": text, "response": response}

@api_router.post("/test/classify-intent")
async def test_classify_intent(text: str = Body(...)):
    """Test intent classification"""
    result = await sarvam_service.classify_intent(text)
    return result

# ==================== APP SETUP ====================

# Include routers
app.include_router(api_router)
app.include_router(webhook_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Bharat Biz-Agent...")
    
    # Set database for services
    agent_orchestrator.set_db(db)
    inventory_service.set_db(db)
    udhaar_service.set_db(db)
    
    # Create indexes
    await db.customers.create_index("id", unique=True)
    await db.customers.create_index("phone")
    await db.customers.create_index("name")
    await db.inventory.create_index("id", unique=True)
    await db.inventory.create_index([("fabric_type", 1), ("color", 1)])
    await db.invoices.create_index("id", unique=True)
    await db.invoices.create_index("customer_id")
    await db.invoices.create_index("created_at")
    await db.messages.create_index("message_id")
    await db.messages.create_index("from_number")
    await db.sessions.create_index("whatsapp_id", unique=True)
    await db.hitl_requests.create_index("id", unique=True)
    await db.hitl_requests.create_index("status")
    
    # Seed sample data if empty
    await seed_sample_data()
    
    logger.info("Bharat Biz-Agent started successfully!")

async def seed_sample_data():
    """Seed sample data for demo"""
    # Check if data exists
    customer_count = await db.customers.count_documents({})
    if customer_count > 0:
        return
    
    logger.info("Seeding sample data...")
    
    # Sample customers
    customers = [
        {"id": str(uuid.uuid4()), "name": "Ramesh Kapoor", "phone": "+919876543210", "total_credit": 15000, "credit_limit": 50000, "is_bulk_buyer": False, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Suresh Gupta", "phone": "+919876543211", "total_credit": 45000, "credit_limit": 100000, "is_bulk_buyer": True, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Mohan Lal", "phone": "+919876543212", "total_credit": 8500, "credit_limit": 30000, "is_bulk_buyer": False, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Priya Sharma", "phone": "+919876543213", "total_credit": 0, "credit_limit": 25000, "is_bulk_buyer": False, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Anil Verma", "phone": "+919876543214", "total_credit": 22000, "credit_limit": 50000, "is_bulk_buyer": False, "created_at": datetime.now(timezone.utc).isoformat()},
    ]
    await db.customers.insert_many(customers)
    
    # Sample inventory
    inventory = [
        {"id": str(uuid.uuid4()), "name": "Red Silk Fabric", "fabric_type": "silk", "color": "red", "width": 44, "grade": "A", "hsn_code": "5007", "quantity": 250, "unit": "meter", "rate_per_unit": 450, "gst_rate": 5.0, "reorder_level": 50, "wastage_percent": 0, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Blue Cotton Fabric", "fabric_type": "cotton", "color": "blue", "width": 54, "grade": "A", "hsn_code": "5208", "quantity": 180, "unit": "meter", "rate_per_unit": 180, "gst_rate": 5.0, "reorder_level": 100, "wastage_percent": 0, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Green Polyester Fabric", "fabric_type": "polyester", "color": "green", "width": 60, "grade": "B", "hsn_code": "5407", "quantity": 45, "unit": "meter", "rate_per_unit": 120, "gst_rate": 5.0, "reorder_level": 50, "wastage_percent": 0, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "White Cotton Fabric", "fabric_type": "cotton", "color": "white", "width": 44, "grade": "A", "hsn_code": "5208", "quantity": 320, "unit": "meter", "rate_per_unit": 150, "gst_rate": 5.0, "reorder_level": 80, "wastage_percent": 0, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Black Silk Fabric", "fabric_type": "silk", "color": "black", "width": 44, "grade": "A+", "hsn_code": "5007", "quantity": 30, "unit": "meter", "rate_per_unit": 550, "gst_rate": 5.0, "reorder_level": 40, "wastage_percent": 0, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Yellow Linen Fabric", "fabric_type": "linen", "color": "yellow", "width": 54, "grade": "A", "hsn_code": "5309", "quantity": 85, "unit": "meter", "rate_per_unit": 280, "gst_rate": 5.0, "reorder_level": 30, "wastage_percent": 0, "created_at": datetime.now(timezone.utc).isoformat()},
    ]
    await db.inventory.insert_many(inventory)
    
    logger.info("Sample data seeded successfully!")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
