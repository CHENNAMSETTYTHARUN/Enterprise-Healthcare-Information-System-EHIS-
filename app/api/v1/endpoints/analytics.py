from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.rbac import require_roles
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.analytics_service import analytics_service
from app.schemas.analytics import DashboardStatsResponse, RevenueAnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["Dashboard & Analytics"])

@router.get("/dashboard", response_model=DashboardStatsResponse)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return analytics_service.get_dashboard_stats(db)

@router.get("/revenue", response_model=RevenueAnalyticsResponse)
def get_revenue_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return analytics_service.get_revenue_analytics(db)

@router.get("/patient-trends")
def get_patient_trends(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return analytics_service.get_patient_trends(db, days)

@router.get("/department-occupancy")
def get_department_occupancy(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return analytics_service.get_department_occupancy(db)
