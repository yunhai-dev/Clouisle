"""
Timezone utilities for consistent datetime handling across the application.
"""

from datetime import datetime, timezone as tz
from zoneinfo import ZoneInfo

from app.core.config import settings


def get_timezone() -> ZoneInfo:
    """Get the configured timezone."""
    return ZoneInfo(settings.TIMEZONE)


def now() -> datetime:
    """Get current datetime in configured timezone."""
    return datetime.now(get_timezone())


def now_utc() -> datetime:
    """Get current datetime in UTC."""
    return datetime.now(tz.utc)


def to_local(dt: datetime) -> datetime:
    """Convert datetime to configured timezone."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = dt.replace(tzinfo=tz.utc)
    return dt.astimezone(get_timezone())


def to_utc(dt: datetime) -> datetime:
    """Convert datetime to UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume local timezone if no timezone info
        dt = dt.replace(tzinfo=get_timezone())
    return dt.astimezone(tz.utc)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime in configured timezone."""
    if dt is None:
        return ""
    local_dt = to_local(dt)
    return local_dt.strftime(fmt)
