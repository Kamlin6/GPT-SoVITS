#!/usr/bin/env python3
"""
morning-bot.py — Discord Bot 发送音频（备选方案，webhook 代理不通时使用）

用法:
    export DISCORD_BOT_TOKEN="xxx"
    export DISCORD_CHANNEL_ID="1234567890"
    python3 morning-bot.py
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

import discord

TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
CHANNEL_ID = int(os.environ.get("DISCORD_CHANNEL_ID", "0"))

MORNING_DIR = Path("/home/kambravolin/morning")
SENT_DIR = MORNING_DIR / "sent"


async def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    wav_path = MORNING_DIR / f"{date_str}.wav"
    txt_path = MORNING_DIR / f"{date_str}.txt"
    sent_path = SENT_DIR / date_str

    if not wav_path.exists() or not txt_path.exists():
        print(f"No file for {date_str}")
        return
    if sent_path.exists():
        print(f"Already sent {date_str}")
        return

    text = txt_path.read_text("utf-8").strip()
    print(f"Sending: {text[:60]}")

    intents = discord.Intents.default()
    client = discord.Client(intents=intents, proxy="http://127.0.0.1:7897")

    @client.event
    async def on_ready():
        channel = client.get_channel(CHANNEL_ID)
        if channel is None:
            print(f"Channel {CHANNEL_ID} not found")
            await client.close()
            return
        await channel.send(content=text, file=discord.File(str(wav_path)))
        print(f"Sent {date_str}")
        SENT_DIR.mkdir(parents=True, exist_ok=True)
        sent_path.touch()
        await client.close()

    await client.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
