from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from app import models
from sqlalchemy import or_, cast, String
from sqlalchemy.orm import Session
from app.schemas.bookings import BookingBase, BookingResponse, BookingUpdate
from app.models import Booking

class BookingService:
    @staticmethod
    def create_booking(db:Session, create_booking: BookingBase, user_id: str) -> BookingResponse:
        # check for Time validity
        if create_booking.end_time <= create_booking.start_time:
            raise HTTPException(status_code=400, detail="End time must be after start time")
        if create_booking.start_time < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Start time must be in the future")
        
        # check for service conflicts
        # validate service exists
        service = db.query(models.Service).filter(models.Service.id == create_booking.service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        service_status = db.query(models.Service).filter(
            models.Service.id == create_booking.service_id,
            models.Service.is_active == True
        ).first()
        if not service_status:
            raise HTTPException(status_code=409, detail="Service is not active")

        # check for service conflicts
        conflict = db.query(Booking).filter(
            Booking.service_id == create_booking.service_id,
            Booking.status.in_(['pending', 'confirmed']),
            Booking.start_time < create_booking.end_time,
            Booking.end_time > create_booking.start_time
        ).first()
        if conflict:
            raise HTTPException(status_code=409, detail="Service is already booked for the selected time slot")
        
        # check for user conflicts
        user_conflict = db.query(Booking).filter(
            Booking.user_id == user_id,
            Booking.status.in_(['pending', 'confirmed']),
            Booking.start_time < create_booking.end_time,
            Booking.end_time > create_booking.start_time
        ).first()
        if user_conflict:
            raise HTTPException(status_code=409, detail="You have another booking that conflicts with the selected time slot")
        
        booking_status = "pending" # Default status

        new_booking = models.Booking(
            user_id=create_booking.user_id,
            service_id=create_booking.service_id,
            start_time=create_booking.start_time,
            end_time=create_booking.end_time,
            status=booking_status
        )

        db.add(new_booking)
        db.flush()
        db.refresh(new_booking)
        return BookingResponse.from_orm(new_booking)
    
    @staticmethod
    def get_bookings_by_admin(db: Session,
                              q: Optional[str] = None,
                              status: Optional[str] = None,
                              start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None
        )-> List[models.Booking]:
        query = db.query(models.Booking)

        if q:
            search = f"%{q}%"
            query = query.join(models.User).join(models.Service).filter(
                or_(
                    cast(models.User.id, String).ilike(search),
                    models.User.email.ilike(search),
                    models.Service.title.ilike(search),
                    models.Service.description.ilike(search)
                )
            )

        if status is not None:
            query = query.filter(models.Booking.status == status)

        if start_time is not None:
            query = query.filter(models.Booking.start_time >= start_time)

        if end_time is not None:
            query = query.filter(models.Booking.end_time <= end_time)

        bookings = query.all()
        return [BookingResponse.from_orm(b) for b in bookings]
    
    @staticmethod
    def get_bookings_by_user(db: Session, user_id: str) -> List[models.Booking]:
        bookings = db.query(models.Booking).filter(models.Booking.user_id == user_id).all()
        return [BookingResponse.from_orm(b) for b in bookings]
    

    @staticmethod
    def get_booking_by_id(db: Session, booking_id: str) -> models.Booking:
        return db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    

    @staticmethod
    def update_booking_status_admin(db: Session,
                                    booking: models.Booking,
                                    booking_update: BookingUpdate
        ):
        if booking_update.status:
            booking.status = booking_update.status
        else: 
            raise HTTPException(status_code=400, detail="Status is required for admin update")

        db.add(booking)
        db.flush()
        db.refresh(booking)
        return booking
    
    @staticmethod
    def update_booking_status_user(db: Session,
                                   booking: models.Booking,
                                   booking_update: BookingUpdate
        ):

        if booking.status not in ["pending", "confirmed"]:
            raise HTTPException(status_code=400, detail="Only pending or confirmed bookings can be modified")
        
        # if booking_update.status is pending or cancelled
        if booking_update.status == "pending":
            booking.status = booking_update.status
        if booking_update.status == "cancelled":
            booking.status = booking_update.status
        if booking_update.status is None:
            booking.status = booking.status
        else:
            raise HTTPException(status_code=403, detail="Users can only cancel their bookings")

            # Users can reschedule their bookings
        if booking_update.start_time and booking_update.end_time:
            # check for Time validity
            if booking_update.end_time <= booking_update.start_time:
                raise HTTPException(status_code=409, detail="End time must be after start time")
            if booking_update.start_time < datetime.now(timezone.utc):
                raise HTTPException(status_code=409, detail="Start time must be in the future")
            
            # check for service conflicts
            conflict = db.query(Booking).filter(
                Booking.service_id == booking.service_id,
                Booking.id != booking.id,  # Exclude current booking
                Booking.status.in_(['pending', 'confirmed']),
                Booking.start_time < booking_update.end_time,
                Booking.end_time > booking_update.start_time
            ).first()
            if conflict:
                raise HTTPException(status_code=409, detail="Service is already booked for the selected time slot")
            
            # check for user conflicts
            user_conflict = db.query(Booking).filter(
                Booking.user_id == booking.user_id,
                Booking.id != booking.id,  # Exclude current booking
                Booking.status.in_(['pending', 'confirmed']),
                Booking.start_time < booking_update.end_time,
                Booking.end_time > booking_update.start_time
            ).first()
            if user_conflict:
                raise HTTPException(status_code=409, detail="You have another booking that conflicts with the selected time slot")
            
            booking.start_time = booking_update.start_time
            booking.end_time = booking_update.end_time

        db.add(booking)
        db.flush()
        db.refresh(booking)
        return booking
    
    @staticmethod
    def delete_booking_admin(db: Session, booking: models.Booking):
        db.delete(booking)
        db.flush()
        return
    
    @staticmethod
    def delete_booking_user(db: Session, booking: models.Booking):
        if booking.start_time > datetime.now(timezone.utc):
            db.delete(booking)
            db.flush()
            return
        else:
            raise HTTPException(status_code=400, detail="Cannot delete past or ongoing bookings")
       

       
client_bookings = BookingService()   