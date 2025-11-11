from datetime import timedelta
from typing import List
from app.logger import get_logger
from sqlalchemy.orm import Session
from app.schemas.users import UserCreate, UserLogin, UserResponse
from app import models
from app.security import create_access_token,  create_refresh_token, get_password_hash, authenticate_user
from jose import jwt, JWTError
from fastapi import Header, HTTPException, Depends
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

logger = get_logger(__name__)


class AuthService:
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> UserResponse:
        # check if the user already exists
        db_user = (
            db.query(models.User)
            .filter(models.User.email == user_create.email)
            .first()
        )
        if db_user:
            return None  # User already exists
        
        # hash the password
        hashed_password = get_password_hash(user_create.password)
        new_user = models.User(
            name=user_create.name,
            email=user_create.email,
            hashed_password=hashed_password,
            role=user_create.role.value
        )
        db.add(new_user)
        db.flush()
        db.refresh(new_user)
        return UserResponse.from_orm(new_user)
    
    @staticmethod
    def login_user(db: Session, user=UserLogin):
        db_user = authenticate_user(user.email, user.password, db)
        if not db_user:
            logger.warning(f"Invalid login attempt for email: {user.email}")
            return None
        access_token = create_access_token(
            sub=db_user.email, roles=db_user.role
        )
        return access_token
    
    @staticmethod
    def refresh_token(db: Session, user=UserLogin):
        db_user = authenticate_user(user.email, user.password, db)
        if not db_user:
            logger.warning(f"Refresh token request for unknown email: {user.email}")
            return None
        user_role = db_user.role
        refresh = create_refresh_token(sub=db_user.email, roles=user_role)
        return refresh
    

    @staticmethod 
    def refresh_access_token(x_refresh_token: str = Header(...)):

        try:
            payload = jwt.decode(
                x_refresh_token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
            )

            # Ensure this is indeed a refresh token
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Not a refresh token")

            sub = payload.get("sub")
            role = payload.get("role")

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        new_access = create_access_token(sub=sub, roles=role)

        return new_access




