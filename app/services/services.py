from app.schemas.services import ServiceBase, ServiceResponse, ServiceUpdate
from sqlalchemy.orm import Session
from app import models
from sqlalchemy import or_ 
from typing import Optional, List

class Services:
    @staticmethod
    def create_service(db: Session, service_data: ServiceBase) -> ServiceResponse:
        new_service = models.Service(
            title=service_data.title,
            description=service_data.description,
            price=service_data.price,
            duration_minutes=service_data.duration_minutes,
            is_active=service_data.is_active
        )
        db.add(new_service)
        db.flush()
        db.refresh(new_service)
        return ServiceResponse.from_orm(new_service)
    
    @staticmethod
    def get_service_by_id(db: Session, service_id: str) -> models.Service:
        return db.query(models.Service).filter(models.Service.id == service_id).first()
    
    @staticmethod
    def get_services(db: Session,
                     q: Optional[str] = None,
                     price_min: Optional[int] = None,
                     price_max: Optional[int] = None,
                     is_active: Optional[bool] = None
    ) -> List[models.Service]:
        query = db.query(models.Service)

        if q:
            search = f"%{q}%"
            query = query.filter(
                or_(
                    models.Service.title.ilike(search),
                    models.Service.description.ilike(search)
                )
            )

        if price_min is not None:
            query = query.filter(models.Service.price >= price_min)

        if price_max is not None:
            query = query.filter(models.Service.price <= price_max)

        if is_active is not None:
            query = query.filter(models.Service.is_active == is_active)

        services = query.all()
        return [ServiceResponse.from_orm(s) for s in services]
    
    @staticmethod
    def update_service(db: Session, service_data: models.Service, updated_data: ServiceUpdate) -> models.Service:
        if updated_data.title is not None:
            service_data.title = updated_data.title
        if updated_data.description is not None:
            service_data.description = updated_data.description
        if updated_data.price is not None:
            service_data.price = updated_data.price
        if updated_data.duration_minutes is not None:
            service_data.duration_minutes = updated_data.duration_minutes
        if updated_data.is_active is not None:
            service_data.is_active = updated_data.is_active

        db.add(service_data)
        db.flush()
        db.refresh(service_data)

        return service_data

    @staticmethod
    def delete_service(db: Session, service_data: models.Service) -> None:
        db.delete(service_data)
        db.flush()
        return {"message": "Service deleted successfully"}

client_services = Services()
    

