from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, decode_token, blacklist_token,
    validate_password_strength
)
from app.core.exceptions import UnauthorizedException, ConflictException, NotFoundException, BadRequestException
from app.repositories.user_repository import user_repository, role_repository
from app.schemas.auth import LoginRequest, TokenResponse, UserMinResponse
from app.schemas.user import UserCreate
from app.models.user import User, UserSession

class AuthService:
    def authenticate_user(self, db: Session, login_data: LoginRequest, device_info: str = None, ip_address: str = None) -> TokenResponse:
        user = user_repository.get_by_email(db, login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        role_names = [role.name for role in user.roles]

        claims = {
            "email": user.email,
            "roles": role_names,
            "is_superuser": user.is_superuser
        }

        access_token = create_access_token(subject=user.id, claims=claims)
        refresh_token = create_refresh_token(subject=user.id)

        session = UserSession(
            user_id=user.id,
            device_info=device_info,
            ip_address=ip_address,
            last_active=datetime.now(timezone.utc),
            is_active=True
        )
        db.add(session)
        db.commit()

        user_min = UserMinResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=role_names
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=480 * 60,
            user=user_min
        )

    def logout_user(self, token: str) -> dict:
        blacklist_token(token)
        return {"message": "Logged out successfully"}

    def register_user(self, db: Session, user_in: UserCreate) -> User:
        existing = user_repository.get_by_email(db, user_in.email)
        if existing:
            raise ConflictException(f"User with email '{user_in.email}' already exists")

        errors = validate_password_strength(user_in.password)
        if errors:
            raise BadRequestException("; ".join(errors))

        hashed_password = get_password_hash(user_in.password)

        roles = []
        if user_in.role_names:
            for r_name in user_in.role_names:
                role_obj = role_repository.get_by_name(db, r_name)
                if role_obj:
                    roles.append(role_obj)

        if not roles:
            default_role = role_repository.get_by_name(db, "PATIENT")
            if default_role:
                roles.append(default_role)

        new_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            phone_number=user_in.phone_number,
            hospital_id=user_in.hospital_id,
            is_verified=True,
            roles=roles
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def refresh_token(self, db: Session, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type")
            user_id = payload.get("sub")
        except Exception:
            raise UnauthorizedException("Invalid or expired refresh token")

        user = user_repository.get_by_id(db, user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        role_names = [role.name for role in user.roles]
        claims = {
            "email": user.email,
            "roles": role_names,
            "is_superuser": user.is_superuser
        }

        new_access_token = create_access_token(subject=user.id, claims=claims)
        new_refresh_token = create_refresh_token(subject=user.id)

        user_min = UserMinResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=role_names
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=480 * 60,
            user=user_min
        )

    def get_user_sessions(self, db: Session, user_id: str):
        return db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).all()

    def revoke_session(self, db: Session, user_id: str, session_id: str):
        session = db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == user_id
        ).first()
        if not session:
            raise NotFoundException("Session not found")
        session.is_active = False
        db.commit()
        return {"message": "Session revoked"}

auth_service = AuthService()
