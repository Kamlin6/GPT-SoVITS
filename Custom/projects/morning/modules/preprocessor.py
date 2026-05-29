"""
preprocessor.py — 文本预处理器

职责：
- 加载自定义读音字典（YAML）
- process(): 对日文文本逐词替换汉字→假名/自定义读法
- 按 key 长度降序替换，避免长词被短词部分匹配截断
"""

import logging

import yaml
from pathlib import Path

logger = logging.getLogger("morning")


class Preprocessor:
    """文本预处理器。加载自定义读音字典，逐词替换。"""

    def __init__(self, dict_path: str = None, enabled: bool = True, app_logger: logging.Logger = None):
        self.overrides = {}
        self.enabled = enabled
        self.logger = app_logger or logger
        if dict_path and enabled:
            self.overrides = self._load(dict_path)

    def _load(self, path: str) -> dict:
        p = Path(path)
        if not p.exists():
            self.logger.warning(f"Reading dict not found: {path}, skipping")
            return {}
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            overrides = data.get("overrides", {})
            self.logger.info(f"Loaded {len(overrides)} reading overrides")
            return overrides
        except Exception as e:
            self.logger.warning(f"Failed to load reading dict: {e}, skipping")
            return {}

    def process(self, text: str, lang: str) -> str:
        """对日文文本逐词替换汉字→读法。

        按 key 长度降序替换，避免 "今日": "きょう" 被 "日": "ひ" 截断。
        zh/en 语言不处理，直接返回原文。
        """
        if not self.enabled or lang != "ja":
            return text
        # 按 key 长度降序，先替换长词
        for kanji in sorted(self.overrides.keys(), key=len, reverse=True):
            reading = self.overrides[kanji]
            text = text.replace(kanji, reading)
        return text
