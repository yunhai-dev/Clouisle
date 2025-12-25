"""
用量追踪服务

负责追踪和管理团队模型的 Token 和请求用量。
"""

import logging
from typing import Optional

from app.core.timezone import now
from app.models.model import TeamModel

logger = logging.getLogger(__name__)


class QuotaExceededError(Exception):
    """配额超限异常"""

    def __init__(self, message: str, quota_type: str):
        super().__init__(message)
        self.quota_type = quota_type


class UsageTracker:
    """
    用量追踪器

    使用示例:
        from app.services.usage_tracker import usage_tracker

        # 检查配额并记录用量
        await usage_tracker.check_and_record_usage(
            team_id="...",
            model_id="...",
            tokens_used=1500,
            request_count=1,
        )

        # 仅检查配额（不记录）
        await usage_tracker.check_quota(team_id="...", model_id="...")

        # 获取用量统计
        stats = await usage_tracker.get_usage_stats(team_id="...", model_id="...")
    """

    async def _get_team_model(self, team_id: str, model_id: str) -> Optional[TeamModel]:
        """获取团队模型授权记录"""
        return (
            await TeamModel.filter(team_id=team_id, model_id=model_id)
            .select_related("model")
            .first()
        )

    async def _reset_daily_if_needed(self, team_model: TeamModel) -> bool:
        """检查并重置每日用量（如果需要）"""
        current_time = now()
        today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)

        if team_model.daily_reset_at is None or team_model.daily_reset_at < today_start:
            team_model.daily_tokens_used = 0
            team_model.daily_requests_used = 0
            team_model.daily_reset_at = current_time
            return True
        return False

    async def _reset_monthly_if_needed(self, team_model: TeamModel) -> bool:
        """检查并重置每月用量（如果需要）"""
        current_time = now()
        month_start = current_time.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        if (
            team_model.monthly_reset_at is None
            or team_model.monthly_reset_at < month_start
        ):
            team_model.monthly_tokens_used = 0
            team_model.monthly_requests_used = 0
            team_model.monthly_reset_at = current_time
            return True
        return False

    async def check_quota(
        self,
        team_id: str,
        model_id: str,
        tokens_needed: int = 0,
    ) -> TeamModel:
        """
        检查团队模型配额

        Args:
            team_id: 团队 ID
            model_id: 模型 ID
            tokens_needed: 预计需要的 token 数量（用于预检查）

        Returns:
            TeamModel: 团队模型授权记录

        Raises:
            QuotaExceededError: 配额超限
            ValueError: 找不到授权记录或模型已禁用
        """
        team_model = await self._get_team_model(team_id, model_id)

        if not team_model:
            raise ValueError(
                f"No authorization found for team {team_id} and model {model_id}"
            )

        if not team_model.is_enabled:
            raise ValueError(f"Model authorization is disabled for team {team_id}")

        # 检查并重置过期的用量
        daily_reset = await self._reset_daily_if_needed(team_model)
        monthly_reset = await self._reset_monthly_if_needed(team_model)

        if daily_reset or monthly_reset:
            await team_model.save()

        # 检查日 Token 配额
        if team_model.daily_token_limit is not None:
            if (
                team_model.daily_tokens_used + tokens_needed
                > team_model.daily_token_limit
            ):
                raise QuotaExceededError(
                    f"Daily token quota exceeded. "
                    f"Used: {team_model.daily_tokens_used}, "
                    f"Limit: {team_model.daily_token_limit}",
                    quota_type="daily_token",
                )

        # 检查月 Token 配额
        if team_model.monthly_token_limit is not None:
            if (
                team_model.monthly_tokens_used + tokens_needed
                > team_model.monthly_token_limit
            ):
                raise QuotaExceededError(
                    f"Monthly token quota exceeded. "
                    f"Used: {team_model.monthly_tokens_used}, "
                    f"Limit: {team_model.monthly_token_limit}",
                    quota_type="monthly_token",
                )

        # 检查日请求配额
        if team_model.daily_request_limit is not None:
            if team_model.daily_requests_used >= team_model.daily_request_limit:
                raise QuotaExceededError(
                    f"Daily request quota exceeded. "
                    f"Used: {team_model.daily_requests_used}, "
                    f"Limit: {team_model.daily_request_limit}",
                    quota_type="daily_request",
                )

        # 检查月请求配额
        if team_model.monthly_request_limit is not None:
            if team_model.monthly_requests_used >= team_model.monthly_request_limit:
                raise QuotaExceededError(
                    f"Monthly request quota exceeded. "
                    f"Used: {team_model.monthly_requests_used}, "
                    f"Limit: {team_model.monthly_request_limit}",
                    quota_type="monthly_request",
                )

        return team_model

    async def record_usage(
        self,
        team_id: str,
        model_id: str,
        tokens_used: int,
        request_count: int = 1,
    ) -> TeamModel:
        """
        记录用量（不检查配额）

        Args:
            team_id: 团队 ID
            model_id: 模型 ID
            tokens_used: 使用的 token 数量
            request_count: 请求次数

        Returns:
            TeamModel: 更新后的团队模型记录
        """
        team_model = await self._get_team_model(team_id, model_id)

        if not team_model:
            logger.warning(
                f"No authorization found for team {team_id} and model {model_id}, "
                f"skipping usage recording"
            )
            return None  # type: ignore

        # 检查并重置过期的用量
        await self._reset_daily_if_needed(team_model)
        await self._reset_monthly_if_needed(team_model)

        # 更新用量
        team_model.daily_tokens_used += tokens_used
        team_model.monthly_tokens_used += tokens_used
        team_model.daily_requests_used += request_count
        team_model.monthly_requests_used += request_count

        await team_model.save()

        logger.info(
            f"Recorded usage for team {team_id}, model {model_id}: "
            f"tokens={tokens_used}, requests={request_count}"
        )

        return team_model

    async def check_and_record_usage(
        self,
        team_id: str,
        model_id: str,
        tokens_used: int,
        request_count: int = 1,
    ) -> TeamModel:
        """
        检查配额并记录用量

        先检查配额是否足够，然后记录用量。

        Args:
            team_id: 团队 ID
            model_id: 模型 ID
            tokens_used: 使用的 token 数量
            request_count: 请求次数

        Returns:
            TeamModel: 更新后的团队模型记录

        Raises:
            QuotaExceededError: 配额超限
            ValueError: 找不到授权记录或模型已禁用
        """
        # 先检查配额
        team_model = await self.check_quota(team_id, model_id, tokens_used)

        # 更新用量
        team_model.daily_tokens_used += tokens_used
        team_model.monthly_tokens_used += tokens_used
        team_model.daily_requests_used += request_count
        team_model.monthly_requests_used += request_count

        await team_model.save()

        logger.info(
            f"Recorded usage for team {team_id}, model {model_id}: "
            f"tokens={tokens_used}, requests={request_count}"
        )

        return team_model

    async def get_usage_stats(self, team_id: str, model_id: str) -> Optional[dict]:
        """
        获取用量统计

        Args:
            team_id: 团队 ID
            model_id: 模型 ID

        Returns:
            用量统计字典，如果找不到记录则返回 None
        """
        team_model = await self._get_team_model(team_id, model_id)

        if not team_model:
            return None

        # 检查并重置过期的用量
        daily_reset = await self._reset_daily_if_needed(team_model)
        monthly_reset = await self._reset_monthly_if_needed(team_model)

        if daily_reset or monthly_reset:
            await team_model.save()

        return {
            "model_id": model_id,
            "model_name": team_model.model.name if team_model.model else None,
            "daily_tokens_used": team_model.daily_tokens_used,
            "daily_token_limit": team_model.daily_token_limit,
            "daily_token_percent": (
                round(
                    team_model.daily_tokens_used / team_model.daily_token_limit * 100, 2
                )
                if team_model.daily_token_limit
                else None
            ),
            "monthly_tokens_used": team_model.monthly_tokens_used,
            "monthly_token_limit": team_model.monthly_token_limit,
            "monthly_token_percent": (
                round(
                    team_model.monthly_tokens_used
                    / team_model.monthly_token_limit
                    * 100,
                    2,
                )
                if team_model.monthly_token_limit
                else None
            ),
            "daily_requests_used": team_model.daily_requests_used,
            "daily_request_limit": team_model.daily_request_limit,
            "monthly_requests_used": team_model.monthly_requests_used,
            "monthly_request_limit": team_model.monthly_request_limit,
            "is_enabled": team_model.is_enabled,
        }


# 全局单例
usage_tracker = UsageTracker()
