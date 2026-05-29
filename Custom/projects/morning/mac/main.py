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
    text, lang = runtime.text_provider.pick()
    text = runtime.preprocessor.process(text, lang)
    runtime.logger.info(f"[{lang}]  {text}")

    audio, sr = runtime.tts_engine.generate(text, lang)

    # ── 保存音频 ──
    import soundfile as sf
    out_dir = Path(runtime.config.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    wav_path = out_dir / f"morning_{timestamp}.wav"
    sf.write(str(wav_path), audio, sr)
    runtime.logger.info(f"Saved: {wav_path}")

    # ── 发送（SCP 优先，HTTP relay 作为降级）──
    config = runtime.config
    if config.scp_host:
        date_str = datetime.now().strftime("%Y-%m-%d")
        success = runtime.relay.send_scp(wav_path, text, config, date_str)
        if not success:
            runtime.logger.warning("SCP failed; audio saved locally.")
    else:
        success = runtime.relay.send(audio, text, sr, config.output_dir)
        if not success:
            runtime.logger.warning("Relay to server failed, but audio was saved locally.")

    runtime.logger.info("Done.")


if __name__ == "__main__":
    main()
