from typing import Annotated
from app import models
from app.logger import get_logger
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from app.schemas.users import UserCreate, UserResponse, Token, UserLogin, TokenPair
from app.services.auth import AuthService
from app.database import get_db
from app.security import get_current_user


logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

@router.post("/register", response_model=UserResponse, status_code=201)
def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to register user with email: {user_create.email}")
    try:
        new_user = AuthService.create_user(db, user_create)
        if not new_user:
            logger.warning(f"Registration failed: User with email {user_create.email} already exists.")
            # Return the exact message requested when email already exists
            raise HTTPException(status_code=400, detail="User already exist")
        db.commit()
        logger.info(f"User registered successfully with email: {new_user.email}")
        return new_user
    except HTTPException:
        # re-raise known HTTP exceptions (like the "User already exist" above)
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error during user registration: {str(e)}")
        raise HTTPException(status_code=400, detail="Registration failed")
    

@router.post("/login", response_model=TokenPair)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"User login attempt: {user.email}")
    access_token = AuthService.login_user(db, user)
    refresh_token = AuthService.refresh_token(db, user)
    if not access_token:
        logger.warning(f"Login failed for email: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    logger.info(f"User logged in successfully with email: {user.email}")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@router.post("/refresh", response_model=Token)
def refresh_token(x_refresh_token: str = Header(...)):
    """
    Endpoint to refresh an expired access token using a valid refresh token.
    """
    logger.info("Refresh token attempt")
    new_access_token = AuthService.refresh_access_token(x_refresh_token)
    if not new_access_token:
        logger.warning("Refresh token failed")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    logger.info("Access token refreshed successfully")
    return {"access_token": new_access_token, "token_type": "bearer"}

