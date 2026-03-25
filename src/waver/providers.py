"""提供商定义"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

PROVIDERS: Dict[str, Dict[str, Any]] = {
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
        "supports_stream": True,
        "supports_tools": True,
    },
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
        "supports_stream": True,
        "supports_tools": True,
    },
    "nvidia": {
        "name": "NVIDIA",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "default_model": "meta/llama-3.1-70b-instruct",
        "supports_stream": True,
        "supports_tools": True,
    },
    "kimi": {
        "name": "Kimi",
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "moonshot-v1-8k",
        "supports_stream": True,
        "supports_tools": True,
    },
    "glm": {
        "name": "GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4-flash",
        "supports_stream": True,
        "supports_tools": True,
    },
    "claude": {
        "name": "Claude",
        "api_type": "anthropic",
        "default_model": "claude-3-5-sonnet-20241022",
        "supports_stream": True,
        "supports_tools": False,
    },
    "google": {
        "name": "Google AI",
        "api_type": "google",
        "default_model": "gemini-2.0-flash",
        "supports_stream": True,
        "supports_tools": False,
    },
    "siliconflow": {
        "name": "SiliconFlow",
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "Qwen/Qwen2.5-7B-Instruct",
        "supports_stream": True,
        "supports_tools": True,
    },
}


def get_provider(name: str) -> Optional[Dict[str, Any]]:
    """获取提供商配置"""
    provider = PROVIDERS.get(name)
    if provider:
        logger.debug(f"Found provider: {name}")
    else:
        logger.warning(f"Provider not found: {name}")
    return provider


def list_providers() -> Dict[str, Dict[str, Any]]:
    """列出所有提供商"""
    logger.debug(f"Available providers: {len(PROVIDERS)}")
    return PROVIDERS


def get_default_model(provider: str) -> str:
    """获取提供商的默认模型"""
    p = PROVIDERS.get(provider, {})
    default_model = p.get("default_model", "gpt-4o")
    logger.debug(f"Default model for {provider}: {default_model}")
    return default_model


def get_provider_feature(provider: str, feature: str) -> bool:
    """获取提供商功能支持状态"""
    p = PROVIDERS.get(provider, {})
    return p.get(feature, False)
