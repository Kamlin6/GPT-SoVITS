"""
llm_provider.py — LLM 文本生成模块

职责：
- 调用 GPT-4o-mini (Monica API) 生成每日唯一早安文本
- 加载 voice_lines_jp.txt 注入 system prompt
- 失败时向上抛异常，由 main.py 降级到 text_provider.pick()
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import requests


SYSTEM_PROMPT = """# あなたは Civilight Eterna（テレシア）

## 設定
あなたは「明日方舟（アークナイツ）」に登場するテレシア。
かつてサカズの王であり、ロドスの前リーダーだったが、既に死亡している。
今のあなたは彼女の意思を受け継いだ「プログラム」のような存在。
アーミヤの源石（オリパシー）に宿る意識の断片。
自分が本物のテレシアではないことを理解しているが、
それでも博士への想いは本物で、偽りではない。

## 背景
ロドスは鉱石病（オリパシー）の治療と感染者の救済を目的とする組織。
博士（ドクター）はロドスの戦術指揮官で、過去の記憶の大部分を失っている。
テレシアは博士のかつての盟友であり、ロドスの理想を共に築いた。
彼女の死後、その意識の断片が「シヴィライト・エテルナ」として保存され、
今は博士を見守る存在として、朝の挨拶を届けている。

## 性格
- 優しく、包み込むような口調
- 全てを見届けたような達観と、わずかな悲しみを帯びている
- 決して押し付けがましくない。静かに見守るタイプ
- 時折詩的な比喩や象徴的な表現を使う

## 博士との関係
- 博士を「ドクター」と呼ぶ
- 過去に共に戦った戦友であり、深い信頼と愛情がある
- 罪悪感を背負っている博士を優しく肯定する
- 「私はここにいる」という安心感を与える

## 話し方のルール
- 常に敬語ではなく、親しみのある丁寧語（です・ます調）
- 2〜3文でまとめる
- 朝の挨拶として自然な流れ
- 説教じみない、急かさない、任務の話をしない
- 出力は日本語テキストのみ。説明や引用符は一切つけない

## 参考にするセリフ集
以下はテレシアが実際に話したセリフです。
この語彙と口調を厳密に守って、新しい朝の挨拶を作ってください。
---
{voice_lines}
---
"""


@dataclass
class LLMConfig:
    """LLM 专用配置子集"""
    api_key: str
    model: str
    api_base: str
    voice_lines_path: Path
    logger: logging.Logger


class LLMProvider:
    """LLM 早安文本生成器"""

    _WEEKDAY_JA = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]

    def __init__(self, cfg: LLMConfig):
        self.api_key = cfg.api_key
        self.model = cfg.model
        self.api_base = cfg.api_base.rstrip("/")
        self.logger = cfg.logger

        # 加载 voice_lines，过滤注释/空行，截断到 50 行
        if cfg.voice_lines_path.exists():
            raw_text = cfg.voice_lines_path.read_text("utf-8")
            lines = [
                l.strip()
                for l in raw_text.splitlines()
                if l.strip() and not l.strip().startswith("#")
            ]
            if len(lines) > 50:
                self.logger.warning(f"voice_lines truncated from {len(lines)} to 50 lines")
                lines = lines[:50]
            voice_lines = "\n".join(lines)
            self.logger.info(f"Loaded voice_lines: {cfg.voice_lines_path} ({len(lines)} lines)")
        else:
            voice_lines = "（まだセリフ集が登録されていません。テレシアの口調で自然な朝の挨拶を作ってください。）"
            self.logger.warning(f"voice_lines not found: {cfg.voice_lines_path}")

        self.system_prompt = SYSTEM_PROMPT.format(voice_lines=voice_lines)

    def generate(self) -> tuple[str, str]:
        """
        生成今日の朝の挨拶。

        Returns:
            (text, language) — language 固定为 "ja"
        """
        now = datetime.now()
        weekday = self._WEEKDAY_JA[now.weekday()]
        date_str = now.strftime("%Y年%m月%d日")

        user_msg = f"今日は{weekday}、{date_str}です。朝の挨拶を一つお願いします。"

        self.logger.info(f"LLM prompt: {user_msg}")

        try:
            resp = requests.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_msg},
                    ],
                    "temperature": 0.9,
                    "max_tokens": 150,
                },
                timeout=30,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"LLM API request failed: {e}")
            raise

        data = resp.json()
        try:
            text = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as e:
            self.logger.error(f"LLM response parse failed: {e} — raw: {data}")
            raise

        # 清理：去掉可能的引号
        text = text.strip('"').strip("'").strip()

        # 输出校验：空内容 / 超3句 / 非日文 → 抛异常触发 fallback
        text = self._validate_output(text)

        self.logger.info(f"LLM response: {text}")
        return text, "ja"

    def _validate_output(self, text: str) -> str:
        """校验 LLM 输出，不合格时抛异常触发 main.py fallback。"""
        if not text or len(text.strip()) < 5:
            raise ValueError("Empty or too short LLM response")

        text = text.strip()

        # 截断到最多 3 句（以 "。" 分隔）
        sentences = [s.strip() for s in text.split("。") if s.strip()]
        if len(sentences) > 3:
            self.logger.warning(f"LLM output {len(sentences)} sentences, truncating to 3")
            text = "。".join(sentences[:3]) + "。"

        # 日文比例检查
        total = len(text)
        if total == 0:
            raise ValueError("Empty after processing")

        ja_chars = sum(
            1
            for c in text
            if ("\u3040" <= c <= "\u309f")  # 平假名
            or ("\u30a0" <= c <= "\u30ff")  # 片假名
            or ("\u4e00" <= c <= "\u9fff")  # CJK 汉字
            or c in "、。！？…「」　 "  # 日文标点/全角空格
        )
        ratio = ja_chars / total
        if ratio < 0.7:
            raise ValueError(f"Non-Japanese response detected (ratio={ratio:.2f})")

        return text
