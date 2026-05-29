"""
relay.py — HTTP 发送到服务器 / SCP 上传

职责：
- 保存音频到本地
- HTTP POST 到服务器（旧管线）
- SCP 上传到服务器（新管线）
- 失败时记录 ERROR 日志，返回 False
"""

import logging
import subprocess
from datetime import datetime
from pathlib import Path

import numpy as np
import requests
import soundfile as sf

from Custom.projects.morning.core.config import MorningConfig

logger = logging.getLogger("morning")


class Relay:
    """中继器。支持 HTTP relay 和 SCP 上传。"""

    def __init__(self, config: MorningConfig, app_logger: logging.Logger):
        self.server_url = config.server_url
        self.output_dir = config.output_dir
        self.logger = app_logger

    def send(self, audio: np.ndarray, text: str, sr: int, output_dir: str) -> bool:
        """保存音频 → POST 到服务器 → 返回成功/失败。

        Args:
            audio: 音频数组
            text: 文本内容
            sr: 采样率
            output_dir: 输出目录

        Returns:
            True 表示成功，False 表示失败
        """
        # ── 保存音频到本地 ──
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = out_dir / f"morning_{timestamp}.wav"

        try:
            sf.write(str(output_path), audio, sr)
            self.logger.info(f"Saved: {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save audio: {e}")
            return False

        # ── POST 到服务器 ──
        self.logger.info(f"Relaying to {self.server_url} ...")
        try:
            with open(output_path, "rb") as f:
                files = {"audio": (f"morning_{timestamp}.wav", f, "audio/wav")}
                data = {"text": text}
                resp = requests.post(self.server_url, files=files, data=data, timeout=30)
            self.logger.info(f"Server response: {resp.status_code}  {resp.text[:200]}")
            return resp.status_code == 200
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Cannot reach {self.server_url} — is the server running?")
            return False
        except Exception as e:
            self.logger.error(f"Relay failed: {e}")
            return False

    def send_scp(self, wav_path: Path, text: str, config: MorningConfig, date_str: str) -> bool:
        """SCP 上传 wav + txt 到服务器。

        Args:
            wav_path: 音频文件路径
            text: 文本内容
            config: MorningConfig（需要 scp_host, scp_remote_dir）
            date_str: 日期字符串（YYYY-MM-DD）

        Returns:
            True 表示成功，False 表示失败
        """
        host = config.scp_host
        remote_dir = config.scp_remote_dir

        try:
            # 上传 wav
            subprocess.run(
                ["scp", str(wav_path), f"{host}:{remote_dir}/{date_str}.wav"],
                check=True, timeout=30)
            self.logger.info(f"Uploaded {date_str}.wav")

            # 上传 txt
            txt_path = Path(wav_path).with_suffix(".txt")
            txt_path.write_text(text, "utf-8")
            subprocess.run(
                ["scp", str(txt_path), f"{host}:{remote_dir}/{date_str}.txt"],
                check=True, timeout=30)
            self.logger.info(f"Uploaded {date_str}.txt")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"SCP failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"SCP upload failed: {e}")
            return False
