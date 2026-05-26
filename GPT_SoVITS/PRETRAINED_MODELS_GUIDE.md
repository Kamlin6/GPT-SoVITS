# GPT-SoVITS Pretrained Models 清理指南

> 生成时间：2026-05-26
> 目标：保留 v2Pro / v2ProPlus 功能，清理冗余底模

---

## 必须保留（删除会导致崩溃）

| 路径 | 用途 | 依赖版本 |
|---|---|---|
| `s1v3.ckpt` | GPT 底模 | **v2Pro / v2ProPlus / v3 / v4 共用** |
| `v2Pro/` | SoVITS 底模 | **v2Pro / v2ProPlus 专用** |
| `sv/` | 说话人验证模型 | **v2Pro / v2ProPlus 专用** |
| `chinese-hubert-base/` | 语音特征提取 | 所有版本 |
| `chinese-roberta-wwm-ext-large/` | BERT 文本编码 | 所有版本 |
| `g2pw-chinese/` | 中文拼音转换 | 中文 TTS |
| `fast_langdetect/` | 语种检测 | 所有版本 |

---

## 建议保留（多处隐式引用）

| 路径 | 用途 | 引用位置 |
|---|---|---|
| `gsv-v2final-pretrained/` | v2 全套底模 | TTS.py 默认配置、api_v2.py 示例、WebUI 选项 |
| `s2Gv3.pth` | v3 SoVITS 底模 | export_torch_script_v3v4.py、name2gpt_path |

---

## 可安全删除（不影响 v2Pro/v2ProPlus）

| 路径 | 用途 | 说明 |
|---|---|---|
| `s1bert25hz-2kh...ckpt` | v1 GPT 底模 | WebUI 已注释，无代码引用 |
| `s2G488k.pth` / `s2D488k.pth` | v1 SoVITS 底模 | 仅 config.py 默认值引用，可忽略 |
| `gsv-v4-pretrained/` | v4 全套底模 | 无 v2Pro 相关引用 |
| `models--nvidia--bigvgan.../` | v3 声码器 | 仅 v3 使用 |

---

## 清理影响评估

- **删除 v1/v4 底模**：WebUI 中对应版本选项消失，但不影响 v2Pro/v2ProPlus
- **保留 v2 底模原因**：TTS.py 默认推理配置使用 v2 模型，多处示例代码引用
- **保留 v3 SoVITS 原因**：export_torch_script 脚本依赖，且与 v4 共享 s1v3.ckpt

---

## 其他目录说明

### Docker/
- **用途**：Docker 镜像构建脚本（install_wrapper.sh、miniforge_install.sh）
- **建议**：如果你不使用 Docker，可以删除；但文件很小（2 个 shell 脚本），保留无妨

### TEMP/
- **用途**：运行时临时文件目录（音频处理中间文件）
- **状态**：当前为空
- **建议**：**不要删除**，程序运行时会自动使用此目录
