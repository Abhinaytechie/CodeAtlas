from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.database import get_db
from datetime import datetime
from bson import ObjectId
from app.api.v1 import deps

router = APIRouter()

@router.get("/items")
def get_vault_items(
    db: Any = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user)
) -> Any:
    """
    Get all proof items for the current user.
    """
    user_id = str(current_user["_id"])
    
    cursor = db.vault_items.find({"user_id": user_id}).sort("created_at", -1)
    items = []
    for item in cursor:
        item["_id"] = str(item["_id"])
        items.append(item)
    return items

@router.post("/items")
def create_vault_item(
    item: dict = Body(...),
    db: Any = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user)
) -> Any:
    """
    Add a new proof item to the vault.
    """
    user_id = str(current_user["_id"])
    
    new_item = {
        "user_id": user_id,
        "title": item.get("title", "Untitled Proof"),
        "description": item.get("description", ""),
        "type": item.get("type", "link"), # link, github, file
        "url": item.get("url", ""),
        "tags": item.get("tags", []),
        "created_at": datetime.utcnow()
    }
    
    result = db.vault_items.insert_one(new_item)
    new_item["_id"] = str(result.inserted_id)
    return new_item

@router.delete("/items/{item_id}")
def delete_vault_item(
    item_id: str,
    db: Any = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user)
) -> Any:
    """
    Remove a proof item.
    """
    user_id = str(current_user["_id"])

    result = db.vault_items.delete_one({"_id": ObjectId(item_id), "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
        
    return {"status": "success"}
