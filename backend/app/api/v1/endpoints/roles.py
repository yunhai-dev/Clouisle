from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.api import deps
from app.models.user import Role, Permission, User
from app.schemas.user import Role as RoleSchema, RoleCreate
from app.schemas.response import Response, PageData, success

router = APIRouter()


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RolePermissionsUpdate(BaseModel):
    permissions: List[str]  # List of permission codes


@router.get("/", response_model=Response[PageData[RoleSchema]])
async def read_roles(
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve roles.
    """
    total = await Role.all().count()
    skip = (page - 1) * page_size
    roles = await Role.all().offset(skip).limit(page_size).prefetch_related("permissions")
    
    return success(data={
        "items": roles,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("/", response_model=Response[RoleSchema])
async def create_role(
    *,
    role_in: RoleCreate,
    current_user: User = Depends(deps.PermissionChecker("user:manage")),
) -> Any:
    """
    Create new role.
    """
    try:
        role = await Role.create(
            name=role_in.name,
            description=role_in.description,
            is_system_role=False,
        )
        
        # Add permissions
        if role_in.permissions:
            for perm_code in role_in.permissions:
                try:
                    perm = await Permission.get(code=perm_code)
                    await role.permissions.add(perm)
                except DoesNotExist:
                    pass  # Skip non-existent permissions
        
        # Reload with permissions
        role = await Role.get(id=role.id).prefetch_related("permissions")
        return success(data=role, msg="Role created successfully")
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Role with this name already exists",
        )


@router.get("/{role_id}", response_model=Response[RoleSchema])
async def read_role(
    role_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get role by ID.
    """
    try:
        role = await Role.get(id=role_id).prefetch_related("permissions")
        return success(data=role)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Role not found",
        )


@router.put("/{role_id}", response_model=Response[RoleSchema])
async def update_role(
    *,
    role_id: UUID,
    role_in: RoleUpdate,
    current_user: User = Depends(deps.PermissionChecker("user:manage")),
) -> Any:
    """
    Update a role.
    """
    try:
        role = await Role.get(id=role_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Role not found",
        )
    
    if role.is_system_role:
        raise HTTPException(
            status_code=400,
            detail="System roles cannot be modified",
        )
    
    # Check if name is being changed and if it conflicts
    if role_in.name and role_in.name != role.name:
        existing = await Role.filter(name=role_in.name).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Role with this name already exists",
            )
        role.name = role_in.name
    
    if role_in.description is not None:
        role.description = role_in.description
    
    await role.save()
    
    role = await Role.get(id=role_id).prefetch_related("permissions")
    return success(data=role, msg="Role updated successfully")


@router.put("/{role_id}/permissions", response_model=Response[RoleSchema])
async def update_role_permissions(
    *,
    role_id: UUID,
    permissions_in: RolePermissionsUpdate,
    current_user: User = Depends(deps.PermissionChecker("user:manage")),
) -> Any:
    """
    Update role permissions (replace all).
    """
    try:
        role = await Role.get(id=role_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Role not found",
        )
    
    if role.is_system_role:
        raise HTTPException(
            status_code=400,
            detail="System role permissions cannot be modified",
        )
    
    # Clear existing permissions
    await role.permissions.clear()
    
    # Add new permissions
    for perm_code in permissions_in.permissions:
        try:
            perm = await Permission.get(code=perm_code)
            await role.permissions.add(perm)
        except DoesNotExist:
            raise HTTPException(
                status_code=400,
                detail=f"Permission '{perm_code}' not found",
            )
    
    role = await Role.get(id=role_id).prefetch_related("permissions")
    return success(data=role, msg="Role permissions updated successfully")


@router.delete("/{role_id}", response_model=Response[RoleSchema])
async def delete_role(
    role_id: UUID,
    current_user: User = Depends(deps.PermissionChecker("user:manage")),
) -> Any:
    """
    Delete a role.
    """
    try:
        role = await Role.get(id=role_id).prefetch_related("permissions")
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Role not found",
        )
    
    if role.is_system_role:
        raise HTTPException(
            status_code=400,
            detail="System roles cannot be deleted",
        )
    
    # Check if role is assigned to any users
    users_with_role = await User.filter(roles=role).count()
    if users_with_role > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete role: {users_with_role} user(s) are assigned to this role",
        )
    
    await role.delete()
    return success(data=role, msg="Role deleted successfully")
