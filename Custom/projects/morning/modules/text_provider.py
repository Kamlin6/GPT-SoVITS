"""
text_provider.py — 文本池选择 + 格式化

职责：
- 从 texts_civilight 加载 ALL_POOLS 和 WEEKDAYS_JA
- pick(): 随机选择 (text, lang)，内部处理 weekday/date 模板替换
- 支持 enabled_languages 过滤
"""

import logging
import random
from datetime import datetime
from typing import Optional

from Custom.characters.CIVILIGHT.texts_civilight import ALL_POOLS, WEEKDAYS_JA

logger = logging.getLogger("morning")


class TextProvider:
    """文本池提供者。随机选择语言+文本，并做模板替换。"""

    def __init__(self, enabled_languages: list = None, app_logger: logging.Logger = None):
        self.pools = ALL_POOLS
        self.weekdays = WEEKDAYS_JA
        # 修复 F-002：显式 None 判断，不用 or
        self.enabled = enabled_languages if enabled_languages is not None else ["ja"]
        self.logger = app_logger or logger

        # 修复 F-002：空列表报错
        if not self.enabled:
            raise ValueError("'enabled_languages' cannot be empty")

        # 修复 F-003：校验语言代码有效性
        valid_langs = {lang for lang, _ in self.pools}
        for lang in self.enabled:
            if lang not in valid_langs:
                self.logger.warning(f"Unknown language '{lang}' in enabled_languages. Valid: {valid_langs}")

    def pick(self, now: Optional[datetime] = None) -> tuple[str, str]:
        """随机选择 (text, lang)。

        只从 enabled_languages 中选择。
        内部处理 weekday/date 模板替换。
        如果 now 为 None，使用 datetime.now()。

        Returns:
            (格式化后的文本, 语言代码)

        Raises:
            RuntimeError: 没有可用的语言池
        """
        if now is None:
            now = datetime.now()

        # 过滤语言池
        available = [(lang, pool) for lang, pool in self.pools if lang in self.enabled]
        if not available:
            raise RuntimeError(f"No enabled languages available. enabled={self.enabled}")

        lang, pool = random.choice(available)
        raw = random.choice(pool)
        text = raw.format(
            weekday=self.weekdays[now.weekday()],
            date=now.strftime("%m月%d日"),
        )
        return text, lang
