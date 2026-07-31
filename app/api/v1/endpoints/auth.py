from fastapi import APIRouter, Depends, status, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.services.auth_service import auth_service
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest, PasswordResetRequest
from app.schemas.user import UserCreate, UserResponse
from app.schemas.common import GenericResponse
from app.models.user import User
from app.background.tasks import send_email_notification, log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])
bearer_scheme = HTTPBearer()

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    device_info = request.headers.get("User-Agent", "Unknown Device")
    ip_address = request.client.host if request.client else "Unknown"
    res = auth_service.authenticate_user(db, login_data, device_info=device_info, ip_address=ip_address)
    background_tasks.add_task(log_audit_event, res.user.id, "USER_LOGIN", {"email": login_data.email, "ip": ip_address})
    return res

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    new_user = auth_service.register_user(db, user_in)
    background_tasks.add_task(send_email_notification, new_user.email, "Welcome to EHIS", "Your account has been created successfully.")
    return new_user

@router.post("/logout", response_model=GenericResponse)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    result = auth_service.logout_user(credentials.credentials)
    background_tasks.add_task(log_audit_event, current_user.id, "USER_LOGOUT", {})
    return GenericResponse(message=result["message"])

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_token(db, req.refresh_token)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/sessions")
def get_my_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = auth_service.get_user_sessions(db, current_user.id)
    return [{"id": s.id, "device_info": s.device_info, "ip_address": s.ip_address, "last_active": s.last_active, "is_active": s.is_active} for s in sessions]

@router.delete("/sessions/{session_id}", response_model=GenericResponse)
def revoke_session(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return GenericResponse(message=auth_service.revoke_session(db, current_user.id, session_id)["message"])

@router.post("/forgot-password", response_model=GenericResponse)
def forgot_password(req: PasswordResetRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email_notification, req.email, "Password Reset", "Instructions to reset your password.")
    return GenericResponse(message="Password reset link sent to your email.")
