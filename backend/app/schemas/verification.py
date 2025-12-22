"""
邮件验证相关 Schema
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class SendVerificationRequest(BaseModel):
    """发送验证邮件请求"""
    email: EmailStr
    purpose: str = "register"  # register, reset_password


class VerifyCodeRequest(BaseModel):
    """验证码验证请求"""
    email: EmailStr
    code: str
    purpose: str = "register"


class VerifyTokenRequest(BaseModel):
    """Token 验证请求"""
    token: str


class ResendVerificationRequest(BaseModel):
    """重新发送验证邮件请求"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    email: EmailStr


class ResetPasswordConfirmRequest(BaseModel):
    """确认重置密码请求"""
    email: EmailStr
    code: str
    new_password: str


class VerificationResponse(BaseModel):
    """验证响应"""
    verified: bool
    email: Optional[str] = None
