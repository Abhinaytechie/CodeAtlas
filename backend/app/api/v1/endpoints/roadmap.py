from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Body, Header
from app.core import security
from app.api.v1.endpoints.dashboard import get_user_stats
from app.core.database import get_db
from app.services.ai_roadmap import ai_service
from datetime import datetime
from app.api.v1 import deps

router = APIRouter()

@router.get("/latest")
async def get_latest_roadmap(
    db: Any = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user)
) -> Any:
    print("DEBUG: Endpoint /latest hit. Fetching from DB.")
    user_id = str(current_user["_id"])
        
    latest = db.roadmaps.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )
    
    if not latest:
        raise HTTPException(status_code=404, detail="No roadmap found")
        
    latest["_id"] = str(latest["_id"])
    result = latest["roadmap"]
    result["_id"] = latest["_id"]
    result["is_bookmarked"] = latest.get("is_bookmarked", False)
    return result

@router.get("/")
async def get_all_roadmaps(
    db: Any = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user)
) -> Any:
    """
    List all roadmaps for the current user.
    """
    user_id = str(current_user["_id"])
    
    cursor = db.roadmaps.find({"user_id": user_id}).sort("created_at", -1)
    roadmaps = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        # Return summary info only
        roadmaps.append({
            "id": doc["_id"],
            "role": doc.get("role", "Unknown"),
            "days": doc.get("days", 0),
            "created_at": doc.get("created_at"),
            "title": doc["roadmap"].get("title", "Untitled Roadmap"),
            "total_patterns": len(doc["roadmap"].get("patterns", [])),
            "is_bookmarked": doc.get("is_bookmarked", False)
        })
    return roadmaps

@router.get("/{roadmap_id}")
async def get_roadmap_by_id(
    roadmap_id: str,
    db: Any = Depends(get_db)
) -> Any:
    """
    Get a specific roadmap by ID.
    """
    from bson.objectid import ObjectId
    try:
        oid = ObjectId(roadmap_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    doc = db.roadmaps.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Roadmap not found")
        
    doc["_id"] = str(doc["_id"])
    result = doc["roadmap"]
    result["_id"] = doc["_id"] # Ensure ID is at root
    result["is_bookmarked"] = doc.get("is_bookmarked", False)
    return result

@router.put("/{roadmap_id}/bookmark")
async def toggle_bookmark(
    roadmap_id: str,
    db: Any = Depends(get_db)
) -> Any:
    """
    Toggle bookmark status.
    """
    from bson.objectid import ObjectId
    try:
        oid = ObjectId(roadmap_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")
        
    doc = db.roadmaps.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Roadmap not found")
        
    new_status = not doc.get("is_bookmarked", False)
    db.roadmaps.update_one(
        {"_id": oid},
        {"$set": {"is_bookmarked": new_status}}
    )
    return {"status": "success", "is_bookmarked": new_status}

from fastapi import APIRouter, Depends, HTTPException, Body, Header, Request

@router.post("/generate")
async def generate_roadmap(
    request: Request,
    body: dict = Body(...),
    x_groq_api_key: str | None = Header(default=None, alias="x-groq-api-key"),
    db: Any = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user)
) -> Any:
    print("DEBUG: All Headers:", request.headers)
    
    try:
        """
        Generates or retrieves a personalized NeetCode-style roadmap.
        1. Checks DB for existing roadmap for this user + role.
        2. If not found, calls AI Service.
        3. Persists result to DB.
        """
        
        # Extract Params
        target_role = body.get("target_role", "Backend")
        days_remaining = body.get("days_remaining", 45)
        weak_patterns = body.get("weak_patterns", [])
        force_regenerate = body.get("force_regenerate", False)
        
        # 0. Get User
        user_id = str(current_user["_id"])

        print(f"DEBUG: Endpoint /generate hit. Params: role={target_role}, force={force_regenerate}")
        print(f"DEBUG: x_groq_api_key received: {'YES' if x_groq_api_key else 'NO'} (Value: {x_groq_api_key[:5] + '...' if x_groq_api_key else 'None'})")

        # 1. Check Cache (Disabled for debugging)
        # if not force_regenerate:
        #     existing_roadmap = db.roadmaps.find_one({
        #         "user_id": user_id,
        #         "target_role": target_role
        #     })
            
        #     if existing_roadmap:
        #         print("DEBUG: Returning Cached Roadmap (AI Skipped)")
        #         # Return cached roadmap (excluding _id)
        #         existing_roadmap["_id"] = str(existing_roadmap["_id"])
        #         return existing_roadmap

        # 2. Generate via AI Service (Passing Groq Key)
        roadmap_data = await ai_service.generate_roadmap(target_role, days_remaining, weak_patterns, api_key=x_groq_api_key)
        
        # 3. Persist to DB
        roadmap_doc = {
            "user_id": user_id,
            "target_role": target_role,
            "days_remaining": days_remaining,
            "created_at": datetime.utcnow(),
            "roadmap": roadmap_data, # Store the whole JSON structure
            # Flattened fields for easy access if needed
            "title": roadmap_data["title"]
        }
        
        # Upsert (Replace if exists for this role, or insert new)
        db.roadmaps.update_one(
            {"user_id": user_id, "target_role": target_role},
            {"$set": roadmap_doc},
            upsert=True
        )
        
        # Return the FULL roadmap structure so frontend can render immediately
        # Also include the DB ID for reference/bookmarking
        final_doc = db.roadmaps.find_one({"user_id": user_id, "target_role": target_role})
        roadmap_data["_id"] = str(final_doc["_id"])
        roadmap_data["is_bookmarked"] = final_doc.get("is_bookmarked", False)
        return roadmap_data
    except Exception as e:
        import traceback
        print(f"ERROR IN GENERATE ROADMAP: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup")
async def cleanup_non_bookmarked(
    db: Any = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user)
) -> Any:
    """
    Delete all roadmaps for user that are NOT bookmarked.
    Called on SignOut.
    """
    # 0. Get User
    user_id = str(current_user["_id"])
    
    # Delete where is_bookmarked is not true
    result = db.roadmaps.delete_many({
        "user_id": user_id,
        "is_bookmarked": {"$ne": True}
    })
    
    return {"deleted_count": result.deleted_count}
