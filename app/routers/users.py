from typing import Annotated
from app import models
from fastapi import Depends, APIRouter, HTTPException
from app.schemas.users import UserUpdate, UserResponse
from app.security import get_current_user
from app.logger import get_logger
from app.database import get_db
from app.services.users import UserService
from sqlalchemy.orm import Session



logger = get_logger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: Annotated[models.User, Depends(get_current_user)]
):
    return current_user

@router.patch("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user : Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    try:
        updated_user = UserService.update_user(db, current_user, user_update)
        db.commit()
        logger.info(f"User updated successfully: {updated_user.email}")
        return updated_user
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user {current_user.email}: {str(e)}")
        raise HTTPException(status_code=400, detail="Update failed")