from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db

router = APIRouter()

@router.get("/me")
async def read_user_me(
    db: Any = Depends(get_db)
) -> Any:
    """
    Get current user profile.
    For now, returns the last created user as a mock for 'current user'.
    """
    user = db.users.find_one(sort=[("_id", -1)])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user stats for joined date (approx) or use created_at if available
    # Assuming user doc has basic info.
    
    return {
        "username": user.get("full_name", "User"),
        "email": user.get("email"),
        "target_role": user.get("target_role", "Backend"),
        "joined_at": str(user.get("_id").generation_time.date()) # Extract date from ObjectId
    }
