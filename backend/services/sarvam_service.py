import httpx
import logging
from typing import Dict, Any, Optional, List
from config import settings
import json
import re

logger = logging.getLogger(__name__)

class SarvamService:
    """Service for Sarvam AI operations - Hinglish NLP and Speech-to-Text"""
    
    def __init__(self):
        self.api_key = settings.sarvam_api_key
        self.base_url = "https://api.sarvam.ai"
        self.headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def chat_completion(self, messages: List[Dict[str, str]], model: str = "sarvam-m") -> Dict[str, Any]:
        """Send chat completion request to Sarvam-M for Hinglish understanding"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": 0.3
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "content": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                        "model": model
                    }
                else:
                    logger.error(f"Sarvam chat error: {response.status_code} - {response.text}")
                    return {"success": False, "error": response.text}
        except Exception as e:
            logger.error(f"Sarvam chat exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def transcribe_audio(self, audio_data: bytes, language_code: str = "hi-IN") -> Dict[str, Any]:
        """Transcribe audio using Saarika v2.5"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                files = {"file": ("audio.ogg", audio_data, "audio/ogg")}
                headers = {"api-subscription-key": self.api_key}
                
                response = await client.post(
                    f"{self.base_url}/speech-to-text",
                    headers=headers,
                    files=files,
                    data={
                        "model": "saarika:v2.5",
                        "language_code": language_code
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "transcript": data.get("transcript", ""),
                        "language": data.get("language_code", language_code)
                    }
                else:
                    logger.error(f"Sarvam STT error: {response.status_code} - {response.text}")
                    return {"success": False, "error": response.text}
        except Exception as e:
            logger.error(f"Sarvam STT exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Translate text between languages"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/translate",
                    headers=self.headers,
                    json={
                        "input": text,
                        "source_language_code": source_lang,
                        "target_language_code": target_lang
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "translated_text": data.get("translated_text", "")
                    }
                else:
                    return {"success": False, "error": response.text}
        except Exception as e:
            logger.error(f"Sarvam translate exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def classify_intent(self, text: str) -> Dict[str, Any]:
        """Classify intent from Hinglish text using Sarvam-M"""
        
        system_prompt = """You are an intent classifier for an Indian textile retail business assistant.
Classify the user's message into one of these intents:
- generate_invoice: User wants to create a bill/invoice
- check_inventory: User wants to check stock/inventory
- check_udhaar: User wants to check credit/pending payments
- process_payment: User mentions payment received
- send_reminder: User wants to send payment reminders
- add_customer: User wants to add a new customer
- bulk_order: User mentions a large order with multiple items
- low_stock_alert: User asks about low stock items
- general_query: General questions about business
- unknown: Cannot determine intent

Also extract entities like:
- customer_name: Name of customer mentioned
- amount: Any monetary amount
- quantity: Quantity in meters/pieces
- fabric_type: silk, cotton, polyester, etc.
- color: Any color mentioned
- payment_method: upi, cash, gpay, phonepe, etc.

Respond in JSON format only:
{"intent": "<intent>", "entities": {"key": "value"}, "confidence": 0.0-1.0}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
        
        result = await self.chat_completion(messages)
        
        if result["success"]:
            try:
                # Parse JSON from response
                content = result["content"]
                # Extract JSON from markdown code blocks if present
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
                
                parsed = json.loads(content)
                return {
                    "success": True,
                    "intent": parsed.get("intent", "unknown"),
                    "entities": parsed.get("entities", {}),
                    "confidence": parsed.get("confidence", 0.5)
                }
            except json.JSONDecodeError:
                logger.error(f"Failed to parse intent JSON: {result['content']}")
                return self._fallback_intent_classification(text)
        else:
            return self._fallback_intent_classification(text)
    
    def _fallback_intent_classification(self, text: str) -> Dict[str, Any]:
        """Fallback regex-based intent classification for Hinglish"""
        text_lower = text.lower()
        
        # Bulk order keywords (check first as it's more specific)
        bulk_keywords = ["meter chahiye", "mtr chahiye", "m chahiye", "bulk order", "total order", "1000m", "500m", "100m"]
        # Also check for pattern like "Xm - Y red silk, Z blue cotton"
        bulk_pattern = r'\d+\s*(?:meter|mtr|m)\s*(?:chahiye|total|ka order)?\s*[-:]\s*\d+'
        if any(kw in text_lower for kw in bulk_keywords) or re.search(bulk_pattern, text_lower):
            return {"success": True, "intent": "bulk_order", "entities": self._extract_entities(text), "confidence": 0.8}
        
        # Invoice keywords
        invoice_keywords = ["invoice", "bill", "bhejo", "banao", "invoice banao", "bill de", "raseed"]
        if any(kw in text_lower for kw in invoice_keywords):
            return {"success": True, "intent": "generate_invoice", "entities": self._extract_entities(text), "confidence": 0.7}
        
        # Inventory keywords
        inventory_keywords = ["stock", "inventory", "kitna hai", "available", "maal", "check karo"]
        if any(kw in text_lower for kw in inventory_keywords):
            return {"success": True, "intent": "check_inventory", "entities": self._extract_entities(text), "confidence": 0.7}
        
        # Udhaar keywords
        udhaar_keywords = ["udhaar", "credit", "pending", "baki", "baaki", "hisaab"]
        if any(kw in text_lower for kw in udhaar_keywords):
            return {"success": True, "intent": "check_udhaar", "entities": self._extract_entities(text), "confidence": 0.7}
        
        # Payment keywords
        payment_keywords = ["payment", "paid", "bheja", "transfer", "gpay", "phonepe", "upi", "paisa"]
        if any(kw in text_lower for kw in payment_keywords):
            return {"success": True, "intent": "process_payment", "entities": self._extract_entities(text), "confidence": 0.7}
        
        # Reminder keywords
        reminder_keywords = ["reminder", "yaad", "bhulna", "follow up", "overdue"]
        if any(kw in text_lower for kw in reminder_keywords):
            return {"success": True, "intent": "send_reminder", "entities": self._extract_entities(text), "confidence": 0.7}
        
        return {"success": True, "intent": "general_query", "entities": self._extract_entities(text), "confidence": 0.5}
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text using regex patterns"""
        entities = {}
        
        # Extract amount (₹, Rs, rupees, etc.)
        amount_pattern = r'(?:₹|rs\.?|rupees?|rupaiye?)\s*(\d+(?:,\d+)*(?:\.\d+)?)|(?:(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:₹|rs\.?|rupees?|rupaiye?|ka|ki))'
        amount_match = re.search(amount_pattern, text, re.IGNORECASE)
        if amount_match:
            amount_str = amount_match.group(1) or amount_match.group(2)
            entities["amount"] = float(amount_str.replace(",", ""))
        
        # Extract quantity (meters, mtr, m)
        qty_pattern = r'(\d+(?:\.\d+)?)\s*(?:meter|mtr|m(?:eter)?s?)'
        qty_match = re.search(qty_pattern, text, re.IGNORECASE)
        if qty_match:
            entities["quantity"] = float(qty_match.group(1))
            entities["unit"] = "meter"
        
        # Extract colors
        colors = ["red", "blue", "green", "yellow", "white", "black", "pink", "orange", "purple", "laal", "neela", "hara", "peela", "safed", "kaala"]
        for color in colors:
            if color in text.lower():
                # Map Hindi colors to English
                color_map = {"laal": "red", "neela": "blue", "hara": "green", "peela": "yellow", "safed": "white", "kaala": "black"}
                entities["color"] = color_map.get(color, color)
                break
        
        # Extract fabric types
        fabrics = ["silk", "cotton", "polyester", "linen", "wool", "resham", "kapas"]
        for fabric in fabrics:
            if fabric in text.lower():
                fabric_map = {"resham": "silk", "kapas": "cotton"}
                entities["fabric_type"] = fabric_map.get(fabric, fabric)
                break
        
        # Extract potential customer names (capitalized words)
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        name_matches = re.findall(name_pattern, text)
        excluded_words = ["Invoice", "Bill", "Stock", "Payment", "Meter", "Silk", "Cotton"]
        names = [n for n in name_matches if n not in excluded_words]
        if names:
            entities["customer_name"] = names[0]
        
        return entities

sarvam_service = SarvamService()
