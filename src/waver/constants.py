"""常量定义和系统消息"""

import sys

# 系统配置
SERVICE_NAME = "waver-cli"
VERSION = "2.0.0"
TIMEOUT_SECONDS = 30
MAX_TOKENS = 2048
MAX_OUTPUT_LENGTH = 5000

# 编码设置
DEFAULT_ENCODING = "utf-8"

# 命令列表
COMMANDS = {
    "/help": "Show help information",
    "/provider": "Switch AI provider",
    "/model": "Switch model",
    "/key": "Manage API keys",
    "/proxy": "Set proxy",
    "/clear": "Clear conversation history",
    "/quit": "Exit the application",
    "/exit": "Exit the application",
}

# 系统提示词
SYSTEM_PROMPTS = {
    "default": "You are a helpful AI assistant. Reply in Chinese.",
    "code": "You are an expert programmer. Help the user with code.",
    "doc": "You are a documentation expert. Help the user write clear documentation.",
}

# UI 消息
UI_MESSAGES = {
    "banner_ready": "✓ Ready to chat",
    "banner_hint": "Type /help for commands",
    "error_prefix": "Error:",
    "success_prefix": "OK:",
    "info_prefix": "Info:",
    "title_waver": "WAVER",
    "title_providers": "Available Providers",
    "title_commands": "Commands",
    "title_models": "Available models",
    "prompt_provider": "Select provider",
    "prompt_apikey": "Enter API key for",
    "prompt_model": "Select number or enter model name",
    "prompt_proxy": "Proxy (http://host:port)",
}

# 错误消息
ERROR_MESSAGES = {
    "unknown_command": "Unknown command: {cmd}",
    "failed_create_client": "Failed to create client: {error}",
    "no_api_key": "No API key found for {provider}",
    "unknown_provider": "Unknown provider: {provider}",
    "timeout": "Command timed out ({timeout}s)",
    "dangerous_pattern": "Dangerous pattern '{pattern}' not allowed",
}

# 提供商功能标志
PROVIDER_FEATURES = {
    "supports_stream": True,
    "supports_tools": True,
}

# 加载动画帧 (Windows CMD 兼容)
ANIMATION_FRAMES = ["|", "/", "-", "\\"]

# 默认模型映射
DEFAULT_MODELS = {
    "siliconflow": [
        "Qwen/Qwen2.5-7B-Instruct",
        "Qwen/Qwen2.5-72B-Instruct",
        "Qwen/Qwen2.5-32B-Instruct",
        "deepseek-ai/DeepSeek-V2.5",
        "deepseek-ai/DeepSeek-R1",
        "THUDM/glm-4-9b-chat",
        "THUDM/glm-4-plus",
        "internlm/internlm2_5-7b-chat",
        "Pro/deepseek-ai/DeepSeek-R1",
    ]
}

# 危险模式检查
DANGEROUS_PATTERNS = [";", "&&", "||", "|", ">", ">>", "<", "`", "$(", "\n", "\r"]

# 平台检查
IS_WINDOWS = sys.platform == "win32"
