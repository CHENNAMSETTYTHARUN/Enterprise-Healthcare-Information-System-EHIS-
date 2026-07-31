from typing import Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.repositories.user_repository import user_repository
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid access token type")
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException("Token payload missing subject ID")
    except Exception:
        raise UnauthorizedException("Could not validate authentication credentials")

    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise UnauthorizedException("User associated with token not found")
    if not user.is_active:
        raise UnauthorizedException("User account is deactivated")
        
    return user

def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise ForbiddenException("Requires Superuser privileges")
    return current_user
