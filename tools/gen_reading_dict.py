#!/usr/bin/env python3
"""
gen_reading_dict.py — 扫描日文文本池 → pykakasi 汉字→假名 → 写入 custom_reading.yaml

用法:
    cd GPT-SoVITS
    python tools/gen_reading_dict.py

已手动修改过的条目不会被覆盖（只追加新词）。
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pykakasi import kakasi
from Custom.characters.CIVILIGHT.texts_civilight import MORNING_GREETINGS_JA

DICT_PATH = ROOT / "ref" / "Civilight" / "custom_reading.yaml"


def extract_kanji_blocks(texts: list) -> set:
    """从文本中提取所有连续汉字块。"""
    words = set()
    for text in texts:
        blocks = re.findall(r'[\u4e00-\u9fff]+', text)
        for block in blocks:
            words.add(block)
    return words


def main():
    k = kakasi()
    # 加载已有字典（保留手动修改的条目）
    existing = {}
    if DICT_PATH.exists():
        with open(DICT_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        existing = data.get("overrides", {})

    # 从日文文本池提取汉字词
    words = extract_kanji_blocks(MORNING_GREETINGS_JA)
    print(f"Found {len(words)} unique kanji blocks")

    # pykakasi 转换（只追加新词，不覆盖已有）
    for word in sorted(words):
        if word not in existing:
            result = k.convert(word)
            reading = ''.join([item['hira'] for item in result])
            existing[word] = reading

    # 写回
    DICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DICT_PATH, "w", encoding="utf-8") as f:
        f.write("# 自定义读法字典\n")
        f.write("# 格式: 原文: 替换读法\n")
        f.write("# pykakasi 自动生成底字典，你只改不满意的条目\n\n")
        yaml.dump({"overrides": existing}, f, allow_unicode=True, sort_keys=False)

    print(f"Written {len(existing)} entries to {DICT_PATH}")
    # 提示可能需要手动改的关键词
    for word in ["博士", "私", "俺", "君"]:
        if word in existing:
            print(f"  check: {word} → {existing[word]}")


if __name__ == "__main__":
    main()
