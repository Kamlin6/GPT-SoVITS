#!/usr/bin/env python3
"""
morning.py — Sprint 1: generate morning greeting TTS, relay to server
Run from GPT-SoVITS root:

    python Custom/projects/morning/mac/morning.py
"""

import json
import random
import sys
from datetime import datetime
from pathlib import Path

import requests
import soundfile as sf

# ── path setup ──
ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
CHARACTER_DIR = ROOT / "Custom" / "characters" / "CIVILIGHT"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CHARACTER_DIR))

from texts_civilight import ALL_POOLS, WEEKDAYS_JA

# ── load config ──
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
try:
    cfg = json.loads(CONFIG_PATH.read_text())
except FileNotFoundError:
    print(f"config.json not found at {CONFIG_PATH}, falling back to example config")
    example = CONFIG_PATH.with_name("config.example.json")
    cfg = json.loads(example.read_text())

SERVER_URL   = cfg.get("server_url", "http://localhost:5000/morning")
REF_AUDIO    = str(ROOT / cfg.get("ref_audio", "ref/Civilight/audio/reference.wav"))
REF_TEXT     = Path(ROOT / cfg.get("ref_text", "ref/Civilight/text/reference.txt")).read_text("utf-8").strip()

OUTPUT_DIR   = ROOT / "output" / "morning"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── pick random language & greeting ──
lang, pool = random.choice(ALL_POOLS)
raw = random.choice(pool)
now = datetime.now()
text = raw.format(
    weekday=WEEKDAYS_JA[now.weekday()],
    date=now.strftime("%m月%d日"),
)
print(f"[{lang}]  {text}")

# ── load TTS engine ──
print("Loading TTS engine (v2ProPlus, CPU) ...")
from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config

config = TTS_Config(str(ROOT / "GPT_SoVITS" / "configs" / "tts_infer.yaml"))
# v2ProPlus SoVITS + v2 GPT (proven config from zero_shot_clone_inference_batch.py)
config.t2s_weights_path  = "GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt"
config.vits_weights_path = "GPT_SoVITS/pretrained_models/v2Pro/s2Gv2ProPlus.pth"

tts = TTS(config)
print("TTS engine ready.")

# ── generate audio ──
print("Generating audio ...")
inputs = {
    "text":           text,
    "text_lang":      lang,
    "ref_audio_path": REF_AUDIO,
    "prompt_text":    REF_TEXT,
    "prompt_lang":    "ja",
    "top_k":          5,
    "top_p":          1.0,
    "temperature":    1.0,
    "speed_factor":   1.00,
    "parallel_infer": True,
}

sr, audio = None, None
for sr, audio in tts.run(inputs):
    pass  # collect final frame

if audio is None:
    print("TTS produced no audio, aborting.")
    sys.exit(1)

timestamp = now.strftime("%Y-%m-%d_%H%M%S")
output_path = OUTPUT_DIR / f"morning_{timestamp}.wav"
sf.write(str(output_path), audio, sr)
print(f"Saved: {output_path}")

# ── relay to server ──
print(f"Relaying to {SERVER_URL} ...")
try:
    with open(output_path, "rb") as f:
        files = {"audio": (f"morning_{timestamp}.wav", f, "audio/wav")}
        data  = {"text": text}
        resp  = requests.post(SERVER_URL, files=files, data=data, timeout=30)
    print(f"Server response: {resp.status_code}  {resp.text[:200]}")
except requests.exceptions.ConnectionError:
    print(f"Cannot reach {SERVER_URL} — is the server running?")
    sys.exit(1)
except Exception as e:
    print(f"Relay failed: {e}")
    sys.exit(1)

print("Done.")
