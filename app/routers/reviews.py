from typing import List
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app import models
from app.services.reviews import client_reviews
from app.database import get_db
from app.schemas.reviews import ReviewBase, ReviewResponse, ReviewUpdate
from app.security import get_current_user, require_role
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)


@router.post("/", response_model=ReviewResponse, status_code=201)
def create_review(
    review_data: ReviewBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("user")),
):
    logger.info(f"User {current_user.email} attempting to drop a review")
    try:
        if not current_user:
            logger.warning("Unauthorized attempt to drop a review")
            raise HTTPException(status_code=403, detail="Unauthorized")
        new_review = client_reviews.create_review(db, review_data, current_user)
        db.commit()
        logger.info(f"Review creation was successful for user: {current_user.email}")
        return new_review
    
    except HTTPException as http_err:
        # Let FastAPI display the original message in Swagger
        logger.error(f"Error creating booking: {http_err.detail}")
        raise http_err

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(status_code=400, detail="Booking creation failed")


 
@router.get("/{service_id}", response_model=List[ReviewResponse], status_code=200)
def get_reviews(
    service_id: str,
    db: Session = Depends(get_db)
): 
    logger.info(f"Fetching reviews with service ID: {service_id}")
    try:
        review = client_reviews.get_reviews(db, service_id)
        if not review:
            logger.warning(f"Reviews for service with ID {service_id} not found")
            raise HTTPException(status_code=404, detail="Review not found")
        logger.info(f"Retrieved {len(review)} reviews successfully")
        return review
    
    except HTTPException as http_err:
        # Let FastAPI display the original message in Swagger
        logger.error(f"Error fetching reviews: {http_err.detail}")
        raise http_err

    except Exception as e:
        db.rollback()
        logger.error(f"Error fetching reviews for service {service_id}: {str(e)}")
        raise HTTPException(status_code=400, detail="Review retrival failed")
    
@router.patch("/{id}", response_model=ReviewResponse)
def get_update(
    review_id: str,
    update_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("user"))
):
    logger.info(f"User {current_user.email} attempting to update review {review_id}")
    try:
        updated_review = client_reviews.update_review(
            db,
            review_id,
            update_data,
            current_user.id
        )
        db.commit()
        logger.info(f"Review {review_id} updated successfully by {current_user.email}")
        return updated_review
    
    except HTTPException as http_err:
        # Let FastAPI display the original message in Swagger
        logger.error(f"Error fetching reviews: {http_err.detail}")
        raise http_err
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating review {review_id}: {e}")
        raise HTTPException(status_code=400, detail="Review update failed")
    
@router.delete("/{id}", status_code=200)
def delete_review(
    review_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "user"))
):
    logger.info(f"Attempting to delete booking with ID: {review_id}")
    try:
        if current_user.role == "admin":
            client_reviews.delete_review_admin(db, review_id)
            db.commit()
            logger.info(f"Review with ID {review_id} deleted successfully by admin {current_user.email}")
            return {"Message": f"Review with ID {review_id} deleted successfully"}
        
        if current_user.role == "user":
            client_reviews.delete_review_user(db, review_id, current_user.id)
            db.commit()
            logger.info(f"Review with ID {review_id} deleted successfully by user {current_user.email}")
            return {"Message": f"Review with ID {review_id} deleted successfully"}
        
    except HTTPException as http_err:
        # Let FastAPI display the original message in Swagger
        logger.error(f"Error deleting review: {http_err.detail}")
        raise http_err
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting review with ID {review_id}: {str(e)}")
        raise HTTPException(status_code=400, detail="Review deletion failed")
