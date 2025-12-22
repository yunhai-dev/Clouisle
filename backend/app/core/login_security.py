"""
登录安全模块
处理登录尝试限制、账号锁定等
"""

from datetime import timedelta
from typing import Optional, Tuple

from app.core.timezone import now_utc
from app.core.redis import get_redis
from app.models.site_setting import SiteSetting
from app.models.user import User


# Redis key 前缀
LOGIN_ATTEMPTS_PREFIX = "login:attempts:"


async def check_account_locked(user: User) -> Tuple[bool, Optional[int]]:
    """
    检查账号是否被锁定

    Returns:
        Tuple[bool, Optional[int]]: (是否锁定, 剩余锁定秒数)
    """
    if user.locked_until is None:
        return False, None

    now = now_utc()
    if user.locked_until > now:
        remaining = int((user.locked_until - now).total_seconds())
        return True, remaining

    # 锁定已过期，重置
    user.locked_until = None
    user.failed_login_attempts = 0
    await user.save()
    return False, None


async def record_failed_login(user: User) -> Tuple[bool, int, Optional[int]]:
    """
    记录登录失败

    Returns:
        Tuple[bool, int, Optional[int]]: (是否被锁定, 剩余尝试次数, 锁定秒数)
    """
    # 获取安全设置
    max_attempts = await SiteSetting.get_value("max_login_attempts", 5)
    lockout_minutes = await SiteSetting.get_value("lockout_duration_minutes", 15)

    # 增加失败次数
    user.failed_login_attempts += 1
    remaining_attempts = max(0, max_attempts - user.failed_login_attempts)

    # 检查是否需要锁定
    if user.failed_login_attempts >= max_attempts:
        user.locked_until = now_utc() + timedelta(minutes=lockout_minutes)
        await user.save()
        return True, 0, lockout_minutes * 60

    await user.save()
    return False, remaining_attempts, None


async def reset_login_attempts(user: User):
    """
    重置登录失败次数（登录成功后调用）
    """
    if user.failed_login_attempts > 0 or user.locked_until is not None:
        user.failed_login_attempts = 0
        user.locked_until = None
        await user.save()


async def get_login_attempts_by_ip(ip: str) -> int:
    """
    获取 IP 的登录尝试次数（防止暴力破解用户名）
    """
    r = await get_redis()
    key = f"{LOGIN_ATTEMPTS_PREFIX}ip:{ip}"
    count = await r.get(key)
    return int(count) if count else 0


async def record_ip_login_attempt(ip: str, ttl: int = 3600):
    """
    记录 IP 登录尝试
    """
    r = await get_redis()
    key = f"{LOGIN_ATTEMPTS_PREFIX}ip:{ip}"
    await r.incr(key)
    await r.expire(key, ttl)


async def reset_ip_login_attempts(ip: str):
    """
    重置 IP 登录尝试次数
    """
    r = await get_redis()
    key = f"{LOGIN_ATTEMPTS_PREFIX}ip:{ip}"
    await r.delete(key)
