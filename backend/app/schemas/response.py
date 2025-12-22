from enum import IntEnum
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseCode(IntEnum):
    """响应状态码枚举"""
    # 成功
    SUCCESS = 0
    
    # 通用错误 (1000-1999)
    UNKNOWN_ERROR = 1000
    VALIDATION_ERROR = 1001
    
    # 认证错误 (2000-2999)
    UNAUTHORIZED = 2000
    INVALID_TOKEN = 2001
    TOKEN_EXPIRED = 2002
    INVALID_CREDENTIALS = 2003
    INACTIVE_USER = 2004
    
    # 权限错误 (3000-3999)
    PERMISSION_DENIED = 3000
    INSUFFICIENT_PRIVILEGES = 3001
    
    # 资源错误 (4000-4999)
    NOT_FOUND = 4000
    USER_NOT_FOUND = 4001
    ROLE_NOT_FOUND = 4002
    PERMISSION_NOT_FOUND = 4003
    
    # 业务逻辑错误 (5000-5999)
    ALREADY_EXISTS = 5000
    USERNAME_EXISTS = 5001
    EMAIL_EXISTS = 5002
    ROLE_NAME_EXISTS = 5003
    PERMISSION_CODE_EXISTS = 5004
    CANNOT_DELETE_SYSTEM_ROLE = 5010
    CANNOT_DELETE_SUPERUSER = 5011
    CANNOT_DELETE_WILDCARD_PERMISSION = 5012
    CANNOT_MODIFY_SYSTEM_ROLE = 5013
    ROLE_IN_USE = 5020


# 状态码对应的默认消息
CODE_MESSAGES: dict[ResponseCode, str] = {
    ResponseCode.SUCCESS: "Success",
    ResponseCode.UNKNOWN_ERROR: "Unknown error",
    ResponseCode.VALIDATION_ERROR: "Validation error",
    ResponseCode.UNAUTHORIZED: "Unauthorized",
    ResponseCode.INVALID_TOKEN: "Invalid token",
    ResponseCode.TOKEN_EXPIRED: "Token expired",
    ResponseCode.INVALID_CREDENTIALS: "Invalid credentials",
    ResponseCode.INACTIVE_USER: "Inactive user",
    ResponseCode.PERMISSION_DENIED: "Permission denied",
    ResponseCode.INSUFFICIENT_PRIVILEGES: "Insufficient privileges",
    ResponseCode.NOT_FOUND: "Resource not found",
    ResponseCode.USER_NOT_FOUND: "User not found",
    ResponseCode.ROLE_NOT_FOUND: "Role not found",
    ResponseCode.PERMISSION_NOT_FOUND: "Permission not found",
    ResponseCode.ALREADY_EXISTS: "Resource already exists",
    ResponseCode.USERNAME_EXISTS: "Username already exists",
    ResponseCode.EMAIL_EXISTS: "Email already exists",
    ResponseCode.ROLE_NAME_EXISTS: "Role name already exists",
    ResponseCode.PERMISSION_CODE_EXISTS: "Permission code already exists",
    ResponseCode.CANNOT_DELETE_SYSTEM_ROLE: "Cannot delete system role",
    ResponseCode.CANNOT_DELETE_SUPERUSER: "Cannot delete superuser",
    ResponseCode.CANNOT_DELETE_WILDCARD_PERMISSION: "Cannot delete wildcard permission",
    ResponseCode.CANNOT_MODIFY_SYSTEM_ROLE: "Cannot modify system role",
    ResponseCode.ROLE_IN_USE: "Role is assigned to users and cannot be deleted",
}


class Response(BaseModel, Generic[T]):
    """统一响应格式"""
    code: int = ResponseCode.SUCCESS
    data: Optional[T] = None
    msg: str = "success"


class PageData(BaseModel, Generic[T]):
    """分页数据"""
    items: list[T]
    total: int
    page: int
    page_size: int


class PageResponse(Response[PageData[T]], Generic[T]):
    """分页响应"""
    pass


# 便捷函数
def success(data: Any = None, msg: str = "success") -> dict:
    """成功响应"""
    return {"code": ResponseCode.SUCCESS, "data": data, "msg": msg}


def error(
    code: ResponseCode | int = ResponseCode.UNKNOWN_ERROR, 
    msg: str | None = None, 
    data: Any = None
) -> dict:
    """错误响应"""
    if msg is None and isinstance(code, ResponseCode):
        msg = CODE_MESSAGES.get(code, "Error")
    return {"code": int(code), "data": data, "msg": msg or "Error"}
