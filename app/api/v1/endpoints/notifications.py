from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.schemas.common import GenericResponse
from app.models.user import User
from app.models.audit import Notification
from app.background.tasks import send_email_notification, create_notification

router = APIRouter(prefix="/notifications", tags=["Enterprise Services"])

class EmailRequest(BaseModel):
    recipient: str
    subject: str
    body: str

class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str

@router.post("/send-email", response_model=GenericResponse)
def trigger_email_notification(
    req: EmailRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    background_tasks.add_task(send_email_notification, req.recipient, req.subject, req.body)
    return GenericResponse(message=f"Email task scheduled for '{req.recipient}'")

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_in_app_notification(
    req: NotificationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    background_tasks.add_task(create_notification, req.user_id, req.title, req.message)
    return {"message": "Notification created"}

@router.get("/my")
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifications = db.query(Notification).filter(
        Notification.recipient_user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()
    return [
        {"id": n.id, "title": n.title, "message": n.message, "is_read": n.is_read, "created_at": n.created_at}
        for n in notifications
    ]

@router.put("/my/{notification_id}/read", response_model=GenericResponse)
def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_user_id == current_user.id
    ).first()
    if not notification:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = "TRUE"
    db.commit()
    return GenericResponse(message="Notification marked as read")

@router.delete("/my/clear-all", response_model=GenericResponse)
def clear_all_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(Notification).filter(
        Notification.recipient_user_id == current_user.id,
        Notification.is_read == "TRUE"
    ).delete()
    db.commit()
    return GenericResponse(message="Read notifications cleared")
