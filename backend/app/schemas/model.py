"""
Pydantic schemas for AI Model management.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ModelProvider(str, Enum):
    """Supported model providers"""

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
    OLLAMA = "ollama"
    RUNWAY = "runway"
    PIKA = "pika"
    LUMA = "luma"
    KLING = "kling"
    STABILITY = "stability"
    MIDJOURNEY = "midjourney"
    CUSTOM = "custom"


class ModelType(str, Enum):
    """Model type classification"""

    CHAT = "chat"
    EMBEDDING = "embedding"
    RERANK = "rerank"
    TTS = "tts"
    STT = "stt"
    TEXT_TO_IMAGE = "text_to_image"
    TEXT_TO_VIDEO = "text_to_video"
    IMAGE_TO_VIDEO = "image_to_video"


class ProviderInfo(BaseModel):
    """Provider information for frontend display"""

    code: str
    name: str
    base_url: Optional[str] = None
    icon: str


# ============ Request Schemas ============


class ModelCreate(BaseModel):
    """Schema for creating a new model"""

    name: str = Field(..., min_length=1, max_length=100, description="Display name")
    provider: ModelProvider = Field(..., description="Provider identifier")
    model_id: str = Field(
        ..., min_length=1, max_length=100, description="Model identifier"
    )
    model_type: ModelType = Field(..., description="Model type")
    base_url: Optional[str] = Field(None, max_length=512, description="Custom API URL")
    api_key: str = Field(
        ..., min_length=1, max_length=1024, description="API key (required)"
    )
    context_length: Optional[int] = Field(None, ge=1, description="Context length")
    max_output_tokens: Optional[int] = Field(
        None, ge=1, description="Max output tokens"
    )
    input_price: Optional[Decimal] = Field(
        None, ge=0, decimal_places=6, description="Input price per 1M tokens"
    )
    output_price: Optional[Decimal] = Field(
        None, ge=0, decimal_places=6, description="Output price per 1M tokens"
    )
    default_params: Optional[dict[str, Any]] = Field(
        None, description="Default inference parameters"
    )
    capabilities: Optional[dict[str, Any]] = Field(
        None, description="Model capabilities"
    )
    config: Optional[dict[str, Any]] = Field(
        None, description="Additional configuration"
    )
    is_enabled: bool = Field(True, description="Whether model is enabled")
    is_default: bool = Field(False, description="Whether this is the default model")
    sort_order: int = Field(0, description="Sort order")


class ModelUpdate(BaseModel):
    """Schema for updating a model"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    base_url: Optional[str] = Field(None, max_length=512)
    api_key: Optional[str] = Field(
        None, max_length=1024, description="Empty string to clear"
    )
    context_length: Optional[int] = Field(None, ge=1)
    max_output_tokens: Optional[int] = Field(None, ge=1)
    input_price: Optional[Decimal] = Field(None, ge=0, decimal_places=6)
    output_price: Optional[Decimal] = Field(None, ge=0, decimal_places=6)
    default_params: Optional[dict[str, Any]] = None
    capabilities: Optional[dict[str, Any]] = None
    config: Optional[dict[str, Any]] = None
    is_enabled: Optional[bool] = None
    is_default: Optional[bool] = None
    sort_order: Optional[int] = None


# ============ Response Schemas ============


class ModelResponse(BaseModel):
    """Schema for model response (API key hidden)"""

    id: UUID
    name: str
    provider: str
    model_id: str
    model_type: str
    base_url: Optional[str] = None
    has_api_key: bool = Field(description="Whether API key is configured")
    context_length: Optional[int] = None
    max_output_tokens: Optional[int] = None
    input_price: Optional[Decimal] = None
    output_price: Optional[Decimal] = None
    default_params: Optional[dict[str, Any]] = None
    capabilities: Optional[dict[str, Any]] = None
    config: Optional[dict[str, Any]] = None
    is_enabled: bool
    is_default: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelBrief(BaseModel):
    """Brief model info for dropdown selections"""

    id: UUID
    name: str
    provider: str
    model_id: str
    model_type: str

    class Config:
        from_attributes = True


class ModelTestRequest(BaseModel):
    """Schema for testing model configuration before creation"""

    provider: ModelProvider = Field(..., description="Provider identifier")
    model_id: str = Field(
        ..., min_length=1, max_length=100, description="Model identifier"
    )
    model_type: ModelType = Field(..., description="Model type")
    base_url: Optional[str] = Field(None, max_length=512, description="Custom API URL")
    api_key: str = Field(..., min_length=1, max_length=1024, description="API key")
    config: Optional[dict[str, Any]] = Field(
        None, description="Additional configuration"
    )


class ModelTestResponse(BaseModel):
    """Schema for model test response"""

    success: bool = Field(..., description="Whether the test was successful")
    message: str = Field(..., description="Test result message")
    latency_ms: Optional[int] = Field(
        None, description="Response latency in milliseconds"
    )
