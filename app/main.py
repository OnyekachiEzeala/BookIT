from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.logger import get_logger
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.services import router as services_router
from app.routers.bookings import router as bookings_router
from app.routers.reviews import router as review_router

logger = get_logger(__name__)

app = FastAPI(
    title="BookIT API",
    description="A secure Booking platform API with JWT authentication and rate limiting",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed"),
    return {"message": "Welcome to the BookIT API"}

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(services_router)
app.include_router(bookings_router)
app.include_router(review_router)
