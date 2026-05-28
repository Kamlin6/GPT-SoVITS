"""
tts_engine.py — TTS 模型加载 + 音频生成

职责：
- 加载 GPT-SoVITS TTS 模型
- generate(): 接收文本+语言 → 返回 (sr, audio)，内部自动匹配 ref
- 检查空音频，抛出 RuntimeError
"""

import logging
from pathlib import Path

import numpy as np

from Custom.projects.morning.core.config import MorningConfig

logger = logging.getLogger("morning")


class TTSEngine:
    """TTS 引擎封装。负责模型加载和音频生成。"""

    def __init__(self, config: MorningConfig):
        self.config = config
        self.tts = self._load_model()

    def _load_model(self):
        """加载 TTS 模型。

        Returns:
            TTS 实例
        """
        from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config

        tts_config = TTS_Config(str(Path(__file__).resolve().parent.parent.parent.parent.parent / "GPT_SoVITS" / "configs" / "tts_infer.yaml"))
        tts_config.t2s_weights_path = self.config.tts_weights_s1
        tts_config.vits_weights_path = self.config.tts_weights_s2

        logger.info("Loading TTS engine (v2ProPlus, CPU) ...")
        tts = TTS(tts_config)
        logger.info("TTS engine ready.")
        return tts

    def _build_inputs(self, text: str, lang: str) -> dict:
        """构建 TTS 输入参数。

        Args:
            text: 待合成文本
            lang: 语言代码

        Returns:
            TTS run() 的输入字典
        """
        ref = self.config.refs.get(lang, {})
        ref_audio = ref.get("audio", "")
        ref_text = ref.get("text", "")

        if not ref_audio:
            raise ValueError(f"No reference audio configured for language '{lang}'")

        prompt_text = ""
        if ref_text:
            prompt_text = Path(ref_text).read_text("utf-8").strip()

        return {
            "text": text,
            "text_lang": lang,
            "ref_audio_path": ref_audio,
            "prompt_text": prompt_text,
            "prompt_lang": lang,
            "top_k": self.config.top_k,
            "top_p": self.config.top_p,
            "temperature": self.config.temperature,
            "speed_factor": self.config.speed_factor,
            "parallel_infer": self.config.parallel_infer,
        }

    def generate(self, text: str, lang: str) -> tuple[int, np.ndarray]:
        """生成音频。

        Args:
            text: 待合成文本
            lang: 语言代码

        Returns:
            (sample_rate, audio_array)

        Raises:
            RuntimeError: TTS 未产生任何音频帧
        """
        inputs = self._build_inputs(text, lang)
        logger.debug(f"TTS inputs: text={text[:30]}..., lang={lang}")

        audio, sr = None, None
        for sr, audio in self.tts.run(inputs):
            pass  # collect final frame

        if audio is None:
            raise RuntimeError(f"TTS generated no audio for text: {text[:30]}...")

        return sr, audio
