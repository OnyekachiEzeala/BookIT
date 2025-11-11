import ulid
from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(ulid.new()))
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    created_at = Column(
        DateTime(timezone = True), nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )
    
    bookings = relationship("Booking", back_populates="customer")

class Service(Base):
    __tablename__ = "services"

    id = Column(String, primary_key=True, index=True, default=lambda: str(ulid.new()))
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime(timezone = True), nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )

    orders = relationship("Booking", back_populates="service")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, index=True, default=lambda: str(ulid.new()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    service_id = Column(String, ForeignKey("services.id"), nullable=False)
    start_time = Column(DateTime(timezone = True), nullable=False)
    end_time = Column(DateTime(timezone = True), nullable=False)
    status = Column(String, default="pending")
    created_at = Column(
        DateTime(timezone = True), nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )

    customer = relationship("User", back_populates="bookings")
    service = relationship("Service", back_populates="orders")
    review = relationship("Review", back_populates="booking")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, index=True, default=lambda: str(ulid.new()))
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone = True), nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )

    booking = relationship("Booking", back_populates="review")
