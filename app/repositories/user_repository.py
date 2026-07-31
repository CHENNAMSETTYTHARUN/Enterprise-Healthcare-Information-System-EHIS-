from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User, Role, Permission
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email, User.is_active == True).first()

class RoleRepository(BaseRepository[Role]):
    def __init__(self):
        super().__init__(Role)

    def get_by_name(self, db: Session, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name, Role.is_active == True).first()

class PermissionRepository(BaseRepository[Permission]):
    def __init__(self):
        super().__init__(Permission)

    def get_by_name(self, db: Session, name: str) -> Optional[Permission]:
        return db.query(Permission).filter(Permission.name == name, Permission.is_active == True).first()

user_repository = UserRepository()
role_repository = RoleRepository()
permission_repository = PermissionRepository()
