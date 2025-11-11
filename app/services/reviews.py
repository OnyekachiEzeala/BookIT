from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from app import models
from app.schemas.reviews import ReviewBase, ReviewUpdate, ReviewResponse
from app.models import Review


class ServiceReview:

    @staticmethod
    def create_review (db: Session, create_review: ReviewBase, current_user: models.User):
        #1. Ensure booking exist
        booking = db.query(models.Booking).filter(
            models.Booking.id == create_review.booking_id
        ).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        #2. Ensure booking belongs to the current user
        if booking.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only review your own bookings")
        
        # 3. Ensure the booking is completed
        if booking.status != "completed":
            raise HTTPException(status_code=400, detail="You can only review completed bookings")
        
        #4. Ensure the booking hasn't already been reviewed
        existing_review = db.query(Review).filter(
            Review.booking_id == booking.id
        ).first()
        if existing_review:
            raise HTTPException(status_code=400, detail="You have already reviewed this booking")
        
        review = models.Review(
            booking_id=create_review.booking_id,
            rating= create_review.rating,
            comment=create_review.comment
        )

        db.add(review)
        db.flush()
        db.refresh(review)
        return ReviewResponse.from_orm(review)

    @staticmethod
    def get_reviews (db: Session, service_id: str) -> List[models.Review]:
        service = db.query(models.Service).filter(models.Service.id == service_id).first()
        
        if not service:
            raise HTTPException(status_code=404, detail="Service ID not found")
        
        reviews = (
            db.query(models.Review)
            .join(models.Booking)
            .filter(models.Booking.service_id == service_id)
            .all()
        )
        return [ReviewResponse.from_orm(review) for review in reviews]
    
    @staticmethod
    def update_review (db: Session, review_id: str, update_data: ReviewUpdate, current_user_id: str):
        former_review = (
            db.query(models.Review)
            .options(joinedload(models.Review.booking))
            .filter(models.Review.id == review_id).
            first()
        )
        
        if not former_review:
            raise HTTPException(status_code=404, detail="Review not found")

        if not former_review.booking:
            raise HTTPException(status_code=400, detail="This review is not linked to any booking")
        
        if former_review.booking.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="You can only update your own reviews")
        
        if update_data.rating is not None:
            former_review.rating = update_data.rating
        if update_data.comment is not None:
            former_review.comment = update_data.comment

        db.add(former_review)
        db.flush()
        db.refresh(former_review)
        return former_review
    

    @staticmethod
    def delete_review_admin(db:Session, review_id: str):
        review = (
            db.query(models.Review)
            .options(joinedload(models.Review.booking))
            .filter(models.Review.id == review_id).
            first()
        )

        if not review: 
            raise HTTPException(status_code=404, detail="Review not found")
        
        if not review.booking:
            raise HTTPException(status_code=400, detail="This review is not linked to any booking")
        
        
        db.delete(review)
        db.flush()
        return


    @staticmethod
    def delete_review_user(db:Session, review_id: str, current_user_id: str):
        review = (
            db.query(models.Review)
            .options(joinedload(models.Review.booking))
            .filter(models.Review.id == review_id).
            first()
        )

        if not review: 
            raise HTTPException(status_code=404, detail="Review not found")
        
        if not review.booking:
            raise HTTPException(status_code=400, detail="This review is not linked to any booking")
        
        if review.booking.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="You can only delete your own reviews")
        
        db.delete(review)
        db.flush()
        return
      
client_reviews = ServiceReview()

