from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.alert import AlertRead
from app.services.alert_service import AlertService

router = APIRouter()


@router.get("", response_model=list[AlertRead])
def list_alerts(limit: int = 50, db: Session = Depends(get_db)) -> list[AlertRead]:
    return AlertService(db).list_alerts(limit=limit)
