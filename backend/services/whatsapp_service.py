import httpx
import logging
from typing import Dict, Any, Optional, List
from config import settings
import json

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for WhatsApp Cloud API operations"""
    
    def __init__(self):
        self.access_token = settings.whatsapp_access_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.api_version = settings.whatsapp_api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_text_message(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send a text message via WhatsApp"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "messaging_product": "whatsapp",
                    "to": to_number,
                    "type": "text",
                    "text": {"body": message}
                }
                
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "message_id": data.get("messages", [{}])[0].get("id"),
                        "to": to_number
                    }
                else:
                    logger.error(f"WhatsApp send error: {response.status_code} - {response.text}")
                    return {"success": False, "error": response.text}
        except Exception as e:
            logger.error(f"WhatsApp send exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_document(self, to_number: str, document_url: str, filename: str, caption: str = "") -> Dict[str, Any]:
        """Send a document (PDF invoice) via WhatsApp"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "messaging_product": "whatsapp",
                    "to": to_number,
                    "type": "document",
                    "document": {
                        "link": document_url,
                        "filename": filename,
                        "caption": caption
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "message_id": data.get("messages", [{}])[0].get("id")
                    }
                else:
                    logger.error(f"WhatsApp document error: {response.status_code} - {response.text}")
                    return {"success": False, "error": response.text}
        except Exception as e:
            logger.error(f"WhatsApp document exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_interactive_buttons(self, to_number: str, body_text: str, buttons: List[Dict[str, str]], header: str = "") -> Dict[str, Any]:
        """Send interactive button message for HITL approval"""
        try:
            button_objects = []
            for idx, button in enumerate(buttons[:3]):  # Max 3 buttons
                button_objects.append({
                    "type": "reply",
                    "reply": {
                        "id": button.get("id", f"btn_{idx}"),
                        "title": button.get("title", f"Option {idx+1}")[:20]  # Max 20 chars
                    }
                })
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "messaging_product": "whatsapp",
                    "to": to_number,
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {"text": body_text},
                        "action": {"buttons": button_objects}
                    }
                }
                
                if header:
                    payload["interactive"]["header"] = {"type": "text", "text": header}
                
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "message_id": data.get("messages", [{}])[0].get("id")
                    }
                else:
                    logger.error(f"WhatsApp buttons error: {response.status_code} - {response.text}")
                    return {"success": False, "error": response.text}
        except Exception as e:
            logger.error(f"WhatsApp buttons exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_list_message(self, to_number: str, body_text: str, sections: List[Dict], button_text: str = "Options") -> Dict[str, Any]:
        """Send interactive list message"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "messaging_product": "whatsapp",
                    "to": to_number,
                    "type": "interactive",
                    "interactive": {
                        "type": "list",
                        "body": {"text": body_text},
                        "action": {
                            "button": button_text,
                            "sections": sections
                        }
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {"success": True, "message_id": data.get("messages", [{}])[0].get("id")}
                else:
                    return {"success": False, "error": response.text}
        except Exception as e:
            logger.error(f"WhatsApp list exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def download_media(self, media_id: str) -> Optional[bytes]:
        """Download media file (voice note, image) from WhatsApp"""
        try:
            # First, get the media URL
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"https://graph.facebook.com/{self.api_version}/{media_id}",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    logger.error(f"Media URL fetch error: {response.status_code}")
                    return None
                
                media_url = response.json().get("url")
                if not media_url:
                    return None
                
                # Download the actual media
                media_response = await client.get(
                    media_url,
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
                
                if media_response.status_code == 200:
                    return media_response.content
                else:
                    logger.error(f"Media download error: {media_response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Media download exception: {str(e)}")
            return None
    
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                payload = {
                    "messaging_product": "whatsapp",
                    "status": "read",
                    "message_id": message_id
                }
                
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    json=payload
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Mark as read exception: {str(e)}")
            return False

whatsapp_service = WhatsAppService()
