"""
logger.py — 通用日志模块

职责：
- setup_logger(): 配置日志格式、级别
"""

import logging
import sys


def setup_logger(level: str = "INFO", name: str = "morning") -> logging.Logger:
    """配置日志格式、级别。

    Args:
        level: 日志级别（DEBUG/INFO/WARNING/ERROR）
        name: logger 名称

    Returns:
        配置好的 logging.Logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
