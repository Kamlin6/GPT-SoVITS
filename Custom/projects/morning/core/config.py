"""
config.py — MorningConfig: 中心环境变量定义处

职责：
- 声明所有配置项及其默认值
- from_json(): 从 config.json 加载，处理旧格式兼容
- resolve_paths(): 将相对路径解析为绝对路径
"""

import json
import logging
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("morning")


@dataclass
class MorningConfig:
    """中心环境变量定义。不直接从文件读取，只声明结构。"""

    # ── 服务器 ──
    server_url: str = "http://localhost:5000/morning"

    # ── 参考音频（per-language）──
    refs: dict = field(default_factory=lambda: {
        "ja": {"audio": "", "text": ""},
        "zh": {"audio": "", "text": ""},
        "en": {"audio": "", "text": ""},
    })

    # ── TTS 参数 ──
    tts_weights_s1: str = "GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt"
    tts_weights_s2: str = "GPT_SoVITS/pretrained_models/v2Pro/s2Gv2ProPlus.pth"
    tts_device: str = "cpu"
    top_k: int = 5
    top_p: float = 1.0
    temperature: float = 1.0
    speed_factor: float = 1.00
    parallel_infer: bool = True

    # ── 输出 ──
    output_dir: str = "output/morning"

    # ── 日志 ──
    log_level: str = "INFO"

    # ── 多语言 ──
    enabled_languages: list = field(default_factory=lambda: ["ja"])

    @classmethod
    def from_json(cls, path: str) -> "MorningConfig":
        """从 config.json 加载，覆盖默认值。

        错误处理契约:
        - 文件不存在 → 抛出 FileNotFoundError
        - JSON 缺少字段 → 使用默认值
        - 字段类型错误 → 抛出 ValueError
        - 旧格式检测 (ref_audio/ref_text) → 自动迁移到 refs.ja，打 WARNING 日志
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"config.json not found at {path}")

        with open(p, "r", encoding="utf-8") as f:
            raw: dict[str, Any] = json.load(f)

        # ── 旧格式兼容：检测 ref_audio/ref_text → 迁移到 refs.ja ──
        if "ref_audio" in raw or "ref_text" in raw:
            warnings.warn(
                "旧格式 config.json 检测到 ref_audio/ref_text，自动迁移到 refs.ja。"
                "请更新 config.json 为新的 per-language 结构。",
                DeprecationWarning,
            )
            refs = {
                "ja": {
                    "audio": raw.pop("ref_audio", ""),
                    "text": raw.pop("ref_text", ""),
                },
                "zh": {"audio": "", "text": ""},
                "en": {"audio": "", "text": ""},
            }
            raw["refs"] = refs

        # ── 类型校验 ──
        type_hints = {
            "server_url": str,
            "log_level": str,
            "output_dir": str,
            "tts_weights_s1": str,
            "tts_weights_s2": str,
            "tts_device": str,
            "top_k": int,
            "top_p": float,
            "temperature": float,
            "speed_factor": float,
            "parallel_infer": bool,
            "enabled_languages": list,
        }
        for key, expected_type in type_hints.items():
            if key in raw and not isinstance(raw[key], expected_type):
                raise ValueError(
                    f"Invalid type for '{key}': expected {expected_type.__name__}, "
                    f"got {type(raw[key]).__name__}"
                )

        # ── 提取 enabled_languages 并校验 ──
        enabled_languages = raw.pop("enabled_languages", None)
        if enabled_languages is not None:
            if not isinstance(enabled_languages, list):
                raise ValueError("'enabled_languages' must be a list")
            for item in enabled_languages:
                if not isinstance(item, str):
                    raise ValueError(f"'enabled_languages' items must be strings, got {type(item).__name__}")
            if not enabled_languages:
                raise ValueError("'enabled_languages' cannot be empty")
        else:
            enabled_languages = ["ja"]  # 默认值

        # ── 提取 refs 并校验结构 ──
        refs_raw = raw.pop("refs", {})
        if not isinstance(refs_raw, dict):
            raise ValueError("'refs' must be a dict")

        # 合并默认 refs 和用户提供的 refs
        default_refs = {
            "ja": {"audio": "", "text": ""},
            "zh": {"audio": "", "text": ""},
            "en": {"audio": "", "text": ""},
        }
        for lang in default_refs:
            if lang in refs_raw:
                lang_ref = refs_raw[lang]
                if isinstance(lang_ref, dict):
                    default_refs[lang]["audio"] = lang_ref.get("audio", "")
                    default_refs[lang]["text"] = lang_ref.get("text", "")

        # ── 构建实例 ──
        return cls(refs=default_refs, enabled_languages=enabled_languages, **{k: v for k, v in raw.items() if k in type_hints})

    def resolve_paths(self, root: Path) -> None:
        """将 config 中的相对路径解析为绝对路径。

        处理:
        - refs[lang].audio
        - refs[lang].text
        - tts_weights_s1
        - tts_weights_s2
        - output_dir
        """
        for lang in self.refs:
            audio = self.refs[lang].get("audio", "")
            if audio and not Path(audio).is_absolute():
                self.refs[lang]["audio"] = str(root / audio)

            text = self.refs[lang].get("text", "")
            if text and not Path(text).is_absolute():
                self.refs[lang]["text"] = str(root / text)

        if self.tts_weights_s1 and not Path(self.tts_weights_s1).is_absolute():
            self.tts_weights_s1 = str(root / self.tts_weights_s1)

        if self.tts_weights_s2 and not Path(self.tts_weights_s2).is_absolute():
            self.tts_weights_s2 = str(root / self.tts_weights_s2)

        if self.output_dir and not Path(self.output_dir).is_absolute():
            self.output_dir = str(root / self.output_dir)
