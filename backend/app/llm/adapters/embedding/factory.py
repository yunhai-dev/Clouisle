"""
Embedding 模型工厂 - 使用 LangChain
"""
import logging

from langchain_core.embeddings import Embeddings

from app.models.model import Model, ModelProvider

logger = logging.getLogger(__name__)


def create_embedding_model(model_config: Model) -> Embeddings:
    """
    根据模型配置创建 LangChain Embedding 模型实例

    Args:
        model_config: 数据库中的模型配置

    Returns:
        Embeddings: LangChain Embedding 模型实例
    """
    provider = model_config.provider
    model_id = model_config.model_id
    api_key = model_config.api_key
    base_url = model_config.base_url

    if provider == ModelProvider.OPENAI:
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=model_id,
            api_key=api_key,
            base_url=base_url,
        )

    elif provider == ModelProvider.AZURE_OPENAI:
        from langchain_openai import AzureOpenAIEmbeddings

        config = model_config.config or {}
        azure_config = config.get("azure", {})
        return AzureOpenAIEmbeddings(
            azure_deployment=model_id,
            api_key=api_key,
            azure_endpoint=base_url,
            api_version=azure_config.get("api_version", "2024-02-01"),
        )

    elif provider in [
        ModelProvider.DEEPSEEK,
        ModelProvider.MOONSHOT,
        ModelProvider.ZHIPU,
        ModelProvider.QWEN,
        ModelProvider.BAICHUAN,
        ModelProvider.MINIMAX,
        ModelProvider.OLLAMA,
        ModelProvider.CUSTOM,
    ]:
        from langchain_openai import OpenAIEmbeddings

        # 这些供应商一般兼容 OpenAI API
        provider_base_urls = {
            ModelProvider.DEEPSEEK: "https://api.deepseek.com/v1",
            ModelProvider.MOONSHOT: "https://api.moonshot.cn/v1",
            ModelProvider.ZHIPU: "https://open.bigmodel.cn/api/paas/v4",
            ModelProvider.QWEN: "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ModelProvider.BAICHUAN: "https://api.baichuan-ai.com/v1",
            ModelProvider.MINIMAX: "https://api.minimax.chat/v1",
            ModelProvider.OLLAMA: "http://localhost:11434/v1",
        }
        final_base_url = base_url or provider_base_urls.get(provider)

        return OpenAIEmbeddings(
            model=model_id,
            api_key=api_key or "ollama",
            base_url=final_base_url,
        )

    else:
        raise ValueError(f"Unsupported provider for embedding: {provider}")
