"""
用量追踪定时任务

包含以下任务：
- 批量重置每日用量
- 批量重置每月用量
"""

import asyncio
import logging

from app.core.celery import celery_app
from app.core.timezone import now as get_now
from app.models.model import TeamModel

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.reset_daily_usage")
def reset_daily_usage():
    """
    重置所有团队模型的每日用量

    此任务应该在每天凌晨执行。
    """

    async def _reset():
        current_time = get_now()
        today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)

        # 使用批量更新，避免 N+1 查询问题
        count = await TeamModel.filter(daily_reset_at__lt=today_start).update(
            daily_tokens_used=0,
            daily_requests_used=0,
            daily_reset_at=current_time,
        )

        if count > 0:
            logger.info(f"Reset daily usage for {count} team models")
        else:
            logger.info("No team models need daily usage reset")

        return count

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_reset())


@celery_app.task(name="tasks.reset_monthly_usage")
def reset_monthly_usage():
    """
    重置所有团队模型的每月用量

    此任务应该在每月第一天凌晨执行。
    """

    async def _reset():
        current_time = get_now()
        month_start = current_time.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        # 使用批量更新，避免 N+1 查询问题
        count = await TeamModel.filter(monthly_reset_at__lt=month_start).update(
            monthly_tokens_used=0,
            monthly_requests_used=0,
            monthly_reset_at=current_time,
        )

        if count > 0:
            logger.info(f"Reset monthly usage for {count} team models")
        else:
            logger.info("No team models need monthly usage reset")

        return count

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_reset())
