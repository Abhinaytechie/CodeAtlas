from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from app.core import security
from app.core.config import settings
from app.core.database import get_db
from bson.objectid import ObjectId

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)

def get_current_user(
    db = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data_sub = payload.get("sub")
        if token_data_sub is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except (JWTError, ValidationError) as e:
        print(f"Auth Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    try:
        user_id = ObjectId(token_data_sub)
    except:
        print(f"Invalid ObjectId: {token_data_sub}")
        raise HTTPException(status_code=400, detail="Invalid user ID in token")
        
    user = db.users.find_one({"_id": user_id})
    if not user:
        print(f"User not found for ID: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
        
    return user

