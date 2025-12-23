"""
图像生成适配器
"""
from app.models.model import Model, ModelProvider
from app.llm.errors import UnsupportedOperationError

from .base import BaseImageAdapter
from .openai import OpenAIImageAdapter


def create_image_adapter(model_config: Model) -> BaseImageAdapter:
    """
    创建图像生成适配器

    Args:
        model_config: 模型配置

    Returns:
        BaseImageAdapter: 图像生成适配器
    """
    provider = model_config.provider

    if provider == ModelProvider.OPENAI:
        return OpenAIImageAdapter(model_config)
    elif provider == ModelProvider.AZURE_OPENAI:
        # Azure OpenAI 使用相同的适配器，只是 base_url 不同
        return OpenAIImageAdapter(model_config)
    else:
        raise UnsupportedOperationError(
            message=f"Image generation not supported for provider: {provider}",
            operation="generate_image",
            provider=provider,
        )


__all__ = ["create_image_adapter", "BaseImageAdapter", "OpenAIImageAdapter"]
