import json
from typing import Dict, List, Optional
from app.utils.logger import get_logger
from pydantic import BaseModel

logger = get_logger()
with open("app/data/inventory/stock-data.json", "r") as f:
    inventory = json.load(f)


class InventoryItem(BaseModel):
    """
    Pydantic model for inventory item with selected fields.
    """
    id: str
    name: str
    quantity_in_stock: int


def get_inventory(product_name: str) -> Optional[InventoryItem]:
    """
    Find an inventory item by product name and return a Pydantic model
    with id, name, and quantity_in_stock fields.
    
    Args:
        product_name: Name of the product to find
        
    Returns:
        InventoryItem model or None if product not found
    """
    logger.info(f"Getting inventory for product: {product_name}")
    
    # Search for the product in inventory_items list
    for item in inventory.get("inventory_items", []):
        if item.get("name") == product_name:
            # Create and return Pydantic model with requested fields
            return InventoryItem(
                id=item.get("id"),
                name=item.get("name"),
                quantity_in_stock=item.get("quantity_in_stock")
            )
    
    # If product not found
    logger.warning(f"Product not found: {product_name}")
    return None

