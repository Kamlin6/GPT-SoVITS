"""
setup.py — 加载一切，产出 Runtime

职责：
- Runtime dataclass: 装配所有模块的容器
- setup(): 读取 config.json → 填充 MorningConfig → 解析路径 → 初始化所有模块 → 返回 Runtime
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from Custom.projects.morning.core.config import MorningConfig
from Custom.projects.morning.core.logger import setup_logger

if TYPE_CHECKING:
    from GPT_SoVITS.TTS_infer_pack.TTS import TTS
    from Custom.projects.morning.modules.text_provider import TextProvider
    from Custom.projects.morning.modules.tts_engine import TTSEngine
    from Custom.projects.morning.modules.relay import Relay
    from Custom.projects.morning.modules.preprocessor import Preprocessor


@dataclass
class Runtime:
    """DI 容器。持有所有已初始化的模块。"""
    config: MorningConfig
    tts_engine: "TTSEngine"
    text_provider: "TextProvider"
    relay: "Relay"
    preprocessor: "Preprocessor"
    logger: logging.Logger


def setup(config_path: str, root: Path) -> Runtime:
    """读取 config.json → 填充 MorningConfig → 解析路径 → 初始化所有模块 → 返回 Runtime。

    Args:
        config_path: config.json 的路径
        root: GPT-SoVITS 项目根目录

    Returns:
        Runtime 实例
    """
    # ── 加载配置 ──
    config = MorningConfig.from_json(config_path)

    # ── 解析路径 ──
    config.resolve_paths(root)

    # ── 初始化日志 ──
    app_logger = setup_logger(config.log_level)

    # ── 初始化模块 ──
    from Custom.projects.morning.modules.text_provider import TextProvider
    from Custom.projects.morning.modules.tts_engine import TTSEngine
    from Custom.projects.morning.modules.relay import Relay
    from Custom.projects.morning.modules.preprocessor import Preprocessor

    text_provider = TextProvider(config.enabled_languages, app_logger)
    tts_engine = TTSEngine(config)
    relay = Relay(config, app_logger)
    dict_path = root / "ref" / "Civilight" / "custom_reading.yaml"
    preprocessor = Preprocessor(str(dict_path), config.preprocessor_enabled, app_logger)

    return Runtime(
        config=config,
        tts_engine=tts_engine,
        text_provider=text_provider,
        relay=relay,
        preprocessor=preprocessor,
        logger=app_logger,
    )
