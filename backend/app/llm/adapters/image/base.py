"""
图像生成适配器基类
"""
from abc import ABC, abstractmethod

from app.llm.types import ImageGenerationRequest, ImageGenerationResponse


class BaseImageAdapter(ABC):
    """图像生成适配器基类"""

    @abstractmethod
    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """生成图像"""
        pass
