from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


# Permission Schemas
class PermissionBase(BaseModel):
    scope: str
    code: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class Permission(PermissionBase):
    id: UUID

    class Config:
        from_attributes = True


# Role Schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permissions: List[str] = []  # List of permission codes


class Role(RoleBase):
    id: UUID
    is_system_role: bool
    permissions: List[Permission] = []

    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    department_id: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    department_id: Optional[str] = None
    avatar_url: Optional[str] = None
    roles: Optional[List[str]] = None  # List of role names


class UserInDBBase(UserBase):
    id: UUID
    created_at: datetime
    last_login: Optional[datetime] = None
    auth_source: str
    external_id: Optional[str] = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    roles: List[Role] = []


class UserInDB(UserInDBBase):
    hashed_password: str
