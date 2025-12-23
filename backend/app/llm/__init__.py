"""
Clouisle LLM 调用模块

提供统一的 LLM 调用接口。

使用示例:
    from app.llm import model_manager

    # Chat 调用
    response = await model_manager.chat(
        messages=[{"role": "user", "content": "Hello!"}]
    )

    # 流式调用
    async for chunk in model_manager.chat_stream(messages):
        print(chunk.delta.content, end="")

    # Embedding
    vectors = await model_manager.embed(["text1", "text2"])

    # 图像生成
    result = await model_manager.generate_image({"prompt": "A cat"})

    # TTS
    audio = await model_manager.text_to_speech({"text": "Hello!"})

    # STT
    text = await model_manager.speech_to_text({"audio": {...}})

    # 获取 LangChain 原生模型 (用于 LangGraph 等高级场景)
    chat_model = await model_manager.get_chat_model()
"""
from .manager import model_manager, ModelManager
from .errors import (
    LLMError,
    AuthenticationError,
    RateLimitError,
    ContextLengthError,
    ContentFilterError,
    ModelNotFoundError,
    ModelDisabledError,
    ProviderError,
    TimeoutError,
    InvalidRequestError,
    InsufficientQuotaError,
    TaskNotFoundError,
    UnsupportedOperationError,
)
from .types import (
    # Base
    MediaContent,
    ImageContent,
    VideoContent,
    AudioContent,
    ContentType,
    ContentPart,
    Usage,
    TaskStatus,
    # Chat
    MessageRole,
    Message,
    ToolCall,
    FunctionCall,
    ToolDefinition,
    FunctionDefinition,
    FinishReason,
    ChatRequest,
    ChatResponse,
    ChatStreamDelta,
    ChatStreamChunk,
    # Image
    ImageGenerationRequest,
    ImageGenerationResponse,
    GeneratedImage,
    # Video
    VideoGenerationRequest,
    VideoGenerationResponse,
    # Audio
    TTSRequest,
    TTSResponse,
    STTRequest,
    STTResponse,
)
from .tools import tool_registry, ToolRegistry, ToolInfo, ToolParameter

__all__ = [
    # Manager
    "model_manager",
    "ModelManager",
    # Errors
    "LLMError",
    "AuthenticationError",
    "RateLimitError",
    "ContextLengthError",
    "ContentFilterError",
    "ModelNotFoundError",
    "ModelDisabledError",
    "ProviderError",
    "TimeoutError",
    "InvalidRequestError",
    "InsufficientQuotaError",
    "TaskNotFoundError",
    "UnsupportedOperationError",
    # Base Types
    "MediaContent",
    "ImageContent",
    "VideoContent",
    "AudioContent",
    "ContentType",
    "ContentPart",
    "Usage",
    "TaskStatus",
    # Chat Types
    "MessageRole",
    "Message",
    "ToolCall",
    "FunctionCall",
    "ToolDefinition",
    "FunctionDefinition",
    "FinishReason",
    "ChatRequest",
    "ChatResponse",
    "ChatStreamDelta",
    "ChatStreamChunk",
    # Image Types
    "ImageGenerationRequest",
    "ImageGenerationResponse",
    "GeneratedImage",
    # Video Types
    "VideoGenerationRequest",
    "VideoGenerationResponse",
    # Audio Types
    "TTSRequest",
    "TTSResponse",
    "STTRequest",
    "STTResponse",
    # Tools
    "tool_registry",
    "ToolRegistry",
    "ToolInfo",
    "ToolParameter",
]
