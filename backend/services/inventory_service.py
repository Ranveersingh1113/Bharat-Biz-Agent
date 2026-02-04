import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from models import InventoryItem, FabricType
import uuid

logger = logging.getLogger(__name__)

class InventoryService:
    """Service for textile inventory management with variant tracking"""
    
    def __init__(self, db=None):
        self.db = db
    
    def set_db(self, db):
        self.db = db
    
    async def get_item_by_variant(
        self,
        fabric_type: Optional[str] = None,
        color: Optional[str] = None,
        width: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Find inventory item by variant attributes"""
        if self.db is None:
            return None
        
        query = {}
        if fabric_type:
            query["fabric_type"] = fabric_type.lower()
        if color:
            query["color"] = color.lower()
        if width:
            query["width"] = width
        
        item = await self.db.inventory.find_one(query, {"_id": 0})
        return item
    
    async def check_availability(
        self,
        fabric_type: Optional[str] = None,
        color: Optional[str] = None,
        quantity_needed: float = 0
    ) -> Dict[str, Any]:
        """Check if required quantity is available"""
        item = await self.get_item_by_variant(fabric_type, color)
        
        if not item:
            return {
                "available": False,
                "message": f"{color or ''} {fabric_type or 'item'} not found in inventory",
                "current_stock": 0
            }
        
        current_qty = item.get("quantity", 0)
        available = current_qty >= quantity_needed
        
        return {
            "available": available,
            "item": item,
            "current_stock": current_qty,
            "requested": quantity_needed,
            "shortage": max(0, quantity_needed - current_qty) if not available else 0,
            "message": f"{current_qty} {item.get('unit', 'meter')} available" if available else f"Only {current_qty} available, need {quantity_needed}"
        }
    
    async def get_low_stock_items(self, threshold_multiplier: float = 1.0) -> List[Dict[str, Any]]:
        """Get items below reorder level"""
        if not self.db:
            return []
        
        pipeline = [
            {
                "$match": {
                    "$expr": {
                        "$lte": ["$quantity", {"$multiply": ["$reorder_level", threshold_multiplier]}]
                    }
                }
            },
            {"$project": {"_id": 0}}
        ]
        
        items = await self.db.inventory.aggregate(pipeline).to_list(100)
        return items
    
    async def update_stock(
        self,
        item_id: str,
        quantity_change: float,
        operation: str = "subtract"  # "add" or "subtract"
    ) -> Dict[str, Any]:
        """Update stock quantity after sale or restock"""
        if not self.db:
            return {"success": False, "error": "Database not connected"}
        
        update_value = quantity_change if operation == "add" else -quantity_change
        
        result = await self.db.inventory.update_one(
            {"id": item_id},
            {
                "$inc": {"quantity": update_value},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        if result.modified_count > 0:
            updated_item = await self.db.inventory.find_one({"id": item_id}, {"_id": 0})
            return {"success": True, "item": updated_item}
        return {"success": False, "error": "Item not found"}
    
    async def record_wastage(
        self,
        item_id: str,
        wastage_qty: float,
        reason: str = "cutting_loss"
    ) -> Dict[str, Any]:
        """Record fabric wastage"""
        if not self.db:
            return {"success": False, "error": "Database not connected"}
        
        # Update inventory
        await self.update_stock(item_id, wastage_qty, "subtract")
        
        # Record wastage log
        wastage_log = {
            "id": str(uuid.uuid4()),
            "item_id": item_id,
            "quantity": wastage_qty,
            "reason": reason,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.wastage_logs.insert_one(wastage_log)
        
        return {"success": True, "wastage_log": wastage_log}
    
    async def get_inventory_summary(self) -> Dict[str, Any]:
        """Get summary of inventory by fabric type"""
        if not self.db:
            return {}
        
        pipeline = [
            {
                "$group": {
                    "_id": "$fabric_type",
                    "total_quantity": {"$sum": "$quantity"},
                    "total_value": {"$sum": {"$multiply": ["$quantity", "$rate_per_unit"]}},
                    "item_count": {"$sum": 1}
                }
            }
        ]
        
        summary = await self.db.inventory.aggregate(pipeline).to_list(100)
        return {
            "by_fabric": summary,
            "total_items": sum(s["item_count"] for s in summary),
            "total_value": sum(s["total_value"] for s in summary)
        }
    
    def format_stock_message(self, items: List[Dict[str, Any]]) -> str:
        """Format inventory items as WhatsApp message"""
        if not items:
            return "📦 No items found matching your criteria."
        
        message = "📦 *Inventory Status*\n" + "=" * 25 + "\n\n"
        
        for item in items:
            status_emoji = "✅" if item.get("quantity", 0) > item.get("reorder_level", 50) else "⚠️"
            message += f"{status_emoji} *{item.get('name', 'Item')}*\n"
            message += f"   {item.get('color', '')} {item.get('fabric_type', '')} {item.get('width', '')}\"\n"
            message += f"   Stock: {item.get('quantity', 0)} {item.get('unit', 'mtr')}\n"
            message += f"   Rate: ₹{item.get('rate_per_unit', 0)}/mtr\n\n"
        
        return message.strip()
    
    def format_low_stock_alert(self, items: List[Dict[str, Any]]) -> str:
        """Format low stock alert message"""
        if not items:
            return "✅ All items are well-stocked!"
        
        message = "⚠️ *LOW STOCK ALERT*\n" + "=" * 25 + "\n\n"
        
        for item in items:
            message += f"🔴 *{item.get('name', 'Item')}*\n"
            message += f"   Current: {item.get('quantity', 0)} {item.get('unit', 'mtr')}\n"
            message += f"   Reorder Level: {item.get('reorder_level', 50)} {item.get('unit', 'mtr')}\n"
            message += f"   Suggested Order: {item.get('reorder_level', 50) * 2} {item.get('unit', 'mtr')}\n\n"
        
        return message.strip()

inventory_service = InventoryService()
