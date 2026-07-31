from typing import List
from fastapi import Depends
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.core.exceptions import ForbiddenException

class PermissionChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user

        user_role_names = [role.name for role in current_user.roles]
        has_role = any(role in self.allowed_roles for role in user_role_names)
        if not has_role:
            raise ForbiddenException(f"Access denied for roles: {user_role_names}")
        return current_user

def require_roles(allowed_roles: List[str]):
    return PermissionChecker(allowed_roles)
