"""
音频适配器
"""

from app.models.model import Model, ModelProvider
from app.llm.errors import UnsupportedOperationError

from .base import BaseTTSAdapter, BaseSTTAdapter
from .openai_tts import OpenAITTSAdapter
from .openai_stt import OpenAISTTAdapter


def create_tts_adapter(model_config: Model) -> BaseTTSAdapter:
    """
    创建 TTS 适配器

    Args:
        model_config: 模型配置

    Returns:
        BaseTTSAdapter: TTS 适配器
    """
    provider = model_config.provider

    if provider == ModelProvider.OPENAI:
        return OpenAITTSAdapter(model_config)
    elif provider == ModelProvider.AZURE_OPENAI:
        return OpenAITTSAdapter(model_config)
    else:
        raise UnsupportedOperationError(
            message=f"TTS not supported for provider: {provider}",
            operation="text_to_speech",
            provider=provider,
        )


def create_stt_adapter(model_config: Model) -> BaseSTTAdapter:
    """
    创建 STT 适配器

    Args:
        model_config: 模型配置

    Returns:
        BaseSTTAdapter: STT 适配器
    """
    provider = model_config.provider

    if provider == ModelProvider.OPENAI:
        return OpenAISTTAdapter(model_config)
    elif provider == ModelProvider.AZURE_OPENAI:
        return OpenAISTTAdapter(model_config)
    else:
        raise UnsupportedOperationError(
            message=f"STT not supported for provider: {provider}",
            operation="speech_to_text",
            provider=provider,
        )


__all__ = [
    "create_tts_adapter",
    "create_stt_adapter",
    "BaseTTSAdapter",
    "BaseSTTAdapter",
    "OpenAITTSAdapter",
    "OpenAISTTAdapter",
]
