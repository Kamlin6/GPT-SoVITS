#!/bin/bash
set -euo pipefail

REMOTE_DIR="/home/kambravolin/morning"
SENT_DIR="${REMOTE_DIR}/sent"
DATE=$(date +%F)
WAV="${REMOTE_DIR}/${DATE}.wav"
TXT="${REMOTE_DIR}/${DATE}.txt"

[ -f "$WAV" ] || { echo "[$(date)] No file for $DATE"; exit 0; }
[ -f "$TXT" ] || { echo "[$(date)] No text for $DATE"; exit 0; }
[ -f "${SENT_DIR}/${DATE}" ] && { echo "[$(date)] Already sent $DATE"; exit 0; }

TEXT=$(cat "$TXT")

curl -s --max-time 120 -X POST "${DISCORD_WEBHOOK_URL}" \
    -F "content=${TEXT}" \
    -F "file=@${WAV};type=audio/wav;filename=morning.wav" && {
    mkdir -p "$SENT_DIR"
    touch "${SENT_DIR}/${DATE}"
    echo "[$(date)] Sent $DATE"
}
