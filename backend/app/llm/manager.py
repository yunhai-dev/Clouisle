"""
统一模型管理器

提供统一的 LLM 调用接口，从数据库加载模型配置，
根据模型类型分发到对应的适配器。
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

from app.models.model import Model, ModelType

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

    async def _get_model_config(
        self, model_id: str | None = None, model_type: ModelType = ModelType.CHAT
    ) -> Model:
        """获取模型配置"""
        if model_id:
            model = await Model.filter(id=model_id).first()
            if not model:
                # 尝试按 model_id 字段查找
                model = await Model.filter(model_id=model_id, model_type=model_type).first()
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
                message=f"No model found for type: {model_type}",
                model=model_id,
            )

        if not model.is_enabled:
            raise ModelDisabledError(
                message=f"Model {model.name} is disabled",
                model=str(model.id),
            )

        return model

    def _convert_messages(self, messages: list[Message]) -> list:
        """将内部消息格式转换为 LangChain 消息"""
        lc_messages = []
        for msg in messages:
            content = msg.content
            if isinstance(content, list):
                # TODO: 处理多模态内容
                content = " ".join(
                    part.text for part in content if part.text
                )

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
                    id=tc.get("id", str(uuid.uuid4())),
                    type="function",
                    function=FunctionCall(
                        name=tc.get("name", ""),
                        arguments=tc.get("args", "{}") if isinstance(tc.get("args"), str)
                        else str(tc.get("args", {})),
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

        if "authentication" in error_msg or "api key" in error_msg or "invalid_api_key" in error_msg:
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
        elif "context length" in error_msg or "token" in error_msg and "max" in error_msg:
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
        messages = [
            Message(**m) if isinstance(m, dict) else m
            for m in messages
        ]

        model_config = await self._get_model_config(model_id, ModelType.CHAT)
        chat_model = create_chat_model(model_config)

        lc_messages = self._convert_messages(messages)
        lc_tools = self._convert_tools(tools)

        try:
            if lc_tools:
                chat_model = chat_model.bind_tools(lc_tools)

            response = await chat_model.ainvoke(lc_messages, **kwargs)
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
        messages = [
            Message(**m) if isinstance(m, dict) else m
            for m in messages
        ]

        model_config = await self._get_model_config(model_id, ModelType.CHAT)
        chat_model = create_chat_model(model_config)

        lc_messages = self._convert_messages(messages)

        try:
            response_id = str(uuid.uuid4())
            async for chunk in chat_model.astream(lc_messages, **kwargs):
                if isinstance(chunk, AIMessageChunk):
                    yield ChatStreamChunk(
                        id=response_id,
                        model=model_config.model_id,
                        delta=ChatStreamDelta(
                            content=chunk.content if isinstance(chunk.content, str) else None,
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


# 全局单例
model_manager = ModelManager()
