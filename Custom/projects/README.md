# Custom Projects

> 所有自定义实验项目

## 项目列表

| 项目 | 状态 | 说明 |
|------|------|------|
| [morning](./morning/) | ✅ 管线完成 | 早安 TTS 管线：LLM → 预处理 → GPT-SoVITS → Delivery Switcher |

---

## morning 项目

### 管线架构

```
Mac 22:00 (launchd)
  → LLM.generate() (GPT-4o-mini)
    → preprocessor.process() (自定义读法字典)
      → tts_engine.generate() (GPT-SoVITS v2Pro)
        → switcher.deliver()
          → icloud handler (iCloud Drive 同步)
          → scp handler (服务器上传，可选)
```

### 已完成 Sprint

| Sprint | 内容 | 状态 |
|--------|------|------|
| 1 | 管线全通（Mac → Server → Discord） | ✅ |
| 2a | Interface-based 重构 | ✅ |
| 2b | JA-only 锁定 | ✅ |
| 3 | 预处理 + launchd + systemd + SCP | ✅ |
| 4 | LLM 文本生成 | ✅ |
| 4b | 热修复（env key + 输出校验） | ✅ |
| 5 | iCloud 直传 | ✅ |
| 6 | Delivery Switcher | ✅ |
| 6b | P1 热修复（异常/去重/白名单/最小权限） | ✅ |

### 快速开始

```bash
cd ~/GPT-SoVITS
python Custom/projects/morning/mac/main.py
```

### 配置

- `config.json` — 项目配置（已被 .gitignore 排除）
- `core/config.py` — 配置结构定义
- `modules/switcher.py` — Delivery 分发控制器

### 文档

- `PIPELINE/STATUS.md` — 当前 Sprint 状态
- `PIPELINE/BACKLOG.md` — 项目 Backlog
- `PIPELINE/DESIGN/` — 设计文档
- `PIPELINE/ATTACK/` — 安全审查

## 文档索引

- `PIPELINE/BACKLOG.md` — 唯一需求池 + Sprint 历史
- `PIPELINE/STATUS.md` — 当前 Sprint 状态
- `PIPELINE/README.md` — 工程流水线总纲 + Delivery 扩展指导
