"""配置管理模块 - 使用 keyring 加密存储"""

import keyring
import json
import logging
from pathlib import Path
from typing import Optional, Dict

SERVICE_NAME = "waver-cli"
CONFIG_DIR = Path.home() / ".waver"
CONFIG_FILE = CONFIG_DIR / "config.json"

logger = logging.getLogger(__name__)

# 内存缓存
_config_cache: Optional[Dict] = None
_cache_dirty = False


def ensure_config_dir():
    """确保配置目录存在"""
    try:
        CONFIG_DIR.mkdir(exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create config directory: {e}")
        raise


def _validate_provider(provider: str) -> bool:
    """验证提供商名称有效"""
    if not provider or not isinstance(provider, str):
        return False
    return len(provider) > 0 and provider.isidentifier()


def _validate_key(key: str) -> bool:
    """验证 API key 有效"""
    if not key or not isinstance(key, str):
        return False
    return len(key.strip()) > 0


def get_key(provider: str) -> Optional[str]:
    """从 keyring 获取 API Key"""
    if not _validate_provider(provider):
        logger.warning(f"Invalid provider name: {provider}")
        return None
    
    try:
        return keyring.get_password(SERVICE_NAME, provider)
    except Exception as e:
        logger.error(f"Failed to get key for {provider}: {e}")
        return None


def set_key(provider: str, key: str) -> None:
    """保存 API Key 到 keyring"""
    if not _validate_provider(provider):
        raise ValueError(f"Invalid provider name: {provider}")
    if not _validate_key(key):
        raise ValueError("API key cannot be empty")
    
    try:
        keyring.set_password(SERVICE_NAME, provider, key)
        # 记录到配置文件以便跟踪哪些提供商有密钥
        config = load_config()
        if "providers" not in config:
            config["providers"] = {}
        if provider not in config["providers"]:
            config["providers"][provider] = {}
        config["providers"][provider]["has_key"] = True
        _save_config(config)
        logger.info(f"API key saved for {provider}")
    except Exception as e:
        logger.error(f"Failed to set key for {provider}: {e}")
        raise


def delete_key(provider: str) -> None:
    """删除 API Key"""
    if not _validate_provider(provider):
        raise ValueError(f"Invalid provider name: {provider}")
    
    try:
        keyring.delete_password(SERVICE_NAME, provider)
        config = load_config()
        if "providers" in config and provider in config["providers"]:
            config["providers"][provider]["has_key"] = False
            _save_config(config)
        logger.info(f"API key deleted for {provider}")
    except keyring.errors.PasswordDeleteError:
        logger.warning(f"API key not found for {provider}")
    except Exception as e:
        logger.error(f"Failed to delete key for {provider}: {e}")


def get_all_keys() -> Dict[str, str]:
    """获取所有保存的 provider keys"""
    config = load_config()
    return config.get("providers", {})


def save_config(key: str, value) -> None:
    """保存配置"""
    global _config_cache, _cache_dirty
    ensure_config_dir()
    config = load_config()
    config[key] = value
    _save_config(config)


def _save_config(config: dict) -> None:
    """内部保存配置函数"""
    global _config_cache, _cache_dirty
    try:
        CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        _config_cache = config
        _cache_dirty = False
        logger.debug("Config saved successfully")
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        raise


def load_config() -> dict:
    """加载配置（使用缓存）"""
    global _config_cache
    
    ensure_config_dir()
    
    if _config_cache is not None:
        return _config_cache
    
    try:
        if CONFIG_FILE.exists():
            content = CONFIG_FILE.read_text(encoding="utf-8")
            _config_cache = json.loads(content)
        else:
            _config_cache = {}
        return _config_cache
    except json.JSONDecodeError as e:
        logger.error(f"Invalid config file: {e}")
        return {}
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}


def save_provider_config(provider: str, model: str) -> None:
    """保存 provider 配置"""
    if not _validate_provider(provider):
        raise ValueError(f"Invalid provider name: {provider}")
    if not model or not isinstance(model, str):
        raise ValueError("Model name cannot be empty")
    
    config = load_config()
    if "providers" not in config:
        config["providers"] = {}
    config["providers"][provider] = {"model": model}
    config["default_provider"] = provider
    _save_config(config)
    logger.info(f"Provider config saved: {provider} -> {model}")


def get_provider_config(provider: str) -> dict:
    """获取 provider 配置"""
    config = load_config()
    return config.get("providers", {}).get(provider, {})


def get_default_provider() -> str:
    """获取默认 provider"""
    config = load_config()
    return config.get("default_provider", "openai")


def set_default_provider(provider: str) -> None:
    """设置默认 provider"""
    if not _validate_provider(provider):
        raise ValueError(f"Invalid provider name: {provider}")
    save_config("default_provider", provider)
    logger.info(f"Default provider set to: {provider}")


def get_proxy() -> Optional[str]:
    """获取代理配置"""
    config = load_config()
    proxy = config.get("proxy")
    return proxy if proxy else None


def set_proxy(proxy: str) -> None:
    """设置代理"""
    if not proxy or not isinstance(proxy, str):
        raise ValueError("Proxy cannot be empty")
    save_config("proxy", proxy)
    logger.info(f"Proxy set to: {proxy}")


def clear_proxy() -> None:
    """清除代理"""
    config = load_config()
    if "proxy" in config:
        del config["proxy"]
        _save_config(config)
        logger.info("Proxy cleared")


def clear_all_config() -> None:
    """清除所有配置"""
    try:
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        global _config_cache
        _config_cache = None
        logger.info("All config cleared")
    except Exception as e:
        logger.error(f"Failed to clear config: {e}")
        raise

