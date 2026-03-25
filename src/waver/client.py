"""API 客户端工厂"""

import logging
from typing import Optional, Any, List
from openai import OpenAI
import tenacity
from waver import config, providers, constants

logger = logging.getLogger(__name__)

# 默认模型列表
DEFAULT_MODELS = constants.DEFAULT_MODELS


class ClientFactory:
    """API 客户端工厂 - 支持重试和日志"""

    @staticmethod
    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(3),
        reraise=True
    )
    def create(provider: str) -> Any:
        """创建 API 客户端（支持重试）"""
        logger.info(f"Creating client for provider: {provider}")
        
        api_key = config.get_key(provider)
        if not api_key:
            error_msg = constants.ERROR_MESSAGES["no_api_key"].format(provider=provider)
            logger.error(error_msg)
            raise ValueError(error_msg)

        p = providers.get_provider(provider)
        if not p:
            error_msg = constants.ERROR_MESSAGES["unknown_provider"].format(provider=provider)
            logger.error(error_msg)
            raise ValueError(error_msg)

        api_type = p.get("api_type", "openai")

        try:
            if api_type == "anthropic":
                import anthropic
                logger.debug(f"Creating Anthropic client")
                return anthropic.Anthropic(api_key=api_key)
            
            elif api_type == "google":
                import google.generativeai as genai
                logger.debug(f"Creating Google AI client")
                genai.configure(api_key=api_key)
                return genai
            
            else:
                # OpenAI 兼容格式
                base_url = p.get("base_url", "https://api.openai.com/v1")
                logger.debug(f"Creating OpenAI-compatible client: {base_url}")
                return OpenAI(api_key=api_key, base_url=base_url)
        
        except Exception as e:
            logger.error(f"Failed to create client for {provider}: {e}")
            raise

    @staticmethod
    def get_model(provider: str) -> str:
        """获取当前使用的模型"""
        p_config = config.get_provider_config(provider)
        if p_config and "model" in p_config:
            model = p_config["model"]
            logger.debug(f"Using saved model for {provider}: {model}")
            return model
        
        default_model = providers.get_default_model(provider)
        logger.debug(f"Using default model for {provider}: {default_model}")
        return default_model

    @staticmethod
    def list_models(provider: str) -> List[str]:
        """获取可用模型列表"""
        logger.debug(f"Fetching models for {provider}")
        
        # 先尝试从 API 获取
        try:
            client = ClientFactory.create(provider)
            if hasattr(client, "models") and hasattr(client.models, "list"):
                resp = client.models.list()
                if hasattr(resp, "data"):
                    models = [m.id for m in resp.data]
                    logger.debug(f"Found {len(models)} models from API")
                    return models
        except Exception as e:
            logger.warning(f"Failed to fetch models from API: {e}")

        # 返回默认列表
        default_list = DEFAULT_MODELS.get(provider, [])
        logger.debug(f"Using default model list for {provider}: {len(default_list)} models")
        return default_list
def create_client(provider: str) -> Any:
    """创建客户端的便捷函数"""
    return ClientFactory.create(provider)


def get_model(provider: str) -> str:
    """获取模型的便捷函数"""
    return ClientFactory.get_model(provider)


def list_models(provider: str) -> List[str]:
    """获取模型列表"""
    return ClientFactory.list_models(provider)
