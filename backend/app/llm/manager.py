"""
统一模型管理器

提供统一的 LLM 调用接口，从数据库加载模型配置，
根据模型类型分发到对应的适配器。

支持团队级调用，自动追踪 token 用量和配额检查。
"""

import logging
import uuid
from collections.abc import AsyncIterator
from typing import Any

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    AIMessageChunk,
)

from app.models.model import Model, ModelType, TeamModel
from app.services.usage_tracker import usage_tracker, QuotaExceededError

from .adapters import (
    create_chat_model,
    create_embedding_model,
    create_image_adapter,
    create_tts_adapter,
    create_stt_adapter,
)
from .errors import (
    LLMError,
    ModelNotFoundError,
    ModelDisabledError,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    ContextLengthError,
    ContentFilterError,
    QuotaExceededError as LLMQuotaExceededError,
)
from .types import (
    Message,
    MessageRole,
    ChatResponse,
    ChatStreamChunk,
    ChatStreamDelta,
    FinishReason,
    Usage,
    ToolCall,
    FunctionCall,
    ToolDefinition,
    ImageGenerationRequest,
    ImageGenerationResponse,
    TTSRequest,
    TTSResponse,
    STTRequest,
    STTResponse,
)

logger = logging.getLogger(__name__)


class ModelManager:
    """
    统一模型管理器

    使用示例:
        from app.llm import model_manager

        # Chat
        response = await model_manager.chat(messages=[...])

        # Stream
        async for chunk in model_manager.chat_stream(messages=[...]):
            print(chunk.delta.content)

        # Embedding
        vectors = await model_manager.embed(["text1", "text2"])

        # 获取 LangChain 原生模型
        chat_model = await model_manager.get_chat_model()
    """

    # ==================== 内部辅助方法 ====================

    def _parse_model_identifier(
        self, identifier: str
    ) -> tuple[str | None, str | None, str | None]:
        """
        解析模型标识符

        支持的格式:
        - UUID: 数据库主键 (e.g., "550e8400-e29b-41d4-a716-446655440000")
        - 句柄: provider/model_id (e.g., "openai/gpt-4o")

        Args:
            identifier: 模型标识符

        Returns:
            (uuid, provider, model_id) 元组，未匹配的字段为 None
        """
        # 尝试解析为 UUID
        try:
            uuid.UUID(identifier)
            return (identifier, None, None)
        except ValueError:
            pass

        # 尝试解析为 provider/model_id 句柄
        if "/" in identifier:
            parts = identifier.split("/", 1)
            if len(parts) == 2:
                provider, model_id = parts
                return (None, provider, model_id)

        # 不支持单独的 model_id，因为它不是唯一的
        return (None, None, None)

    async def _get_model_config(
        self, model_id: str | None = None, model_type: ModelType = ModelType.CHAT
    ) -> Model:
        """
        获取模型配置

        Args:
            model_id: 模型标识符，支持以下格式：
                - UUID: 数据库主键
                - 句柄: "provider/model_id" 格式 (e.g., "openai/gpt-4o")
                - None: 使用该类型的默认模型
            model_type: 模型类型，仅在获取默认模型时使用

        Returns:
            Model: 模型配置对象

        Raises:
            ModelNotFoundError: 找不到模型或标识符格式无效
            ModelDisabledError: 模型已禁用
        """
        model: Model | None = None

        if model_id:
            parsed_uuid, provider, parsed_model_id = self._parse_model_identifier(
                model_id
            )

            if parsed_uuid:
                # 按 UUID 查找
                model = await Model.filter(id=parsed_uuid).first()
            elif provider and parsed_model_id:
                # 按 provider/model_id 句柄查找
                model = await Model.filter(
                    provider=provider, model_id=parsed_model_id
                ).first()
            else:
                # 无效的标识符格式
                raise ModelNotFoundError(
                    message=f"Invalid model identifier format: '{model_id}'. "
                    f"Use UUID or 'provider/model_id' format (e.g., 'openai/gpt-4o')",
                    model=model_id,
                )
        else:
            # 获取该类型的默认模型
            model = await Model.filter(model_type=model_type, is_default=True).first()
            if not model:
                # 如果没有默认模型，获取第一个启用的模型
                model = await Model.filter(
                    model_type=model_type, is_enabled=True
                ).first()

        if not model:
            raise ModelNotFoundError(
                message=f"No model found for identifier: {model_id or model_type}",
                model=model_id,
            )

        if not model.is_enabled:
            raise ModelDisabledError(
                message=f"Model {model.name} is disabled",
                model=str(model.id),
            )

        return model

    def _convert_messages(
        self, messages: list[Message]
    ) -> list[SystemMessage | HumanMessage | AIMessage | ToolMessage]:
        """将内部消息格式转换为 LangChain 消息"""
        lc_messages: list[SystemMessage | HumanMessage | AIMessage | ToolMessage] = []
        for msg in messages:
            content = msg.content
            if isinstance(content, list):
                # TODO: 处理多模态内容
                content = " ".join(part.text for part in content if part.text)

            if msg.role == MessageRole.SYSTEM:
                lc_messages.append(SystemMessage(content=content or ""))
            elif msg.role == MessageRole.USER:
                lc_messages.append(HumanMessage(content=content or ""))
            elif msg.role == MessageRole.ASSISTANT:
                lc_messages.append(AIMessage(content=content or ""))
            elif msg.role == MessageRole.TOOL:
                lc_messages.append(
                    ToolMessage(
                        content=content or "",
                        tool_call_id=msg.tool_call_id or "",
                    )
                )

        return lc_messages

    def _convert_tools(self, tools: list[ToolDefinition] | None) -> list[dict] | None:
        """将内部工具定义转换为 LangChain 格式"""
        if not tools:
            return None

        return [
            {
                "type": tool.type,
                "function": {
                    "name": tool.function.name,
                    "description": tool.function.description or "",
                    "parameters": tool.function.parameters,
                },
            }
            for tool in tools
        ]

    def _parse_response(self, response: AIMessage, model_name: str) -> ChatResponse:
        """解析 LangChain 响应为内部格式"""
        # 解析工具调用
        tool_calls = None
        if response.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.get("id") or str(uuid.uuid4()),
                    type="function",
                    function=FunctionCall(
                        name=tc.get("name", ""),
                        arguments=str(tc.get("args", "{}")),
                    ),
                )
                for tc in response.tool_calls
            ]

        # 确定完成原因
        finish_reason = FinishReason.STOP
        if tool_calls:
            finish_reason = FinishReason.TOOL_CALLS

        # 解析 usage
        usage = Usage()
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = Usage(
                prompt_tokens=response.usage_metadata.get("input_tokens", 0),
                completion_tokens=response.usage_metadata.get("output_tokens", 0),
                total_tokens=response.usage_metadata.get("total_tokens", 0),
            )

        return ChatResponse(
            id=response.id or str(uuid.uuid4()),
            model=model_name,
            content=response.content if isinstance(response.content, str) else None,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            usage=usage,
        )

    def _handle_error(self, e: Exception, provider: str, model: str) -> LLMError:
        """统一处理异常"""
        error_msg = str(e).lower()

        if (
            "authentication" in error_msg
            or "api key" in error_msg
            or "invalid_api_key" in error_msg
        ):
            return AuthenticationError(
                message=str(e),
                provider=provider,
                model=model,
            )
        elif "rate limit" in error_msg or "rate_limit" in error_msg:
            return RateLimitError(
                message=str(e),
                provider=provider,
                model=model,
            )
        elif (
            "context length" in error_msg or "token" in error_msg and "max" in error_msg
        ):
            return ContextLengthError(
                message=str(e),
                provider=provider,
                model=model,
            )
        elif "content filter" in error_msg or "safety" in error_msg:
            return ContentFilterError(
                message=str(e),
                provider=provider,
                model=model,
            )
        else:
            return ProviderError(
                message=str(e),
                provider=provider,
                model=model,
            )

    async def _get_team_model(
        self, team_id: str, model_id: str
    ) -> tuple[Model, TeamModel]:
        """
        获取团队授权的模型

        Args:
            team_id: 团队 ID
            model_id: 模型标识符

        Returns:
            (Model, TeamModel) 元组

        Raises:
            ModelNotFoundError: 找不到模型或团队未授权该模型
            ModelDisabledError: 模型或团队授权已禁用
        """
        # 先获取模型配置
        model_config = await self._get_model_config(model_id)

        # 查找团队授权
        team_model = await TeamModel.filter(
            team_id=team_id, model_id=model_config.id
        ).first()

        if not team_model:
            raise ModelNotFoundError(
                message=f"Team {team_id} is not authorized to use model {model_config.name}",
                model=str(model_config.id),
            )

        if not team_model.is_enabled:
            raise ModelDisabledError(
                message=f"Model {model_config.name} is disabled for team {team_id}",
                model=str(model_config.id),
            )

        return model_config, team_model

    async def _check_and_record_usage(
        self,
        team_id: str,
        model_id: str,
        tokens_used: int,
        request_count: int = 1,
    ) -> None:
        """
        检查配额并记录用量

        Args:
            team_id: 团队 ID
            model_id: 模型 UUID
            tokens_used: 使用的 token 数
            request_count: 请求次数
        """
        try:
            await usage_tracker.check_and_record_usage(
                team_id=team_id,
                model_id=model_id,
                tokens_used=tokens_used,
                request_count=request_count,
            )
        except QuotaExceededError as e:
            raise LLMQuotaExceededError(
                message=str(e),
                quota_type=e.quota_type,
                team_id=team_id,
                model=model_id,
            )

    # ==================== Chat 方法 ====================

    async def chat(
        self,
        messages: list[Message | dict],
        model_id: str | None = None,
        tools: list[ToolDefinition] | None = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """
        Chat 调用

        Args:
            messages: 消息列表，可以是 Message 对象或 dict
            model_id: 模型 ID（数据库主键或 model_id 字段），不指定则使用默认
            tools: 工具定义列表
            **kwargs: 额外参数传递给模型

        Returns:
            ChatResponse: 响应对象
        """
        # 转换 dict 为 Message
        converted_messages: list[Message] = [
            Message(**m) if isinstance(m, dict) else m for m in messages
        ]

        model_config = await self._get_model_config(model_id, ModelType.CHAT)
        chat_model = create_chat_model(model_config)

        lc_messages = self._convert_messages(converted_messages)
        lc_tools = self._convert_tools(tools)

        try:
            model_to_invoke: BaseChatModel = chat_model
            if lc_tools:
                model_to_invoke = chat_model.bind_tools(lc_tools)  # type: ignore[assignment]

            response = await model_to_invoke.ainvoke(lc_messages, **kwargs)
            return self._parse_response(response, model_config.model_id)
        except Exception as e:
            logger.exception(f"Chat error: {e}")
            raise self._handle_error(e, model_config.provider, model_config.model_id)

    async def chat_stream(
        self,
        messages: list[Message | dict],
        model_id: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatStreamChunk]:
        """
        Chat 流式调用

        Args:
            messages: 消息列表
            model_id: 模型 ID
            **kwargs: 额外参数

        Yields:
            ChatStreamChunk: 流式响应块
        """
        converted_messages: list[Message] = [
            Message(**m) if isinstance(m, dict) else m for m in messages
        ]

        model_config = await self._get_model_config(model_id, ModelType.CHAT)
        chat_model = create_chat_model(model_config)

        lc_messages = self._convert_messages(converted_messages)

        try:
            response_id = str(uuid.uuid4())
            async for chunk in chat_model.astream(lc_messages, **kwargs):
                if isinstance(chunk, AIMessageChunk):
                    yield ChatStreamChunk(
                        id=response_id,
                        model=model_config.model_id,
                        delta=ChatStreamDelta(
                            content=chunk.content
                            if isinstance(chunk.content, str)
                            else None,
                        ),
                        finish_reason=None,
                    )

            # 最后一个块带 finish_reason
            yield ChatStreamChunk(
                id=response_id,
                model=model_config.model_id,
                delta=ChatStreamDelta(),
                finish_reason=FinishReason.STOP,
            )
        except Exception as e:
            logger.exception(f"Chat stream error: {e}")
            raise self._handle_error(e, model_config.provider, model_config.model_id)

    async def get_chat_model(self, model_id: str | None = None) -> BaseChatModel:
        """
        获取 LangChain Chat 模型实例，用于高级用法

        Args:
            model_id: 模型 ID

        Returns:
            BaseChatModel: LangChain 模型实例
        """
        model_config = await self._get_model_config(model_id, ModelType.CHAT)
        return create_chat_model(model_config)

    # ==================== Embedding 方法 ====================

    async def embed(
        self,
        texts: list[str],
        model_id: str | None = None,
    ) -> list[list[float]]:
        """
        文本嵌入

        Args:
            texts: 文本列表
            model_id: 模型 ID

        Returns:
            list[list[float]]: 嵌入向量列表
        """
        model_config = await self._get_model_config(model_id, ModelType.EMBEDDING)
        embedding_model = create_embedding_model(model_config)

        try:
            return await embedding_model.aembed_documents(texts)
        except Exception as e:
            logger.exception(f"Embedding error: {e}")
            raise self._handle_error(e, model_config.provider, model_config.model_id)

    async def embed_query(
        self,
        text: str,
        model_id: str | None = None,
    ) -> list[float]:
        """
        单个查询文本嵌入

        Args:
            text: 文本
            model_id: 模型 ID

        Returns:
            list[float]: 嵌入向量
        """
        model_config = await self._get_model_config(model_id, ModelType.EMBEDDING)
        embedding_model = create_embedding_model(model_config)

        try:
            return await embedding_model.aembed_query(text)
        except Exception as e:
            logger.exception(f"Embed query error: {e}")
            raise self._handle_error(e, model_config.provider, model_config.model_id)

    async def get_embedding_model(self, model_id: str | None = None) -> Embeddings:
        """
        获取 LangChain Embedding 模型实例

        Args:
            model_id: 模型 ID

        Returns:
            Embeddings: LangChain Embedding 模型实例
        """
        model_config = await self._get_model_config(model_id, ModelType.EMBEDDING)
        return create_embedding_model(model_config)

    # ==================== Image 方法 ====================

    async def generate_image(
        self,
        request: ImageGenerationRequest | dict,
        model_id: str | None = None,
    ) -> ImageGenerationResponse:
        """
        图像生成

        Args:
            request: 图像生成请求
            model_id: 模型 ID

        Returns:
            ImageGenerationResponse: 生成结果
        """
        if isinstance(request, dict):
            request = ImageGenerationRequest(**request)

        model_config = await self._get_model_config(model_id, ModelType.TEXT_TO_IMAGE)
        adapter = create_image_adapter(model_config)

        try:
            return await adapter.generate(request)
        except LLMError:
            raise
        except Exception as e:
            logger.exception(f"Image generation error: {e}")
            raise self._handle_error(e, model_config.provider, model_config.model_id)

    # ==================== Audio 方法 ====================

    async def text_to_speech(
        self,
        request: TTSRequest | dict,
        model_id: str | None = None,
    ) -> TTSResponse:
        """
        语音合成

        Args:
            request: TTS 请求
            model_id: 模型 ID

        Returns:
            TTSResponse: 合成结果
        """
        if isinstance(request, dict):
            request = TTSRequest(**request)

        model_config = await self._get_model_config(model_id, ModelType.TTS)
        adapter = create_tts_adapter(model_config)

        try:
            return await adapter.synthesize(request)
        except LLMError:
            raise
        except Exception as e:
            logger.exception(f"TTS error: {e}")
            raise self._handle_error(e, model_config.provider, model_config.model_id)

    async def speech_to_text(
        self,
        request: STTRequest | dict,
        model_id: str | None = None,
    ) -> STTResponse:
        """
        语音识别

        Args:
            request: STT 请求
            model_id: 模型 ID

        Returns:
            STTResponse: 识别结果
        """
        if isinstance(request, dict):
            request = STTRequest(**request)

        model_config = await self._get_model_config(model_id, ModelType.STT)
        adapter = create_stt_adapter(model_config)

        try:
            return await adapter.transcribe(request)
        except LLMError:
            raise
        except Exception as e:
            logger.exception(f"STT error: {e}")
            raise self._handle_error(e, model_config.provider, model_config.model_id)

    # ==================== 团队级 Chat 方法 (带用量追踪) ====================

    async def team_chat(
        self,
        team_id: str,
        messages: list[Message | dict],
        model_id: str | None = None,
        tools: list[ToolDefinition] | None = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """
        团队级 Chat 调用（带配额检查和用量追踪）

        Args:
            team_id: 团队 ID
            messages: 消息列表
            model_id: 模型 ID
            tools: 工具定义列表
            **kwargs: 额外参数

        Returns:
            ChatResponse: 响应对象

        Raises:
            QuotaExceededError: 配额超限
            ModelNotFoundError: 团队未授权该模型
        """
        # 获取团队授权的模型
        model_config, team_model = await self._get_team_model(team_id, model_id or "")

        # 检查配额（预检查，确保有足够配额再调用）
        try:
            await usage_tracker.check_quota(
                team_id=team_id,
                model_id=str(model_config.id),
            )
        except QuotaExceededError as e:
            raise LLMQuotaExceededError(
                message=str(e),
                quota_type=e.quota_type,
                team_id=team_id,
                model=str(model_config.id),
            )

        # 调用模型
        converted_messages: list[Message] = [
            Message(**m) if isinstance(m, dict) else m for m in messages
        ]

        chat_model = create_chat_model(model_config)
        lc_messages = self._convert_messages(converted_messages)
        lc_tools = self._convert_tools(tools)

        try:
            model_to_invoke: BaseChatModel = chat_model
            if lc_tools:
                model_to_invoke = chat_model.bind_tools(lc_tools)  # type: ignore[assignment]

            response = await model_to_invoke.ainvoke(lc_messages, **kwargs)
            result = self._parse_response(response, model_config.model_id)

            # 记录用量
            await self._check_and_record_usage(
                team_id=team_id,
                model_id=str(model_config.id),
                tokens_used=result.usage.total_tokens if result.usage else 0,
            )

            return result
        except Exception as e:
            logger.exception(f"Team chat error: {e}")
            raise self._handle_error(e, model_config.provider, model_config.model_id)

    async def team_chat_stream(
        self,
        team_id: str,
        messages: list[Message | dict],
        model_id: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatStreamChunk]:
        """
        团队级 Chat 流式调用（带配额检查和用量追踪）

        注意：流式调用无法准确追踪 token 用量，
        会在流结束后估算一个 token 数并记录。

        Args:
            team_id: 团队 ID
            messages: 消息列表
            model_id: 模型 ID
            **kwargs: 额外参数

        Yields:
            ChatStreamChunk: 流式响应块
        """
        # 获取团队授权的模型
        model_config, team_model = await self._get_team_model(team_id, model_id or "")

        # 检查配额
        try:
            await usage_tracker.check_quota(
                team_id=team_id,
                model_id=str(model_config.id),
            )
        except QuotaExceededError as e:
            raise LLMQuotaExceededError(
                message=str(e),
                quota_type=e.quota_type,
                team_id=team_id,
                model=str(model_config.id),
            )

        converted_messages: list[Message] = [
            Message(**m) if isinstance(m, dict) else m for m in messages
        ]

        chat_model = create_chat_model(model_config)
        lc_messages = self._convert_messages(converted_messages)

        try:
            response_id = str(uuid.uuid4())
            total_content = ""

            async for chunk in chat_model.astream(lc_messages, **kwargs):
                if isinstance(chunk, AIMessageChunk):
                    content = chunk.content if isinstance(chunk.content, str) else ""
                    total_content += content
                    yield ChatStreamChunk(
                        id=response_id,
                        model=model_config.model_id,
                        delta=ChatStreamDelta(content=content or None),
                        finish_reason=None,
                    )

            # 估算 token 用量（简单估算：4 字符约 1 token）
            # 计算输入 token（所有消息内容）
            input_chars = sum(
                len(m.content or "") if isinstance(m.content, str) else 0
                for m in converted_messages
            )
            input_tokens = max(input_chars // 4, 1)
            output_tokens = max(len(total_content) // 4, 1)
            total_tokens = input_tokens + output_tokens

            # 记录用量
            await self._check_and_record_usage(
                team_id=team_id,
                model_id=str(model_config.id),
                tokens_used=total_tokens,
            )

            # 最后一个块带 finish_reason
            yield ChatStreamChunk(
                id=response_id,
                model=model_config.model_id,
                delta=ChatStreamDelta(),
                finish_reason=FinishReason.STOP,
            )
        except Exception as e:
            logger.exception(f"Team chat stream error: {e}")
            raise self._handle_error(e, model_config.provider, model_config.model_id)

    async def team_embed(
        self,
        team_id: str,
        texts: list[str],
        model_id: str | None = None,
    ) -> list[list[float]]:
        """
        团队级文本嵌入（带配额检查和用量追踪）

        Args:
            team_id: 团队 ID
            texts: 文本列表
            model_id: 模型 ID

        Returns:
            list[list[float]]: 嵌入向量列表
        """
        # 获取团队授权的模型
        model_config, team_model = await self._get_team_model(team_id, model_id or "")

        # 检查配额
        try:
            await usage_tracker.check_quota(
                team_id=team_id,
                model_id=str(model_config.id),
            )
        except QuotaExceededError as e:
            raise LLMQuotaExceededError(
                message=str(e),
                quota_type=e.quota_type,
                team_id=team_id,
                model=str(model_config.id),
            )

        embedding_model = create_embedding_model(model_config)

        try:
            result = await embedding_model.aembed_documents(texts)

            # 估算 token 用量（embedding 模型按字符数估算）
            total_chars = sum(len(t) for t in texts)
            total_tokens = max(total_chars // 4, 1)

            # 记录用量
            await self._check_and_record_usage(
                team_id=team_id,
                model_id=str(model_config.id),
                tokens_used=total_tokens,
            )

            return result
        except Exception as e:
            logger.exception(f"Team embedding error: {e}")
            raise self._handle_error(e, model_config.provider, model_config.model_id)


# 全局单例
model_manager = ModelManager()
