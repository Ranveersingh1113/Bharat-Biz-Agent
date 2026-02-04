from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid

# Enums
class InvoiceType(str, Enum):
    PUCCA = "pucca"  # GST Invoice
    KACHA = "kacha"  # Informal receipt

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"

class PaymentMethod(str, Enum):
    CASH = "cash"
    UPI = "upi"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"

class FabricType(str, Enum):
    SILK = "silk"
    COTTON = "cotton"
    POLYESTER = "polyester"
    LINEN = "linen"
    WOOL = "wool"
    SYNTHETIC = "synthetic"

class MessageType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    BUTTON = "button"
    INTERACTIVE = "interactive"

class IntentType(str, Enum):
    GENERATE_INVOICE = "generate_invoice"
    CHECK_INVENTORY = "check_inventory"
    CHECK_UDHAAR = "check_udhaar"
    PROCESS_PAYMENT = "process_payment"
    SEND_REMINDER = "send_reminder"
    ADD_CUSTOMER = "add_customer"
    GENERAL_QUERY = "general_query"
    BULK_ORDER = "bulk_order"
    LOW_STOCK_ALERT = "low_stock_alert"
    UNKNOWN = "unknown"

# Customer Model
class Customer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: str
    whatsapp_id: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    total_credit: float = 0.0
    credit_limit: float = 50000.0
    is_bulk_buyer: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomerCreate(BaseModel):
    name: str
    phone: str
    whatsapp_id: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    is_bulk_buyer: bool = False

# Inventory Item Model
class InventoryItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    fabric_type: FabricType
    color: str
    width: int = 44  # inches
    grade: str = "A"
    hsn_code: str = "5007"
    quantity: float  # meters
    unit: str = "meter"
    rate_per_unit: float
    gst_rate: float = 5.0
    reorder_level: float = 50.0
    wastage_percent: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InventoryItemCreate(BaseModel):
    name: str
    fabric_type: FabricType
    color: str
    width: int = 44
    grade: str = "A"
    hsn_code: str = "5007"
    quantity: float
    unit: str = "meter"
    rate_per_unit: float
    gst_rate: float = 5.0
    reorder_level: float = 50.0

# Invoice Line Item
class InvoiceLineItem(BaseModel):
    item_id: str
    name: str
    fabric_type: str
    color: str
    width: int
    hsn_code: str
    quantity: float
    unit: str
    rate: float
    gst_rate: float
    taxable_amount: float
    cgst_amount: float
    sgst_amount: float
    igst_amount: float
    total_amount: float

# Invoice Model
class Invoice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str
    invoice_type: InvoiceType = InvoiceType.PUCCA
    customer_id: str
    customer_name: str
    customer_phone: str
    customer_gst: Optional[str] = None
    customer_address: Optional[str] = None
    
    items: List[InvoiceLineItem]
    
    subtotal: float
    total_cgst: float
    total_sgst: float
    total_igst: float
    grand_total: float
    
    payment_status: PaymentStatus = PaymentStatus.PENDING
    amount_paid: float = 0.0
    balance_due: float = 0.0
    
    is_inter_state: bool = False
    place_of_supply: str = "Delhi"
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    due_date: Optional[datetime] = None
    pdf_path: Optional[str] = None

# Udhaar (Credit) Transaction
class UdhaarTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_name: str
    invoice_id: Optional[str] = None
    amount: float
    transaction_type: str  # "credit" or "payment"
    payment_method: Optional[PaymentMethod] = None
    balance_after: float
    notes: Optional[str] = None
    requires_approval: bool = False
    is_approved: bool = True
    approved_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Payment Verification
class PaymentVerification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    claimed_amount: float
    payment_method: PaymentMethod
    screenshot_url: Optional[str] = None
    utr_number: Optional[str] = None
    is_verified: bool = False
    is_fake: bool = False
    verification_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# WhatsApp Message
class WhatsAppMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_id: str
    from_number: str
    to_number: Optional[str] = None
    message_type: MessageType
    content: Optional[str] = None
    media_id: Optional[str] = None
    media_url: Optional[str] = None
    direction: str  # "inbound" or "outbound"
    status: str = "received"
    intent: Optional[IntentType] = None
    entities: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Conversation Session
class ConversationSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    whatsapp_id: str
    customer_id: Optional[str] = None
    messages: List[Dict[str, Any]] = []
    current_intent: Optional[IntentType] = None
    context: Dict[str, Any] = {}
    pending_action: Optional[Dict[str, Any]] = None  # For HITL
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# HITL Approval Request
class HITLRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_type: str  # "credit_reminder", "large_credit", "payment_verification"
    customer_id: str
    customer_name: str
    amount: Optional[float] = None
    details: Dict[str, Any] = {}
    status: str = "pending"  # "pending", "approved", "rejected"
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    responded_at: Optional[datetime] = None
    response_by: Optional[str] = None

# Audit Log
class AuditLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str
    entity_type: str
    entity_id: str
    user_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
