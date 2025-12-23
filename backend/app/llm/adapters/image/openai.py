"""
OpenAI DALL-E 图像生成适配器
"""
import logging
import httpx

from app.models.model import Model
from app.llm.types import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    GeneratedImage,
    ImageContent,
)
from app.llm.errors import (
    AuthenticationError,
    RateLimitError,
    ContentFilterError,
    ProviderError,
    InvalidRequestError,
)
from .base import BaseImageAdapter

logger = logging.getLogger(__name__)


class OpenAIImageAdapter(BaseImageAdapter):
    """OpenAI DALL-E 图像生成适配器"""

    def __init__(self, model_config: Model):
        self.model_config = model_config
        self.api_key = model_config.api_key
        self.base_url = model_config.base_url or "https://api.openai.com/v1"
        self.model_id = model_config.model_id

    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """
        生成图像

        Args:
            request: 图像生成请求

        Returns:
            ImageGenerationResponse: 生成结果
        """
        # 构建请求体
        payload = {
            "model": self.model_id,
            "prompt": request.prompt,
            "n": request.num_images,
            "response_format": "url",  # 或 "b64_json"
        }

        # DALL-E 3 使用 size 参数
        if self.model_id in ["dall-e-3", "dall-e-2"]:
            # DALL-E 支持的尺寸
            size = self._get_size(request.width, request.height)
            payload["size"] = size

            # DALL-E 3 特有参数
            if self.model_id == "dall-e-3":
                if request.style:
                    payload["style"] = request.style  # vivid 或 natural
                if request.quality:
                    payload["quality"] = request.quality  # standard 或 hd

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/images/generations",
                    json=payload,
                    headers=headers,
                )

                if response.status_code == 401:
                    raise AuthenticationError(
                        message="Invalid API key",
                        provider="openai",
                        model=self.model_id,
                    )
                elif response.status_code == 429:
                    raise RateLimitError(
                        message="Rate limit exceeded",
                        provider="openai",
                        model=self.model_id,
                    )
                elif response.status_code == 400:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", "Bad request")
                    if "content_policy" in error_msg.lower() or "safety" in error_msg.lower():
                        raise ContentFilterError(
                            message=error_msg,
                            provider="openai",
                            model=self.model_id,
                        )
                    raise InvalidRequestError(
                        message=error_msg,
                        provider="openai",
                        model=self.model_id,
                    )
                elif response.status_code != 200:
                    raise ProviderError(
                        message=f"OpenAI API error: {response.text}",
                        status_code=response.status_code,
                        provider="openai",
                        model=self.model_id,
                    )

                data = response.json()
                images = []

                for item in data.get("data", []):
                    image = GeneratedImage(
                        image=ImageContent(
                            url=item.get("url"),
                            base64=item.get("b64_json"),
                        ),
                        revised_prompt=item.get("revised_prompt"),
                    )
                    images.append(image)

                return ImageGenerationResponse(
                    images=images,
                    model=self.model_id,
                )

            except httpx.TimeoutException:
                raise ProviderError(
                    message="Request timeout",
                    provider="openai",
                    model=self.model_id,
                )
            except httpx.RequestError as e:
                raise ProviderError(
                    message=f"Request error: {str(e)}",
                    provider="openai",
                    model=self.model_id,
                )

    def _get_size(self, width: int, height: int) -> str:
        """将宽高转换为 DALL-E 支持的尺寸"""
        # DALL-E 3 支持: 1024x1024, 1792x1024, 1024x1792
        # DALL-E 2 支持: 256x256, 512x512, 1024x1024
        if self.model_id == "dall-e-3":
            if width > height:
                return "1792x1024"
            elif height > width:
                return "1024x1792"
            else:
                return "1024x1024"
        else:  # dall-e-2
            if width <= 256 or height <= 256:
                return "256x256"
            elif width <= 512 or height <= 512:
                return "512x512"
            else:
                return "1024x1024"
