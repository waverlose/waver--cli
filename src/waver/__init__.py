"""Waver CLI - Modern AI CLI Tool"""

import logging
import os
from pathlib import Path

__version__ = "2.0.0"

# 配置日志
LOG_DIR = Path.home() / ".waver" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "waver.log"

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 配置根日志记录器
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ]
)

# 获取应用级日志记录器
logger = logging.getLogger(__name__)
logger.info(f"Waver {__version__} started")
