"""
Internationalization (i18n) module for multi-language support.
Currently supports: English (en), Chinese (zh)
"""
from contextvars import ContextVar
from enum import Enum
from typing import Optional

# Context variable to store current language per request
current_language: ContextVar[str] = ContextVar("current_language", default="en")


class Language(str, Enum):
    """Supported languages"""
    EN = "en"
    ZH = "zh"


# Translation messages dictionary
# Format: {message_key: {language_code: translated_message}}
TRANSLATIONS: dict[str, dict[str, str]] = {
    # Success messages
    "success": {
        "en": "Success",
        "zh": "成功",
    },
    "login_successful": {
        "en": "Login successful",
        "zh": "登录成功",
    },
    "logout_successful": {
        "en": "Logout successful",
        "zh": "登出成功",
    },
    "registration_successful": {
        "en": "Registration successful",
        "zh": "注册成功",
    },
    "registration_pending_approval": {
        "en": "Registration successful. Your account is pending admin approval.",
        "zh": "注册成功。您的账户正在等待管理员审核。",
    },
    "registration_pending_verification": {
        "en": "Registration successful. Please verify your email to activate your account.",
        "zh": "注册成功。请验证您的邮箱以激活账户。",
    },
    "registration_successful_superadmin": {
        "en": "Registration successful. You are the first user and have been promoted to Super Admin!",
        "zh": "注册成功。您是第一个用户，已被提升为超级管理员！",
    },
    "registration_disabled": {
        "en": "Registration is currently disabled",
        "zh": "注册功能已关闭",
    },
    "user_created": {
        "en": "User created successfully",
        "zh": "用户创建成功",
    },
    "user_updated": {
        "en": "User updated successfully",
        "zh": "用户更新成功",
    },
    "user_deleted": {
        "en": "User deleted successfully",
        "zh": "用户删除成功",
    },
    "user_activated": {
        "en": "User activated successfully",
        "zh": "用户激活成功",
    },
    "user_deactivated": {
        "en": "User deactivated successfully",
        "zh": "用户已禁用",
    },
    "user_already_active": {
        "en": "User is already active",
        "zh": "用户已经是激活状态",
    },
    "user_already_inactive": {
        "en": "User is already inactive",
        "zh": "用户已经是禁用状态",
    },
    "cannot_deactivate_superuser": {
        "en": "Cannot deactivate superuser",
        "zh": "不能禁用超级管理员",
    },
    "profile_updated": {
        "en": "Profile updated successfully",
        "zh": "个人资料更新成功",
    },
    "password_changed": {
        "en": "Password changed successfully",
        "zh": "密码修改成功",
    },
    "current_password_incorrect": {
        "en": "Current password is incorrect",
        "zh": "当前密码不正确",
    },
    "password_too_short": {
        "en": "Password must be at least 6 characters",
        "zh": "密码长度至少为 6 个字符",
    },
    "account_deleted": {
        "en": "Account deleted successfully",
        "zh": "账号已删除",
    },
    "cannot_delete_superuser_account": {
        "en": "Super admin cannot delete their own account",
        "zh": "超级管理员不能删除自己的账号",
    },
    "account_deletion_disabled": {
        "en": "Account deletion is disabled by administrator",
        "zh": "管理员已禁用账号自主删除功能",
    },
    "role_created": {
        "en": "Role created successfully",
        "zh": "角色创建成功",
    },
    "role_updated": {
        "en": "Role updated successfully",
        "zh": "角色更新成功",
    },
    "role_deleted": {
        "en": "Role deleted successfully",
        "zh": "角色删除成功",
    },
    "role_permissions_updated": {
        "en": "Role permissions updated successfully",
        "zh": "角色权限更新成功",
    },
    "permission_created": {
        "en": "Permission created successfully",
        "zh": "权限创建成功",
    },
    "permission_updated": {
        "en": "Permission updated successfully",
        "zh": "权限更新成功",
    },
    "permission_deleted": {
        "en": "Permission deleted successfully",
        "zh": "权限删除成功",
    },
    
    # Error messages - General
    "unknown_error": {
        "en": "Unknown error",
        "zh": "未知错误",
    },
    "validation_error": {
        "en": "Validation error",
        "zh": "验证错误",
    },
    
    # Error messages - Authentication
    "unauthorized": {
        "en": "Unauthorized",
        "zh": "未授权",
    },
    "invalid_token": {
        "en": "Invalid token",
        "zh": "无效的令牌",
    },
    "token_expired": {
        "en": "Token expired",
        "zh": "令牌已过期",
    },
    "token_revoked": {
        "en": "Token has been revoked",
        "zh": "令牌已被撤销",
    },
    "invalid_credentials": {
        "en": "Invalid credentials",
        "zh": "凭证无效",
    },
    "incorrect_email_or_password": {
        "en": "Incorrect email or password",
        "zh": "邮箱或密码错误",
    },
    "inactive_user": {
        "en": "Inactive user",
        "zh": "用户未激活",
    },
    "could_not_validate_credentials": {
        "en": "Could not validate credentials",
        "zh": "无法验证凭证",
    },
    
    # Account security messages
    "account_locked": {
        "en": "Account is locked. Please try again later.",
        "zh": "账户已被锁定，请稍后再试。",
    },
    "account_locked_after_attempts": {
        "en": "Too many failed login attempts. Account has been locked.",
        "zh": "登录失败次数过多，账户已被锁定。",
    },
    "email_not_verified": {
        "en": "Please verify your email before logging in",
        "zh": "请先验证您的邮箱",
    },
    "password_too_weak": {
        "en": "Password does not meet security requirements",
        "zh": "密码不符合安全要求",
    },
    
    # Email verification messages
    "smtp_not_configured": {
        "en": "Email service is not configured",
        "zh": "邮件服务未配置",
    },
    "email_send_too_frequent": {
        "en": "Please wait before requesting another email",
        "zh": "请稍后再请求发送邮件",
    },
    "email_not_found": {
        "en": "Email not found",
        "zh": "邮箱未找到",
    },
    "email_already_verified": {
        "en": "Email has already been verified",
        "zh": "邮箱已验证",
    },
    "verification_email_sent": {
        "en": "Verification email has been sent",
        "zh": "验证邮件已发送",
    },
    "verification_code_invalid": {
        "en": "Invalid verification code",
        "zh": "验证码无效",
    },
    "verification_token_invalid": {
        "en": "Verification link is invalid or expired",
        "zh": "验证链接无效或已过期",
    },
    "email_verified_success": {
        "en": "Email verified successfully",
        "zh": "邮箱验证成功",
    },
    "reset_password_email_sent": {
        "en": "If the email exists, a password reset link has been sent",
        "zh": "如果邮箱存在，密码重置链接已发送",
    },
    "password_reset_success": {
        "en": "Password has been reset successfully",
        "zh": "密码重置成功",
    },
    "email_send_failed": {
        "en": "Failed to send email",
        "zh": "邮件发送失败",
    },
    "test_email_sent": {
        "en": "Test email sent successfully",
        "zh": "测试邮件发送成功",
    },
    "email_queued": {
        "en": "Emails have been queued for sending",
        "zh": "邮件已加入发送队列",
    },
    "email_rate_limit_exceeded": {
        "en": "Email sending rate limit exceeded. Please try again later.",
        "zh": "邮件发送频率超限，请稍后再试",
    },
    "email_quota_insufficient": {
        "en": "Insufficient email quota for this batch. Reduce the number of recipients.",
        "zh": "邮件配额不足，请减少收件人数量",
    },
    
    # File upload messages
    "file_uploaded": {
        "en": "File uploaded successfully",
        "zh": "文件上传成功",
    },
    "file_deleted": {
        "en": "File deleted successfully",
        "zh": "文件删除成功",
    },
    "file_not_found": {
        "en": "File not found",
        "zh": "文件不存在",
    },
    "invalid_file_type": {
        "en": "Invalid file type",
        "zh": "不支持的文件类型",
    },
    "file_too_large": {
        "en": "File too large",
        "zh": "文件过大",
    },
    
    # Captcha messages
    "captcha_required": {
        "en": "Captcha is required",
        "zh": "请输入验证码",
    },
    "captcha_invalid": {
        "en": "Invalid captcha answer",
        "zh": "验证码错误",
    },
    
    # Error messages - Permission
    "permission_denied": {
        "en": "Permission denied",
        "zh": "权限被拒绝",
    },
    "insufficient_privileges": {
        "en": "Insufficient privileges",
        "zh": "权限不足",
    },
    "operation_not_permitted": {
        "en": "Operation not permitted. Required: {permission}",
        "zh": "操作不允许。需要权限：{permission}",
    },
    
    # Error messages - Resource
    "not_found": {
        "en": "Resource not found",
        "zh": "资源未找到",
    },
    "user_not_found": {
        "en": "User not found",
        "zh": "用户未找到",
    },
    "role_not_found": {
        "en": "Role not found",
        "zh": "角色未找到",
    },
    "permission_not_found": {
        "en": "Permission not found",
        "zh": "权限未找到",
    },
    "permission_code_not_found": {
        "en": "Permission '{code}' not found",
        "zh": "权限 '{code}' 未找到",
    },
    
    # Error messages - Business logic
    "already_exists": {
        "en": "Resource already exists",
        "zh": "资源已存在",
    },
    "username_exists": {
        "en": "Username already exists",
        "zh": "用户名已存在",
    },
    "username_already_registered": {
        "en": "Username already registered",
        "zh": "用户名已被注册",
    },
    "email_exists": {
        "en": "Email already exists",
        "zh": "邮箱已存在",
    },
    "email_already_registered": {
        "en": "Email already registered",
        "zh": "邮箱已被注册",
    },
    "user_with_username_exists": {
        "en": "The user with this username already exists in the system.",
        "zh": "该用户名已存在于系统中。",
    },
    "user_with_email_exists": {
        "en": "The user with this email already exists in the system.",
        "zh": "该邮箱已存在于系统中。",
    },
    "user_with_id_not_exists": {
        "en": "The user with this id does not exist in the system",
        "zh": "该ID的用户不存在于系统中",
    },
    "role_name_exists": {
        "en": "Role name already exists",
        "zh": "角色名已存在",
    },
    "role_with_name_exists": {
        "en": "Role with this name already exists",
        "zh": "该角色名已存在",
    },
    "permission_code_exists": {
        "en": "Permission code already exists",
        "zh": "权限代码已存在",
    },
    "permission_with_code_exists": {
        "en": "Permission with this code already exists",
        "zh": "该权限代码已存在",
    },
    "cannot_delete_system_role": {
        "en": "System roles cannot be deleted",
        "zh": "系统角色不能被删除",
    },
    "cannot_delete_superuser": {
        "en": "Superusers cannot be deleted",
        "zh": "超级管理员不能被删除",
    },
    "cannot_delete_wildcard_permission": {
        "en": "Cannot delete the system wildcard permission",
        "zh": "不能删除系统通配符权限",
    },
    "cannot_modify_system_role": {
        "en": "System roles cannot be modified",
        "zh": "系统角色不能被修改",
    },
    "cannot_modify_system_role_permissions": {
        "en": "System role permissions cannot be modified",
        "zh": "系统角色权限不能被修改",
    },
    "role_in_use": {
        "en": "Cannot delete role: {count} user(s) are assigned to this role",
        "zh": "无法删除角色：有 {count} 个用户分配了此角色",
    },
    
    # Team messages
    "team_created": {
        "en": "Team created successfully",
        "zh": "团队创建成功",
    },
    "team_updated": {
        "en": "Team updated successfully",
        "zh": "团队更新成功",
    },
    "team_deleted": {
        "en": "Team deleted successfully",
        "zh": "团队删除成功",
    },
    "team_not_found": {
        "en": "Team not found",
        "zh": "团队未找到",
    },
    "team_name_exists": {
        "en": "Team with this name already exists",
        "zh": "该团队名称已存在",
    },
    "not_team_member": {
        "en": "You are not a member of this team",
        "zh": "您不是该团队成员",
    },
    "team_admin_required": {
        "en": "Team owner or admin permission required",
        "zh": "需要团队所有者或管理员权限",
    },
    "team_owner_required": {
        "en": "Team owner permission required",
        "zh": "需要团队所有者权限",
    },
    "cannot_delete_default_team": {
        "en": "Cannot delete the default team",
        "zh": "不能删除默认团队",
    },
    
    # Team member messages
    "team_member_added": {
        "en": "Team member added successfully",
        "zh": "团队成员添加成功",
    },
    "team_member_updated": {
        "en": "Team member updated successfully",
        "zh": "团队成员更新成功",
    },
    "team_member_removed": {
        "en": "Team member removed successfully",
        "zh": "团队成员移除成功",
    },
    "team_member_not_found": {
        "en": "Team member not found",
        "zh": "团队成员未找到",
    },
    "already_team_member": {
        "en": "User is already a member of this team",
        "zh": "用户已是该团队成员",
    },
    "cannot_add_as_owner": {
        "en": "Cannot add member as owner",
        "zh": "不能将成员添加为所有者",
    },
    "cannot_change_owner_role": {
        "en": "Cannot change the owner's role",
        "zh": "不能更改所有者角色",
    },
    "cannot_promote_to_owner": {
        "en": "Cannot promote to owner. Use transfer ownership instead",
        "zh": "不能提升为所有者，请使用转让所有权功能",
    },
    "cannot_remove_owner": {
        "en": "Cannot remove team owner. Transfer ownership first or delete the team",
        "zh": "不能移除团队所有者，请先转让所有权或删除团队",
    },
    "owner_cannot_leave": {
        "en": "Team owner cannot leave. Transfer ownership first or delete the team",
        "zh": "团队所有者不能离开，请先转让所有权或删除团队",
    },
    "team_left": {
        "en": "You have left the team",
        "zh": "您已离开团队",
    },
    "ownership_transferred": {
        "en": "Team ownership transferred successfully",
        "zh": "团队所有权转让成功",
    },
}


def get_language() -> str:
    """Get current language from context variable"""
    return current_language.get()


def set_language(lang: str) -> None:
    """Set current language in context variable"""
    # Normalize language code
    lang = lang.lower().split("-")[0]  # "zh-CN" -> "zh"
    if lang not in [l.value for l in Language]:
        lang = Language.EN.value
    current_language.set(lang)


def t(key: str, lang: Optional[str] = None, **kwargs) -> str:
    """
    Translate a message key to the current language.
    
    Args:
        key: Message key to translate
        lang: Optional language override (defaults to current context language)
        **kwargs: Format arguments for the message
        
    Returns:
        Translated message string
    """
    if lang is None:
        lang = get_language()
    
    # Normalize language code
    lang = lang.lower().split("-")[0]
    if lang not in [l.value for l in Language]:
        lang = Language.EN.value
    
    # Get translation
    translations = TRANSLATIONS.get(key, {})
    message = translations.get(lang) or translations.get(Language.EN.value, key)
    
    # Apply format arguments
    if kwargs:
        try:
            message = message.format(**kwargs)
        except (KeyError, ValueError):
            pass
    
    return message


def get_code_message(code: int, lang: Optional[str] = None) -> str:
    """
    Get translated message for a ResponseCode.
    Maps ResponseCode values to translation keys.
    """
    from app.schemas.response import ResponseCode
    
    # Map ResponseCode to translation key
    code_to_key = {
        ResponseCode.SUCCESS: "success",
        ResponseCode.UNKNOWN_ERROR: "unknown_error",
        ResponseCode.VALIDATION_ERROR: "validation_error",
        ResponseCode.UNAUTHORIZED: "unauthorized",
        ResponseCode.INVALID_TOKEN: "invalid_token",
        ResponseCode.TOKEN_EXPIRED: "token_expired",
        ResponseCode.INVALID_CREDENTIALS: "invalid_credentials",
        ResponseCode.INACTIVE_USER: "inactive_user",
        ResponseCode.PERMISSION_DENIED: "permission_denied",
        ResponseCode.INSUFFICIENT_PRIVILEGES: "insufficient_privileges",
        ResponseCode.NOT_FOUND: "not_found",
        ResponseCode.USER_NOT_FOUND: "user_not_found",
        ResponseCode.ROLE_NOT_FOUND: "role_not_found",
        ResponseCode.PERMISSION_NOT_FOUND: "permission_not_found",
        ResponseCode.REGISTRATION_DISABLED: "registration_disabled",
        ResponseCode.ALREADY_EXISTS: "already_exists",
        ResponseCode.USERNAME_EXISTS: "username_exists",
        ResponseCode.EMAIL_EXISTS: "email_exists",
        ResponseCode.EMAIL_NOT_VERIFIED: "email_not_verified",
        ResponseCode.VERIFICATION_CODE_INVALID: "verification_code_invalid",
        ResponseCode.VERIFICATION_CODE_EXPIRED: "verification_token_invalid",
        ResponseCode.EMAIL_SEND_FAILED: "smtp_not_configured",
        ResponseCode.EMAIL_SEND_TOO_FREQUENT: "email_send_too_frequent",
        ResponseCode.ROLE_NAME_EXISTS: "role_name_exists",
        ResponseCode.PERMISSION_CODE_EXISTS: "permission_code_exists",
        ResponseCode.CANNOT_DELETE_SYSTEM_ROLE: "cannot_delete_system_role",
        ResponseCode.CANNOT_DELETE_SUPERUSER: "cannot_delete_superuser",
        ResponseCode.CANNOT_DELETE_WILDCARD_PERMISSION: "cannot_delete_wildcard_permission",
        ResponseCode.CANNOT_MODIFY_SYSTEM_ROLE: "cannot_modify_system_role",
        ResponseCode.ROLE_IN_USE: "role_in_use",
        ResponseCode.ACCOUNT_LOCKED: "account_locked",
        ResponseCode.TOO_MANY_LOGIN_ATTEMPTS: "account_locked_after_attempts",
        ResponseCode.CAPTCHA_REQUIRED: "captcha_required",
        ResponseCode.CAPTCHA_INVALID: "captcha_invalid",
    }
    
    try:
        response_code = ResponseCode(code)
        key = code_to_key.get(response_code, "unknown_error")
    except ValueError:
        key = "unknown_error"
    
    return t(key, lang)
