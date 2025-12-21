from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.api.v1 import deps

router = APIRouter()

@router.get("/me")
async def read_user_me(
    current_user: dict = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user profile.
    """
    print(f"Me Endpoint called for: {current_user.get('_id')}")
    return {
        "id": str(current_user["_id"]),
        "username": current_user.get("full_name") or current_user.get("email").split("@")[0],
        "email": current_user.get("email"),
        "target_role": current_user.get("target_role", "Backend"),
        "joined_at": str(current_user.get("_id").generation_time.date())
    }
