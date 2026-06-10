"""
switcher.py — Delivery 开关控制器

职责：
- 按 delivery_channels list 分发到各 handler
- 一个通道失败不影响后续通道
- 新增通道只需加 handler + config，main.py 永远不动
"""

import shutil
import subprocess
from pathlib import Path


class Switcher:
    """Delivery 开关控制器。按 channels list 分发，一个失败不影响后续。"""

    def __init__(self, channels: list, relay, logger):
        # P1-2: 去重（保持插入顺序）
        self.channels = list(dict.fromkeys(channels))
        self.relay = relay
        self.logger = logger
        # P1-4: 不持有全量 config，只持有 channels
        self._handlers = {
            "icloud": self._to_icloud,
            "scp":    self._to_scp,
        }

    def deliver(self, wav_path: Path, text: str, timestamp: str, date_str: str):
        """按 channels 顺序分发。"""
        for ch in self.channels:
            handler = self._handlers.get(ch)
            if handler is None:
                self.logger.warning(f"Unknown delivery channel: {ch}")
                continue
            try:
                handler(wav_path, text, timestamp, date_str)
            except (OSError, IOError, subprocess.CalledProcessError) as e:
                # P1-1: 只捕获预期的 I/O 和 subprocess 异常
                self.logger.error(f"[{ch}] delivery failed: {e}")

    def _to_icloud(self, wav_path: Path, *_):
        icloud_base = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/civilight/morning"
        old_base = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/morning"

        # Ab-004: 提醒旧路径不再使用
        if old_base.exists():
            self.logger.info(f"旧 iCloud 路径 {old_base} 已不再使用，新路径为 {icloud_base}")

        if wav_path.name.startswith("goodnight_"):
            target_dir = icloud_base / "goodnight"
        else:
            target_dir = icloud_base

        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(wav_path, target_dir / wav_path.name)
        self.logger.info(f"[icloud] copied to {target_dir}")

    def _to_scp(self, wav_path: Path, text: str, _, date_str: str):
        self.relay.send_scp(wav_path, text, self.relay.config, date_str)
        self.logger.info(f"[scp] uploaded {date_str}")
