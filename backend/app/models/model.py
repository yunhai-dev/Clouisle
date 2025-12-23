"""
AI Model management models.
Supports various model types: chat, embedding, text-to-image, text-to-video, etc.
"""

from enum import Enum

from tortoise import fields, models


class ModelProvider(str, Enum):
    """Supported model providers"""

    # General LLM providers
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure_openai"
    DEEPSEEK = "deepseek"
    MOONSHOT = "moonshot"
    ZHIPU = "zhipu"
    QWEN = "qwen"
    BAICHUAN = "baichuan"
    MINIMAX = "minimax"

    # Local deployment
    OLLAMA = "ollama"

    # Video generation
    RUNWAY = "runway"
    PIKA = "pika"
    LUMA = "luma"
    KLING = "kling"

    # Image generation
    STABILITY = "stability"
    MIDJOURNEY = "midjourney"

    # Custom provider
    CUSTOM = "custom"


class ModelType(str, Enum):
    """Model type classification"""

    CHAT = "chat"  # Chat/completion models
    EMBEDDING = "embedding"  # Text embedding models
    RERANK = "rerank"  # Reranking models
    TTS = "tts"  # Text-to-speech
    STT = "stt"  # Speech-to-text
    TEXT_TO_IMAGE = "text_to_image"  # Text-to-image generation
    TEXT_TO_VIDEO = "text_to_video"  # Text-to-video generation
    IMAGE_TO_VIDEO = "image_to_video"  # Image-to-video generation


# Provider default configurations (base URLs, etc.)
PROVIDER_DEFAULTS = {
    ModelProvider.OPENAI: {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "icon": "openai",
    },
    ModelProvider.ANTHROPIC: {
        "name": "Anthropic",
        "base_url": "https://api.anthropic.com",
        "icon": "anthropic",
    },
    ModelProvider.GOOGLE: {
        "name": "Google AI",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "icon": "google",
    },
    ModelProvider.AZURE_OPENAI: {
        "name": "Azure OpenAI",
        "base_url": None,  # User must configure
        "icon": "azure",
    },
    ModelProvider.DEEPSEEK: {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "icon": "deepseek",
    },
    ModelProvider.MOONSHOT: {
        "name": "Moonshot",
        "base_url": "https://api.moonshot.cn/v1",
        "icon": "moonshot",
    },
    ModelProvider.ZHIPU: {
        "name": "Zhipu AI",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "icon": "zhipu",
    },
    ModelProvider.QWEN: {
        "name": "Qwen",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "icon": "qwen",
    },
    ModelProvider.BAICHUAN: {
        "name": "Baichuan",
        "base_url": "https://api.baichuan-ai.com/v1",
        "icon": "baichuan",
    },
    ModelProvider.MINIMAX: {
        "name": "MiniMax",
        "base_url": "https://api.minimax.chat/v1",
        "icon": "minimax",
    },
    ModelProvider.OLLAMA: {
        "name": "Ollama",
        "base_url": "http://localhost:11434",
        "icon": "ollama",
    },
    ModelProvider.RUNWAY: {
        "name": "Runway",
        "base_url": "https://api.runwayml.com/v1",
        "icon": "runway",
    },
    ModelProvider.PIKA: {
        "name": "Pika",
        "base_url": "https://api.pika.art/v1",
        "icon": "pika",
    },
    ModelProvider.LUMA: {
        "name": "Luma AI",
        "base_url": "https://api.lumalabs.ai",
        "icon": "luma",
    },
    ModelProvider.KLING: {
        "name": "Kling",
        "base_url": "https://api.klingai.com",
        "icon": "kling",
    },
    ModelProvider.STABILITY: {
        "name": "Stability AI",
        "base_url": "https://api.stability.ai/v1",
        "icon": "stability",
    },
    ModelProvider.MIDJOURNEY: {
        "name": "Midjourney",
        "base_url": None,  # Proxy required
        "icon": "midjourney",
    },
    ModelProvider.CUSTOM: {
        "name": "Custom",
        "base_url": None,
        "icon": "custom",
    },
}


class Model(models.Model):
    """
    AI Model configuration.

    Stores model information including provider, API credentials,
    capabilities, and default inference parameters.
    """

    id = fields.UUIDField(pk=True)

    # Basic info
    name = fields.CharField(max_length=100, description="Display name")
    provider = fields.CharField(
        max_length=30, description="Provider identifier (openai, anthropic, etc.)"
    )
    model_id = fields.CharField(
        max_length=100, description="Model identifier (gpt-4o, claude-3-5-sonnet, etc.)"
    )
    model_type = fields.CharField(
        max_length=20, description="Model type (chat, embedding, text_to_image, etc.)"
    )

    # API configuration
    base_url = fields.CharField(
        max_length=512, null=True, description="Custom API base URL"
    )
    api_key = fields.CharField(
        max_length=1024, null=True, description="Encrypted API key"
    )

    # Model specifications
    context_length = fields.IntField(null=True, description="Maximum context length")
    max_output_tokens = fields.IntField(null=True, description="Maximum output tokens")

    # Pricing (per million tokens)
    input_price = fields.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        description="Input price per 1M tokens",
    )
    output_price = fields.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        description="Output price per 1M tokens",
    )

    # JSON fields for flexible configuration
    default_params = fields.JSONField(
        null=True,
        description="Default inference parameters (temperature, top_p, etc.)",
    )
    capabilities = fields.JSONField(
        null=True,
        description="Model capabilities (vision, function_call, streaming, etc.)",
    )
    config = fields.JSONField(
        null=True,
        description="Additional configuration (api_version, deployment_name, etc.)",
    )

    # Status
    is_enabled = fields.BooleanField(
        default=True, description="Whether model is enabled"
    )
    is_default = fields.BooleanField(
        default=False, description="Whether this is the default model for its type"
    )
    sort_order = fields.IntField(default=0, description="Sort order")

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "models"
        unique_together = (("provider", "model_id"),)
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return f"{self.name} ({self.provider}/{self.model_id})"

    @property
    def has_api_key(self) -> bool:
        """Check if API key is configured (without exposing the actual key)"""
        return bool(self.api_key)

    def get_effective_base_url(self) -> str | None:
        """Get the effective base URL (custom or provider default)"""
        if self.base_url:
            return self.base_url
        try:
            provider_enum = ModelProvider(self.provider)
            return PROVIDER_DEFAULTS.get(provider_enum, {}).get("base_url")
        except ValueError:
            return None
