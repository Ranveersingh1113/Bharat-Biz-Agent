import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BulkOrderItem:
    """Represents a single item in a bulk order"""
    quantity: float
    color: str
    fabric_type: str
    width: Optional[int] = None
    grade: Optional[str] = None

class BulkOrderParser:
    """Parse complex bulk orders in Hinglish format"""
    
    # Color mappings (Hindi to English)
    COLOR_MAP = {
        'laal': 'red', 'red': 'red',
        'neela': 'blue', 'blue': 'blue', 'nila': 'blue',
        'hara': 'green', 'green': 'green', 'hari': 'green',
        'peela': 'yellow', 'yellow': 'yellow', 'pili': 'yellow',
        'safed': 'white', 'white': 'white', 'sada': 'white',
        'kaala': 'black', 'black': 'black', 'kala': 'black',
        'gulabi': 'pink', 'pink': 'pink',
        'narangi': 'orange', 'orange': 'orange',
        'baigani': 'purple', 'purple': 'purple',
        'bhura': 'brown', 'brown': 'brown',
        'grey': 'grey', 'gray': 'gray', 'sleti': 'grey',
        'maroon': 'maroon', 'merun': 'maroon',
        'cream': 'cream', 'off-white': 'off-white',
        'golden': 'golden', 'sona': 'golden',
        'silver': 'silver', 'chandi': 'silver',
    }
    
    # Fabric mappings (Hindi to English)
    FABRIC_MAP = {
        'silk': 'silk', 'resham': 'silk', 'reshmi': 'silk',
        'cotton': 'cotton', 'kapas': 'cotton', 'suti': 'cotton',
        'polyester': 'polyester', 'poly': 'polyester',
        'linen': 'linen', 'lenin': 'linen',
        'wool': 'wool', 'oon': 'wool',
        'synthetic': 'synthetic', 'synth': 'synthetic',
        'chiffon': 'chiffon', 'shifon': 'chiffon',
        'georgette': 'georgette', 'jorjet': 'georgette',
        'crepe': 'crepe', 'krep': 'crepe',
        'velvet': 'velvet', 'makhmal': 'velvet',
        'satin': 'satin', 'setin': 'satin',
        'rayon': 'rayon', 'reyon': 'rayon',
    }
    
    def parse_bulk_order(self, text: str) -> Dict[str, Any]:
        """
        Parse bulk order text like:
        - "1000 meter chahiye - 400 red silk, 300 blue cotton, 300 green poly"
        - "500m - 200 laal resham 44\", 300 neela suti"
        - "1000m total: 40% red silk, 30% blue cotton, 30% green polyester"
        """
        result = {
            'success': False,
            'total_quantity': 0,
            'items': [],
            'raw_text': text
        }
        
        text_lower = text.lower()
        
        # Try to extract total quantity
        total_qty = self._extract_total_quantity(text_lower)
        result['total_quantity'] = total_qty
        
        # Split by common delimiters
        items = self._split_items(text_lower)
        
        parsed_items = []
        for item_text in items:
            parsed = self._parse_single_item(item_text, total_qty)
            if parsed:
                parsed_items.append(parsed)
        
        if parsed_items:
            result['success'] = True
            result['items'] = parsed_items
            
            # If we have percentage-based items, calculate quantities
            if total_qty > 0 and any(item.get('is_percentage') for item in parsed_items):
                for item in parsed_items:
                    if item.get('is_percentage'):
                        item['quantity'] = (item['percentage'] / 100) * total_qty
        
        return result
    
    def _extract_total_quantity(self, text: str) -> float:
        """Extract total quantity from text"""
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:meter|mtr|m)\s*(?:chahiye|total|ka order)',
            r'total\s*:?\s*(\d+(?:\.\d+)?)\s*(?:meter|mtr|m)?',
            r'^(\d+(?:\.\d+)?)\s*(?:meter|mtr|m)',
            r'(\d+(?:\.\d+)?)\s*(?:meter|mtr|m)\s*[-–]',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))
        
        return 0
    
    def _split_items(self, text: str) -> List[str]:
        """Split text into individual item descriptions"""
        # Remove total quantity prefix
        text = re.sub(r'^\d+\s*(?:meter|mtr|m)?\s*(?:chahiye|total|ka order)?\s*[-:–]?\s*', '', text)
        
        # Split by comma, 'aur', 'and', '+'
        items = re.split(r'[,;]|\s+aur\s+|\s+and\s+|\s*\+\s*', text)
        
        return [item.strip() for item in items if item.strip()]
    
    def _parse_single_item(self, text: str, total_qty: float = 0) -> Optional[Dict[str, Any]]:
        """Parse a single item like '400 red silk 44"' or '40% red silk'"""
        result = {}
        
        # Check for percentage
        pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
        if pct_match:
            result['percentage'] = float(pct_match.group(1))
            result['is_percentage'] = True
            result['quantity'] = (result['percentage'] / 100) * total_qty if total_qty > 0 else 0
        else:
            # Extract quantity
            qty_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:meter|mtr|m)?', text)
            if qty_match:
                result['quantity'] = float(qty_match.group(1))
                result['is_percentage'] = False
        
        if 'quantity' not in result and 'percentage' not in result:
            return None
        
        # Extract color
        for hindi, english in self.COLOR_MAP.items():
            if hindi in text:
                result['color'] = english
                break
        
        # Extract fabric type
        for hindi, english in self.FABRIC_MAP.items():
            if hindi in text:
                result['fabric_type'] = english
                break
        
        # Extract width (e.g., 44", 54 inch)
        width_match = re.search(r'(\d+)\s*(?:"|inch|in)', text)
        if width_match:
            result['width'] = int(width_match.group(1))
        
        # Extract grade (A, B, A+, etc.)
        grade_match = re.search(r'grade\s*([A-Za-z+]+)|\b([A-B]\+?)\b\s*grade', text)
        if grade_match:
            result['grade'] = grade_match.group(1) or grade_match.group(2)
        
        # Only return if we have at least color or fabric
        if 'color' in result or 'fabric_type' in result:
            result.setdefault('color', 'white')
            result.setdefault('fabric_type', 'cotton')
            result.setdefault('width', 44)
            return result
        
        return None
    
    def format_parsed_order(self, parsed: Dict[str, Any]) -> str:
        """Format parsed order for confirmation"""
        if not parsed.get('success') or not parsed.get('items'):
            return "Order samajh nahi aaya. Please format mein bhejiye:\n1000m - 400 red silk, 300 blue cotton"
        
        message = f"📦 *Bulk Order Summary*\n{'=' * 30}\n\n"
        message += f"📊 Total: {parsed['total_quantity']} meter\n\n"
        message += "*Items:*\n"
        
        total_calc = 0
        for idx, item in enumerate(parsed['items'], 1):
            qty = item.get('quantity', 0)
            total_calc += qty
            message += f"{idx}. {item.get('color', '').capitalize()} {item.get('fabric_type', '').capitalize()}"
            if item.get('width'):
                message += f" {item['width']}\""
            message += f" - {qty:.0f} mtr\n"
        
        message += f"\n{'=' * 30}\n"
        message += f"✅ Total calculated: {total_calc:.0f} meter\n"
        
        return message

bulk_order_parser = BulkOrderParser()
