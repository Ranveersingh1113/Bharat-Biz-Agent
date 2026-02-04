import logging
import hashlib
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple
import uuid

logger = logging.getLogger(__name__)

class SecurityManager:
    """Security features: DM Pairing, PII Masking, and validation"""
    
    def __init__(self):
        self.pairing_codes: Dict[str, Dict[str, Any]] = {}  # phone -> pairing info
        self.dm_policy = "pairing"  # pairing, allowlist, open, disabled
        self.allowlist: set = set()
    
    # ==================== DM PAIRING ====================
    
    def generate_pairing_code(self, phone_number: str) -> str:
        """Generate 6-digit pairing code for device verification"""
        code = str(uuid.uuid4().int)[:6]
        
        self.pairing_codes[phone_number] = {
            "code": code,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
            "verified": False,
            "attempts": 0
        }
        
        logger.info(f"Pairing code generated for {self.mask_phone(phone_number)}")
        return code
    
    def verify_pairing_code(self, phone_number: str, code: str) -> Tuple[bool, str]:
        """Verify pairing code"""
        if phone_number not in self.pairing_codes:
            return False, "No pairing code found. Request a new code."
        
        pairing_info = self.pairing_codes[phone_number]
        
        # Check expiry
        if datetime.now(timezone.utc) > pairing_info["expires_at"]:
            del self.pairing_codes[phone_number]
            return False, "Pairing code expired. Request a new code."
        
        # Check attempts
        if pairing_info["attempts"] >= 3:
            del self.pairing_codes[phone_number]
            return False, "Too many failed attempts. Request a new code."
        
        # Verify code
        if pairing_info["code"] == code:
            pairing_info["verified"] = True
            self.allowlist.add(phone_number)
            logger.info(f"Device paired successfully for {self.mask_phone(phone_number)}")
            return True, "Device paired successfully! You can now use all features."
        else:
            pairing_info["attempts"] += 1
            return False, f"Invalid code. {3 - pairing_info['attempts']} attempts remaining."
    
    def is_device_paired(self, phone_number: str) -> bool:
        """Check if device is paired/authorized"""
        if self.dm_policy == "open":
            return True
        if self.dm_policy == "disabled":
            return False
        if self.dm_policy == "allowlist":
            return phone_number in self.allowlist
        if self.dm_policy == "pairing":
            return phone_number in self.allowlist or (
                phone_number in self.pairing_codes and 
                self.pairing_codes[phone_number].get("verified", False)
            )
        return False
    
    def get_pairing_status(self, phone_number: str) -> Dict[str, Any]:
        """Get pairing status for a phone number"""
        return {
            "phone": self.mask_phone(phone_number),
            "is_paired": self.is_device_paired(phone_number),
            "policy": self.dm_policy,
            "in_allowlist": phone_number in self.allowlist
        }
    
    # ==================== PII MASKING ====================
    
    def mask_phone(self, phone: str) -> str:
        """Mask phone number: +91987654XXXX"""
        if not phone:
            return "[PHONE_MASKED]"
        if len(phone) > 4:
            return phone[:-4] + "XXXX"
        return "XXXX"
    
    def mask_email(self, email: str) -> str:
        """Mask email: r***h@gmail.com"""
        if not email or '@' not in email:
            return "[EMAIL_MASKED]"
        local, domain = email.split('@', 1)
        if len(local) > 2:
            masked_local = local[0] + "***" + local[-1]
        else:
            masked_local = "***"
        return f"{masked_local}@{domain}"
    
    def mask_name(self, name: str) -> str:
        """Mask name: R***h K***r"""
        if not name:
            return "[NAME_MASKED]"
        
        words = name.split()
        masked_words = []
        for word in words:
            if len(word) > 2:
                masked_words.append(word[0] + "***" + word[-1])
            else:
                masked_words.append("***")
        return " ".join(masked_words)
    
    def mask_amount(self, amount: float) -> str:
        """Mask amount: ₹XX,XXX"""
        return "₹XX,XXX"
    
    def mask_gst(self, gst: str) -> str:
        """Mask GST number: 07AABCK****L1ZX"""
        if not gst or len(gst) < 10:
            return "[GST_MASKED]"
        return gst[:6] + "****" + gst[-4:]
    
    def mask_pii_in_text(self, text: str, mask_level: str = "full") -> str:
        """
        Mask PII in text content
        mask_level: 'full', 'partial', 'none'
        """
        if mask_level == "none":
            return text
        
        masked_text = text
        
        # Mask phone numbers
        phone_pattern = r'(\+?91[-\s]?)?(\d{10}|\d{5}[-\s]?\d{5})'
        masked_text = re.sub(phone_pattern, lambda m: self.mask_phone(m.group()), masked_text)
        
        # Mask email addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        masked_text = re.sub(email_pattern, lambda m: self.mask_email(m.group()), masked_text)
        
        # Mask GST numbers (15 alphanumeric)
        gst_pattern = r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d{1}[A-Z]{1}[A-Z\d]{1}\b'
        masked_text = re.sub(gst_pattern, lambda m: self.mask_gst(m.group()), masked_text)
        
        # Mask Aadhaar numbers (12 digits)
        aadhaar_pattern = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        masked_text = re.sub(aadhaar_pattern, '[AADHAAR_MASKED]', masked_text)
        
        # Mask PAN numbers
        pan_pattern = r'\b[A-Z]{5}\d{4}[A-Z]{1}\b'
        masked_text = re.sub(pan_pattern, '[PAN_MASKED]', masked_text)
        
        if mask_level == "full":
            # Mask amounts (₹ or Rs followed by numbers)
            amount_pattern = r'[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
            # Only mask large amounts (>10000) in full mode
            def mask_large_amount(match):
                try:
                    amount = float(match.group(1).replace(',', ''))
                    if amount > 10000:
                        return '₹XX,XXX'
                except:
                    pass
                return match.group(0)
            masked_text = re.sub(amount_pattern, mask_large_amount, masked_text)
        
        return masked_text
    
    def create_audit_safe_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an audit-safe version of data with PII masked"""
        safe_data = {}
        
        for key, value in data.items():
            if key in ['phone', 'customer_phone', 'from_number', 'to_number']:
                safe_data[key] = self.mask_phone(str(value)) if value else None
            elif key in ['email', 'customer_email']:
                safe_data[key] = self.mask_email(str(value)) if value else None
            elif key in ['name', 'customer_name']:
                safe_data[key] = self.mask_name(str(value)) if value else None
            elif key in ['gst_number', 'customer_gst']:
                safe_data[key] = self.mask_gst(str(value)) if value else None
            elif key in ['content', 'message', 'text']:
                safe_data[key] = self.mask_pii_in_text(str(value), "partial") if value else None
            else:
                safe_data[key] = value
        
        return safe_data

# ==================== AUDIT LOGGER ====================

class AuditLogger:
    """Audit logging for all business actions"""
    
    def __init__(self, db=None):
        self.db = db
        self.security_manager = SecurityManager()
    
    def set_db(self, db):
        self.db = db
    
    async def log_action(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """Log an action to audit trail"""
        if self.db is None:
            logger.warning("Audit logger: DB not configured")
            return
        
        # Mask PII in details
        safe_details = self.security_manager.create_audit_safe_record(details or {})
        
        audit_record = {
            "id": str(uuid.uuid4()),
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "user_id": self.security_manager.mask_phone(user_id) if user_id else None,
            "details": safe_details,
            "ip_address": ip_address,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            await self.db.audit_logs.insert_one(audit_record)
            logger.debug(f"Audit logged: {action} on {entity_type}:{entity_id}")
        except Exception as e:
            logger.error(f"Audit logging failed: {str(e)}")
    
    async def get_audit_trail(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """Retrieve audit trail"""
        if self.db is None:
            return []
        
        query = {}
        if entity_type:
            query["entity_type"] = entity_type
        if entity_id:
            query["entity_id"] = entity_id
        if action:
            query["action"] = action
        
        records = await self.db.audit_logs.find(
            query, {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return records

security_manager = SecurityManager()
audit_logger = AuditLogger()
