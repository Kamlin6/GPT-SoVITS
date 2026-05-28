#!/usr/bin/env python3
"""
server.py — Sprint 1 relay: receive morning TTS → forward to Discord webhook

Run on your Ubuntu server:
    pip install flask requests
    export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
    python server.py
"""

import json
import os
import tempfile
from pathlib import Path

import requests
from flask import Flask, request, jsonify

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
if not WEBHOOK_URL:
    print("Set DISCORD_WEBHOOK_URL environment variable")
    exit(1)

app = Flask(__name__)


@app.route("/morning", methods=["POST"])
def morning():
    audio = request.files.get("audio")
    text  = request.form.get("text", "")

    if not audio:
        return jsonify({"error": "no audio"}), 400

    print(f"Incoming: {text[:60]}")

    # save audio to temp file (requests needs a file handle for multipart)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio.save(tmp)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            resp = requests.post(
                WEBHOOK_URL,
                data={"content": text},
                files={"file": ("morning.wav", f, "audio/wav")},
                timeout=30,
            )
        status = resp.status_code
        body   = resp.text[:200]
        print(f"Discord response: {status}  {body}")
    finally:
        Path(tmp_path).unlink()

    if status == 200:
        return jsonify({"ok": True}), 200
    else:
        return jsonify({"error": f"discord returned {status}"}), 502


if __name__ == "__main__":
    print(f"Listening on 0.0.0.0:5000, webhook: {WEBHOOK_URL[:50]}...")
    app.run(host="0.0.0.0", port=5000)
