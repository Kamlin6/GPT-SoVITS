#!/usr/bin/env python3
"""
main.py — Sprint 3: 重构后的入口 + SCP 上传

Run from GPT-SoVITS root:
    python Custom/projects/morning/mac/main.py
"""

import sys
from datetime import datetime
from pathlib import Path

# ── path setup ──
ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
CHARACTER_DIR = ROOT / "Custom" / "characters" / "CIVILIGHT"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CHARACTER_DIR))

# ── config path 相对于 __file__ ──
CONFIG_DIR = Path(__file__).resolve().parent.parent  # → Custom/projects/morning/
CONFIG_PATH = CONFIG_DIR / "config.json"

from Custom.projects.morning.core.setup import setup


def main():
    runtime = setup(str(CONFIG_PATH), ROOT)
    runtime.logger.info("Morning pipeline starting")

    # LLM 生成 → 失败时降级到模板池
    try:
        text, lang = runtime.llm.generate()
    except Exception as e:
        runtime.logger.error(f"LLM generation failed: {e}, falling back to text provider")
        text, lang = runtime.text_provider.pick()

    text = runtime.preprocessor.process(text, lang)
    runtime.logger.info(f"[{lang}]  {text}")

    sr, audio = runtime.tts_engine.generate(text, lang)

    # ── 保存音频 ──
    import soundfile as sf
    out_dir = Path(runtime.config.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    wav_path = out_dir / f"morning_{timestamp}.wav"
    sf.write(str(wav_path), audio, sr)
    runtime.logger.info(f"Saved: {wav_path}")

    # ── Delivery 分发 ──
    date_str = datetime.now().strftime("%Y-%m-%d")
    runtime.switcher.deliver(wav_path, text, timestamp, date_str)

    runtime.logger.info("Done.")


if __name__ == "__main__":
    main()
