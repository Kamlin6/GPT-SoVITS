"""
GPT-SoVITS V2ProPlus 零样本批量推理脚本

实际目录结构：
  ref/
    Civilight/
      audio/
        reference.wav     ← 主参考音频
        clip_jp.wav       ← 备用参考音频（日语片段）
      text/
        reference.txt     ← 参考文本
  texts.txt               ← 待合成文本，每行一句日语
  output/                 ← 自动创建，输出 wav

模型文件（已按你的 pretrained_models 目录确认）：
  GPT  : pretrained_models/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt
  SoVITS G : pretrained_models/v2Pro/s2Gv2ProPlus.pth
  SoVITS D : pretrained_models/v2Pro/s2Dv2ProPlus.pth
"""

import os
import sys
import soundfile as sf
from pathlib import Path

# ─────────────────────────────────────────────
# 路径配置
# ─────────────────────────────────────────────
GPT_SOVITS_ROOT = "."
sys.path.insert(0, GPT_SOVITS_ROOT)

# V2ProPlus 预训练模型（按你的实际文件确认）
GPT_MODEL_PATH    = "GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt"
SOVITS_MODEL_PATH = "GPT_SoVITS/pretrained_models/v2Pro/s2Gv2ProPlus.pth"

# 角色配置（可扩展为多角色字典）
CHARACTERS = {
    "Civilight": {
        "ref_audio": Path("ref/Civilight/audio/reference.wav"),
        "ref_text":  Path("ref/Civilight/text/reference.txt"),
        # 备用音频，注释掉主音频时使用
        # "ref_audio": Path("ref/Civilight/audio/clip_jp.wav"),
    }
}

# 当前使用的角色
ACTIVE_CHARACTER = "Civilight"

# 待合成文本文件（每行一句）
TEXT_FILE  = Path("texts.txt")

# 输出目录
OUTPUT_DIR = Path("output") / ACTIVE_CHARACTER
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 推理参数
TEXT_LANG   = "ja"    # 输出语言：日语
PROMPT_LANG = "ja"    # 参考音频语言（若参考音频是中文改为 "zh"）
SPEED       = 1.05    # 语速
TOP_K       = 5
TOP_P       = 1.0
TEMPERATURE = 1.0
HOW_TO_CUT  = "按标点符号切"  # 长句切分策略

# ─────────────────────────────────────────────
# 初始化 TTS（只加载一次模型）
# ─────────────────────────────────────────────
from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config

print("⏳ 正在加载 V2ProPlus 模型，请稍候...")

config = TTS_Config("GPT_SoVITS/configs/tts_infer.yaml")
config.t2s_weights_path  = GPT_MODEL_PATH
config.vits_weights_path = SOVITS_MODEL_PATH

tts_engine = TTS(config)
print("✅ 模型加载完成！\n")

# ─────────────────────────────────────────────
# 读取参考音频 & 参考文本
# ─────────────────────────────────────────────
def load_character(name: str) -> tuple[str, str]:
    char = CHARACTERS[name]
    ref_audio = char["ref_audio"]
    ref_txt   = char["ref_text"]

    if not ref_audio.exists():
        raise FileNotFoundError(f"❌ 参考音频不存在：{ref_audio}")
    if not ref_txt.exists():
        raise FileNotFoundError(f"❌ 参考文本不存在：{ref_txt}")

    ref_text = ref_txt.read_text(encoding="utf-8").strip()
    print(f"🎙️  角色：{name}")
    print(f"📂  参考音频：{ref_audio}")
    print(f"📝  参考文本：{ref_text}\n")
    return str(ref_audio), ref_text

# ─────────────────────────────────────────────
# 读取待合成文本列表
# ─────────────────────────────────────────────
def load_texts(text_file: Path) -> list[str]:
    if not text_file.exists():
        raise FileNotFoundError(f"❌ 文本文件不存在：{text_file}")
    lines = [
        line.strip()
        for line in text_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    print(f"📋 共读取 {len(lines)} 条待合成文本\n")
    return lines

# ─────────────────────────────────────────────
# 批量推理
# ─────────────────────────────────────────────
def batch_infer(ref_wav: str, ref_text: str, texts: list[str]):
    total   = len(texts)
    success = 0
    failed  = []

    for i, text in enumerate(texts, start=1):
        preview = text[:40] + ("..." if len(text) > 40 else "")
        print(f"🔊 [{i:04d}/{total}] {preview}")

        inputs = {
            "text":           text,
            "text_lang":      TEXT_LANG,
            "ref_audio_path": ref_wav,
            "prompt_text":    ref_text,
            "prompt_lang":    PROMPT_LANG,
            "top_k":          TOP_K,
            "top_p":          TOP_P,
            "temperature":    TEMPERATURE,
            "speed_factor":   SPEED,
            "how_to_cut":     HOW_TO_CUT,
        }

        output_path = OUTPUT_DIR / f"{ACTIVE_CHARACTER}_{i:04d}.wav"

        try:
            sr, audio = None, None
            for sr, audio in tts_engine.run(inputs):
                pass  # 流式输出，取最终完整帧

            if audio is not None:
                sf.write(str(output_path), audio, sr)
                print(f"         ✅ → {output_path.name}")
                success += 1
            else:
                print(f"         ⚠️  生成结果为空，跳过")
                failed.append(i)

        except Exception as e:
            print(f"         ❌ 合成失败：{e}")
            failed.append(i)
            continue

    # ── 汇总报告 ──
    print(f"\n{'='*50}")
    print(f"🎉 批量推理完成！")
    print(f"   ✅ 成功：{success} / {total}")
    if failed:
        print(f"   ❌ 失败行号：{failed}")
    print(f"   📁 输出目录：{OUTPUT_DIR.resolve()}")
    print(f"{'='*50}")

# ─────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────
if __name__ == "__main__":
    ref_wav, ref_text = load_character(ACTIVE_CHARACTER)
    texts = load_texts(TEXT_FILE)
    batch_infer(ref_wav, ref_text, texts)