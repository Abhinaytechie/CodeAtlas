from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import security
# from app.models.user import User as UserModel
from app import schemas

router = APIRouter()

import logging
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/signup", response_model=schemas.User)
def create_user(
    *,
    db: Any = Depends(get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """
    logger.info(f"Received signup request for: {user_in.email}")
    try:
        # Check if user exists
        existing_user = db.users.find_one({"email": user_in.email})
        if existing_user:
            logger.warning(f"User already exists: {user_in.email}")
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )
        
        user_dict = user_in.dict()
        user_dict["hashed_password"] = security.get_password_hash(user_in.password)
        del user_dict["password"]
        user_dict["target_role"] = user_in.target_role or "Backend" # default
        
        logger.info(f"Inserting user into MongoDB: {user_in.email}")
        result = db.users.insert_one(user_dict)
        logger.info(f"User inserted with ID: {result.inserted_id}")
        
        # Initialize User Stats
        db.user_stats.insert_one({
            "user_id": str(result.inserted_id),
            "solved_count": 0,
            "total_questions": 150, # Arbitrary goal
            "streak": 0,
            "weak_patterns": [],
            "solved_problems": [], # List of problem IDs
            "streak_dates": [] # List of ISO date strings
        })
        
        # Return User schema
        return {**user_dict, "id": str(result.inserted_id)}

    except HTTPException as he:
        # Re-raise HTTP exceptions (like 400)
        raise he
    except Exception as e:
        logger.error(f"CRITICAL ERROR during signup: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )

@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Any = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.users.find_one({"email": form_data.username})
    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=60)
    return {
        "access_token": security.create_access_token(
            str(user["_id"]), expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
