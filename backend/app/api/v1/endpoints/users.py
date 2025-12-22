from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.api import deps
from app.core import security
from app.models.user import User, Role
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.schemas.response import Response, PageData, success

router = APIRouter()


@router.get("/", response_model=Response[PageData[UserSchema]])
async def read_users(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(deps.PermissionChecker("user:read")),
) -> Any:
    """
    Retrieve users.
    """
    skip = (page - 1) * page_size
    total = await User.all().count()
    users = await User.all().offset(skip).limit(page_size).prefetch_related("roles")
    return success(data={
        "items": users,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("/", response_model=Response[UserSchema])
async def create_user(
    *,
    user_in: UserCreate,
    current_user: User = Depends(deps.PermissionChecker("user:create")),
) -> Any:
    """
    Create new user.
    """
    try:
        user_obj = await User.get(username=user_in.username)
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    except DoesNotExist:
        pass
    
    try:
        user_obj = await User.get(email=user_in.email)
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    except DoesNotExist:
        pass

    user_dict = user_in.model_dump(exclude_unset=True)
    password = user_dict.pop("password")
    hashed_password = security.get_password_hash(password)
    
    user = await User.create(
        **user_dict,
        hashed_password=hashed_password,
    )
    return success(data=user, msg="User created successfully")


@router.put("/{user_id}", response_model=Response[UserSchema])
async def update_user(
    *,
    user_id: UUID,
    user_in: UserUpdate,
    current_user: User = Depends(deps.PermissionChecker("user:update")),
) -> Any:
    """
    Update a user.
    """
    try:
        user = await User.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
        
    user_data = user_in.model_dump(exclude_unset=True)
    
    if "password" in user_data:
        password = user_data.pop("password")
        user_data["hashed_password"] = security.get_password_hash(password)
        
    if "roles" in user_data:
        role_names = user_data.pop("roles")
        roles = []
        for role_name in role_names:
            try:
                role = await Role.get(name=role_name)
                roles.append(role)
            except DoesNotExist:
                # Optionally ignore or raise error
                pass
        await user.roles.clear()
        await user.roles.add(*roles)

    await user.update_from_dict(user_data)
    await user.save()
    
    # Refresh to get updated relations
    updated_user = await User.get(id=user_id).prefetch_related("roles")
    return success(data=updated_user, msg="User updated successfully")


@router.get("/me", response_model=Response[UserSchema])
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return success(data=current_user)


@router.get("/{user_id}", response_model=Response[UserSchema])
async def read_user_by_id(
    user_id: UUID,
    current_user: User = Depends(deps.PermissionChecker("user:read")),
) -> Any:
    """
    Get a specific user by id.
    """
    try:
        user = await User.get(id=user_id).prefetch_related("roles")
        return success(data=user)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )


@router.delete("/{user_id}", response_model=Response[UserSchema])
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(deps.PermissionChecker("user:delete")),
) -> Any:
    """
    Delete a user.
    """
    try:
        user = await User.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    
    if user.is_superuser:
         raise HTTPException(
            status_code=400,
            detail="Superusers cannot be deleted",
        )

    await user.delete()
    return success(data=user, msg="User deleted successfully")
