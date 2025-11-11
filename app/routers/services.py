from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models
from app.security import require_role
from app.services.services import client_services
from app.database import get_db
from app.schemas.services import ServiceBase, ServiceResponse, ServiceUpdate
from app.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(
    prefix="/services",
    tags=["services"],
)


@router.post("/", response_model=ServiceResponse, status_code=201)
def create_service(service_data: ServiceBase,
                   current_user: models.User = Depends(require_role("admin")),
                   db: Session = Depends(get_db)
):
    logger.info(f"Admin {current_user.email} attempting to create a new service")
    try:
        if not current_user:
            logger.warning("Unauthorized attempt to create service")
            raise HTTPException(status_code=403, detail="Unauthorized")
        new_service = client_services.create_service(db, service_data)
        db.commit()
        logger.info(f"Service created successfully: {new_service.title}")
        return new_service
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating service: {str(e)}")
        raise HTTPException(status_code=400, detail="Service creation failed")
    
@router.get("/{service_id}", response_model=ServiceResponse, status_code=200)
def get_service(service_id: str,
                db: Session = Depends(get_db)
):
    logger.info(f"Fetching service with ID: {service_id}")
    service = client_services.get_service_by_id(db, service_id)
    if not service:
        logger.warning(f"Service with ID {service_id} not found")
        raise HTTPException(status_code=404, detail="Service not found")
    logger.info(f"Service with ID {service_id} retrieved successfully")
    return service
        

@router.get("/", response_model = List[ServiceResponse])
def get_services(
    q: Optional[str] = Query(None, description="Search keyword for service title or description"),
    price_min: Optional[int] = Query(None, description="Minimum price filter"),
    price_max: Optional[int] = Query(None, description="Maximum price filter"),
    active: Optional[bool] = Query(None, description="Filter by active/inactive status"),
    db: Session = Depends(get_db),
):
    logger.info("Fetching services with filters - "
                f"q: {q}, price_min: {price_min}, price_max: {price_max}, active: {active}"
    )
    services = client_services.get_services(db, q, price_min, price_max, active)
    if not services:
        logger.warning("No services found matching the criteria")
        raise HTTPException(status_code=404, detail="No services found")
    logger.info(f"Retrieved {len(services)} services successfully")
    return services

@router.patch("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: str,
    service_update: ServiceUpdate,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    logger.info(f"Admin {current_user.email} attempting to update service with ID: {service_id}")
    try:
        existing_service = client_services.get_service_by_id(db, service_id)
        if not existing_service:
            logger.warning(f"Service with ID {service_id} not found for update")
            raise HTTPException(status_code=404, detail="Service not found")
        
        updated_service = client_services.update_service(db, existing_service, service_update)
        db.commit()
        logger.info(f"Service with ID {service_id} updated successfully")
        return updated_service
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating service with ID {service_id}: {str(e)}")
        raise HTTPException(status_code=400, detail="Service update failed")
    
@router.delete("/{service_id}", status_code=200)
def delete_service(
    service_id: str,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    logger.info(f"Admin {current_user.email} attempting to delete service with ID: {service_id}")
    try:
        existing_service = client_services.get_service_by_id(db, service_id)
        if not existing_service:
            logger.warning(f"Service with ID {service_id} not found for deletion")
            raise HTTPException(status_code=404, detail="Service not found")
        
        client_services.delete_service(db, existing_service)
        db.commit()
        logger.info(f"Service with ID {service_id} deleted successfully")
        return {"detail": f"Service with ID {service_id} deleted successfully"}
    
    except HTTPException as http_err:
        # Let FastAPI display the original message in Swagger
        logger.error(f"Error deleting booking: {http_err.detail}")
        raise http_err

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting service with ID {service_id}: {str(e)}")
        raise HTTPException(status_code=400, detail="Service deletion failed")