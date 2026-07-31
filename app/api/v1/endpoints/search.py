from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.search_service import search_service

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/")
def global_search(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return search_service.search_all(db, q, limit)

@router.get("/patients")
def search_patients(
    q: str = Query(..., min_length=2),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return search_service.search_patients(db, q, limit)

@router.get("/medicines")
def search_medicines(
    q: str = Query(..., min_length=2),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return search_service.search_medicines(db, q, limit)
