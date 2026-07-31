from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_roles
from app.repositories.user_repository import user_repository, role_repository, permission_repository
from app.schemas.user import UserResponse, UserUpdate, RoleCreate, RoleResponse, PermissionResponse
from app.schemas.common import PaginatedResponse, GenericResponse
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=PaginatedResponse[UserResponse], dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN"]))])
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    users, total = user_repository.get_all(
        db, page=page, page_size=page_size, search=search,
        search_fields=["email", "first_name", "last_name", "phone_number"],
        sort_by=sort_by, sort_order=sort_order
    )
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(items=users, total=total, page=page, page_size=page_size, pages=pages)

@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN"]))])
def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise NotFoundException(f"User '{user_id}' not found")
    return user

@router.put("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN"]))])
def update_user(user_id: str, user_in: UserUpdate, db: Session = Depends(get_db)):
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise NotFoundException(f"User '{user_id}' not found")
    return user_repository.update(db, user, user_in.model_dump(exclude_unset=True))

@router.delete("/{user_id}", response_model=GenericResponse, dependencies=[Depends(require_roles(["SUPER_ADMIN"]))])
def delete_user(user_id: str, db: Session = Depends(get_db)):
    success = user_repository.delete(db, user_id)
    if not success:
        raise NotFoundException(f"User '{user_id}' not found")
    return GenericResponse(message=f"User '{user_id}' deactivated.")

@router.get("/roles/all", response_model=List[RoleResponse], dependencies=[Depends(require_roles(["SUPER_ADMIN", "HOSPITAL_ADMIN"]))])
def get_roles(db: Session = Depends(get_db)):
    roles, _ = role_repository.get_all(db, page=1, page_size=100)
    return roles

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["SUPER_ADMIN"]))])
def create_role(role_in: RoleCreate, db: Session = Depends(get_db)):
    role_dict = role_in.model_dump(exclude={"permission_ids"})
    return role_repository.create(db, role_dict)

@router.get("/permissions/all", response_model=List[PermissionResponse], dependencies=[Depends(require_roles(["SUPER_ADMIN"]))])
def get_permissions(db: Session = Depends(get_db)):
    perms, _ = permission_repository.get_all(db, page=1, page_size=100)
    return perms
