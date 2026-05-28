#!/usr/bin/env python3
"""
main.py — Sprint 2a: 重构后的入口

Run from GPT-SoVITS root:
    python Custom/projects/morning/mac/main.py
"""

import sys
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
    runtime.logger.info(f"[{lang}]  {text}")
    audio, sr = runtime.tts_engine.generate(text, lang)
    success = runtime.relay.send(audio, text, sr, runtime.config.output_dir)
    if not success:
        runtime.logger.warning("Relay to server failed, but audio was saved locally.")
    runtime.logger.info("Done.")


if __name__ == "__main__":
    main()
