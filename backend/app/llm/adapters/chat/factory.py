"""
Chat 模型工厂 - 使用 LangChain
"""
import logging

from langchain_core.language_models.chat_models import BaseChatModel

from app.models.model import Model, ModelProvider

logger = logging.getLogger(__name__)


def create_chat_model(model_config: Model) -> BaseChatModel:
    """
    根据模型配置创建 LangChain Chat 模型实例

    Args:
        model_config: 数据库中的模型配置

    Returns:
        BaseChatModel: LangChain Chat 模型实例
    """
    provider = model_config.provider
    model_id = model_config.model_id
    api_key = model_config.api_key
    base_url = model_config.base_url

    # 从 default_params 获取默认参数
    params = model_config.default_params or {}
    temperature = params.get("temperature")
    top_p = params.get("top_p")

    # 从 config 获取额外配置
    config = model_config.config or {}
    max_tokens = config.get("max_tokens")
    timeout = config.get("timeout", 60)

    if provider == ModelProvider.OPENAI:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model_id,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    elif provider == ModelProvider.ANTHROPIC:
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=model_id,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens or 4096,  # Anthropic 需要指定 max_tokens
            timeout=timeout,
        )

    elif provider == ModelProvider.AZURE_OPENAI:
        from langchain_openai import AzureChatOpenAI

        azure_config = config.get("azure", {})
        return AzureChatOpenAI(
            azure_deployment=model_id,
            api_key=api_key,
            azure_endpoint=base_url,
            api_version=azure_config.get("api_version", "2024-02-01"),
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    elif provider == ModelProvider.DEEPSEEK:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model_id,
            api_key=api_key,
            base_url=base_url or "https://api.deepseek.com/v1",
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    elif provider == ModelProvider.MOONSHOT:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model_id,
            api_key=api_key,
            base_url=base_url or "https://api.moonshot.cn/v1",
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    elif provider == ModelProvider.ZHIPU:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model_id,
            api_key=api_key,
            base_url=base_url or "https://open.bigmodel.cn/api/paas/v4",
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    elif provider == ModelProvider.QWEN:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model_id,
            api_key=api_key,
            base_url=base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    elif provider == ModelProvider.BAICHUAN:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model_id,
            api_key=api_key,
            base_url=base_url or "https://api.baichuan-ai.com/v1",
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    elif provider == ModelProvider.MINIMAX:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model_id,
            api_key=api_key,
            base_url=base_url or "https://api.minimax.chat/v1",
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    elif provider == ModelProvider.OLLAMA:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model_id,
            api_key=api_key or "ollama",  # Ollama 不需要 API key
            base_url=base_url or "http://localhost:11434/v1",
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    elif provider == ModelProvider.CUSTOM:
        # 通用 OpenAI 兼容接口
        from langchain_openai import ChatOpenAI

        if not base_url:
            raise ValueError("Custom provider requires base_url")

        return ChatOpenAI(
            model=model_id,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    else:
        raise ValueError(f"Unsupported provider for chat: {provider}")
