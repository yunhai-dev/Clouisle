from typing import Generator, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from tortoise.exceptions import DoesNotExist

from app.core.config import settings
from app.core.security import settings as security_settings
from app.models.user import User
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


async def get_current_user(token: str = Depends(reusable_oauth2)) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    if token_data.sub is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
        
    try:
        user = await User.get(id=token_data.sub).prefetch_related("roles__permissions")
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.is_superuser:
            return current_user

        # Check permissions
        # Since we prefetched roles and permissions, we can check in memory
        # Note: roles__permissions is a list of Permission objects
        
        has_permission = False
        for role in current_user.roles:
            for permission in role.permissions:
                if permission.code == self.required_permission or permission.code == "*":
                    has_permission = True
                    break
            if has_permission:
                break
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required: {self.required_permission}",
            )
        
        return current_user
