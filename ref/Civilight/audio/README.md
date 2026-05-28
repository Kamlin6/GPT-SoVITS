# 参考音频说明

> 参考音频的选择标准见 [ref/README.md](../../README.md)。

## 当前
- ja: `reference.wav` + `reference.txt`（已配置）

## 待添加
- zh: 录制中文参考音频 → 保存为 `reference_zh.wav` + `reference_zh.txt`
- en: 录制英文参考音频 → 保存为 `reference_en.wav` + `reference_en.txt`

## 配置方法
在 `config.json` 的 `refs` 中更新路径：
```json
{
  "zh": {"audio": "ref/Civilight/audio/reference_zh.wav", "text": "ref/Civilight/text/reference_zh.txt"},
  "en": {"audio": "ref/Civilight/audio/reference_en.wav", "text": "ref/Civilight/text/reference_en.txt"}
}
```
然后更新 `enabled_languages`: `["ja", "zh", "en"]`

## 文件缺失时行为
如果 `enabled_languages` 包含某语言但 `refs` 中对应音频为空，TTS 引擎将在运行时抛出 `ValueError`。
