from typing import Generator, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from tortoise.exceptions import DoesNotExist

from app.core.config import settings
from app.core.security import settings as security_settings
from app.core.i18n import t
from app.core.redis import is_token_blacklisted
from app.models.user import User
from app.schemas.token import TokenPayload
from app.schemas.response import ResponseCode, BusinessError

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


async def get_current_user(token: str = Depends(reusable_oauth2)) -> User:
    # 检查 token 是否在黑名单中
    if await is_token_blacklisted(token):
        raise BusinessError(
            code=ResponseCode.INVALID_TOKEN,
            msg_key="token_revoked",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise BusinessError(
            code=ResponseCode.INVALID_CREDENTIALS,
            msg_key="could_not_validate_credentials",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    
    if token_data.sub is None:
        raise BusinessError(
            code=ResponseCode.USER_NOT_FOUND,
            msg_key="user_not_found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
        
    user = await User.filter(id=token_data.sub).prefetch_related("roles__permissions").first()
    if not user:
        raise BusinessError(
            code=ResponseCode.USER_NOT_FOUND,
            msg_key="user_not_found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise BusinessError(
            code=ResponseCode.INACTIVE_USER,
            msg_key="inactive_user",
        )
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise BusinessError(
            code=ResponseCode.INSUFFICIENT_PRIVILEGES,
            msg_key="insufficient_privileges",
            status_code=status.HTTP_403_FORBIDDEN,
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
            raise BusinessError(
                code=ResponseCode.PERMISSION_DENIED,
                msg_key="operation_not_permitted",
                status_code=status.HTTP_403_FORBIDDEN,
                permission=self.required_permission,
            )
        
        return current_user
