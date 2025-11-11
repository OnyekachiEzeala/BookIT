from typing import List, Optional
from fastapi import HTTPException, Depends, status, APIRouter, Query
from datetime import datetime
from sqlalchemy.orm import Session
from app import models
from app.services.bookings import client_bookings
from app.database import get_db
from app.schemas.bookings import BookingBase, BookingCreate, BookingResponse, BookingUpdate
from app.security import get_current_user, require_role
from app.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)

@router.post("/", response_model=BookingResponse, status_code=201)
def create_booking(
    booking_data: BookingBase,
    current_user: models.User = Depends(require_role("user")),
    db: Session = Depends(get_db)
):
    logger.info(f"User {current_user.email} attempting to create a new booking")
    try:
        if not current_user:
            logger.warning("Unauthorized attempt to create booking")
            raise HTTPException(status_code=403, detail="Unauthorized")
        new_booking = client_bookings.create_booking(db, booking_data, current_user.id)
        db.commit()
        logger.info(f"Booking created successfully for user: {current_user.email}")
        return new_booking
    
    except HTTPException as http_err:
        # Let FastAPI display the original message in Swagger
        logger.error(f"Error creating booking: {http_err.detail}")
        raise http_err

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(status_code=400, detail="Booking creation failed")
    

@router.get("/", response_model=List[BookingResponse], status_code=200)
def get_bookings(
    q: Optional[str] = Query(None, description="Search by user email or service title"),
    status: Optional[str] = Query(None, description="Filter by booking status"),
    start_time: Optional[datetime] = Query(None, description="Filter bookings starting after this time"),
    end_time: Optional[datetime] = Query(None, description="Filter bookings ending before this time"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "user"))  # Both roles allowed
):
    """
    Get bookings.
    - If the logged-in user is an admin → return all bookings with filters.
    - If the logged-in user is a regular user → return only their own bookings.
    """
    try:
        #If Admin: fetch all bookings with optional filters
        if current_user.role == "admin":
            logger.info(f"Admin {current_user.email} fetching all bookings")
            bookings = client_bookings.get_bookings_by_admin(
                db=db,
                q=q,
                status=status,
                start_time=start_time,
                end_time=end_time
            )

        # If Regular User: fetch only their own bookings
        else:
            logger.info(f"User {current_user.email} fetching their bookings")
            bookings = client_bookings.get_bookings_by_user(
                db=db,
                user_id=current_user.id
            )

        return bookings

    except Exception as e:
        logger.error(f"Error fetching bookings: {str(e)}")
        raise HTTPException(status_code=400, detail="Error fetching bookings")
    
@router.get("/{booking_id}", response_model=BookingResponse, status_code=200)
def get_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "user"))  # Both roles allowed
):
    """
    Get a specific booking by ID.
    - Admins can access any booking.
    - Regular users can only access their own bookings.
    """
    logger.info("fetching booking with ID: {booking_id}")
    booking = client_bookings.get_booking_by_id(db, booking_id)
    if not booking:
        logger.warning(f"Booking with ID {booking_id} not found")
        raise HTTPException(status_code=404, detail="Booking not found")
    
    #If Regular User: ensure they own the booking
    if current_user.role == "user" and booking.user_id != current_user.id:
        logger.warning(f"User {current_user.email} unauthorized to access booking ID {booking_id}")
        raise HTTPException(status_code=403, detail="Unauthorized to access this booking")
    
    logger.info(f"Booking with ID {booking_id} retrieved successfully")
    return booking

@router.patch("/{booking_id}", response_model=BookingResponse)
def update_booking_status(
    booking_id: str,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "user"))  # Both roles allowed
):
    """
    Update booking status.
    - Admins can update any booking's status.
    - owner can only reshedule or cancle if pending or confirmed.
    """
    logger.info(f"Attempting to update booking with ID: {booking_id}")
    try:
        existing_booking = client_bookings.get_booking_by_id(db, booking_id)
        if not existing_booking:
            logger.warning(f"Booking with ID {booking_id} not found for update")
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # if current_user.role == "admin":
        if current_user.role == "admin":
            updated_booking = client_bookings.update_booking_status_admin(
                db,
                existing_booking,
                booking_update
            )
            db.commit()
            logger.info(f"Admin {current_user.email} updated booking ID {booking_id} successfully")
            return updated_booking
        
        # if current_user.role == "user":
        #  Validate that it is the owner trying to make the update
        if current_user.role == "user" and existing_booking.user_id != current_user.id:
            logger.warning(f"User {current_user.email} unauthorized to update booking ID {booking_id}")
            raise HTTPException(status_code=403, detail="Unauthorized to update this booking")
        updated_booking = client_bookings.update_booking_status_user(
            db=db,
            booking=existing_booking,
            booking_update=booking_update
        )
        db.commit()
        logger.info(f"User {current_user.email} updated booking ID {booking_id} successfully")
        return updated_booking
    
    except HTTPException as http_err:
        # Let FastAPI display the original message in Swagger
        logger.error(f"Error creating booking: {http_err.detail}")
        raise http_err
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating booking: {str(e)}")
        raise HTTPException(status_code=400, detail="Booking update failed")
    

@router.delete("/{booking_id}", status_code=200)
def delete_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "user"))
):
    logger.info(f"Attempting to delete booking with ID: {booking_id}")
    try:
        existing_booking = client_bookings.get_booking_by_id(db, booking_id)
        if not existing_booking:
            logger.warning(f"Booking with ID {booking_id} not found for deletion")
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # if current_user.role == "admin"
        if current_user.role == "admin":
            client_bookings.delete_booking_admin(db, existing_booking)
            db.commit()
            logger.info(f"Booking with ID {booking_id} deleted successfully by admin {current_user.email}")
            return {"Message": f"Booking with ID {booking_id} deleted successfully"}
        
        # if current_user.role == "user"
        # Validating that it is the owner trying to delete
        if current_user.role == "user" and existing_booking.user_id != current_user.id:
            logger.warning(f"User {current_user.email} unauthorized to delete booking ID {booking_id}")
            raise HTTPException(status_code=403, detail="Unauthorized to delete this booking")
        client_bookings.delete_booking_user(db, existing_booking)
        db.commit()
        logger.info(f"Booking with ID  {booking_id} deleted successfully by user {current_user.email}")
        return {"Message": f"Booking with ID {booking_id} deleted successfully"}

        
    except HTTPException as http_err:
        # Let FastAPI display the original message in Swagger
        logger.error(f"Error deleting booking: {http_err.detail}")
        raise http_err
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting booking with ID {booking_id}: {str(e)}")
        raise HTTPException(status_code=400, detail="Booking deletion failed")
        
        

        
    


    
