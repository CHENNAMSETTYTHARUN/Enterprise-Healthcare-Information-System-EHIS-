from typing import Dict, Any, List
from pydantic import BaseModel

class DashboardStatsResponse(BaseModel):
    total_patients: int
    total_doctors: int
    total_appointments_today: int
    active_emergencies: int
    total_revenue_month: float
    occupied_beds: int
    available_beds: int
    total_lab_orders: int
    total_opd_visits: int
    total_ipd_admissions: int
    medicines_expiring_soon: int

class RevenueAnalyticsResponse(BaseModel):
    total_billed: float
    total_collected: float
    outstanding_balance: float
    claims_pending_approval: int
    total_tax_collected: float
    total_discounts_given: float
    insurance_recovered: float
    total_refunds: float
    net_revenue: float

class DepartmentOccupancyResponse(BaseModel):
    department_stats: Dict[str, Any]
