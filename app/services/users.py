from sqlalchemy.orm import Session
from app.schemas.users import UserUpdate
from app import models
from app.security import get_current_user, get_password_hash
from app.logger import get_logger
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

logger = get_logger(__name__)


class UserService:
    @staticmethod
    def update_user(
        db: Session,
        current_user: models.User,
        update_user: UserUpdate,
    ) -> models.User:
        if update_user.name:
            current_user.name = update_user.name
        if update_user.email:
            current_user.email = update_user.email
        if update_user.password:
            current_user.hashed_password = get_password_hash(update_user.password)
        
        db.add(current_user)
        db.flush()
        db.refresh(current_user)
        return current_user
        
        

