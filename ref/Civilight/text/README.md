# 参考文本说明

> 参考音频的选择标准见 [ref/README.md](../../README.md)。

## 当前
- ja: `reference.txt`（已配置）

## 待添加
- zh: 中文参考文本 → `reference_zh.txt`
- en: 英文参考文本 → `reference_en.txt`

## 配置方法
在 `config.json` 的 `refs` 中更新路径：
```json
{
  "zh": {"audio": "ref/Civilight/audio/reference_zh.wav", "text": "ref/Civilight/text/reference_zh.txt"},
  "en": {"audio": "ref/Civilight/audio/reference_en.wav", "text": "ref/Civilight/text/reference_en.txt"}
}
```
然后更新 `enabled_languages`: `["ja", "zh", "en"]`
