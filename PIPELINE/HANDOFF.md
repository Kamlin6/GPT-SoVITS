# Handoff — 2026-06-09

## 会话总结

Flask 入门学习 + GPT-SoVITS 源码阅读（api_v2.py + TTS.py） + 项目清理。

- 构建 Flask 认知框架：app 本质、路由层（URL→endpoint→view_function）、methods
- 对照阅读 FastAPI：参数自动注入、Pydantic 模型、streaming mode 0-3
- 阅读 TTS.py run()：三阶段管线（TextPreprocessor → T2S → VITS decode）
- 清理：api.py → _deprecated/、.pre-commit-config.yaml → _deprecated/、FAQ_KAM.md 删除
- Worklog 迁移：FAQ_KAM 4 条踩坑转为 worklog
- Highlights 补 metrics：3 条补指标 + 1 条改类型

## 进度状态

- Sprint 7b（pool-infra）已完成
- WEB-01 未开工，backlog 已补完架构决策 + 源码阅读记录

## 待办事项

| # | 描述 | 优先级 |
|---|------|--------|
| 1 | Sprint 7b 收尾（commit/PR） | 低 |
| 2 | 启动 WEB-01（Flask Demo Web），2026-07-09 前需可用 | P1 |

## 上下文快照

- 分支: `custom`
- api.py → _deprecated/ 已 git mv 且 staged
- .pre-commit-config.yaml → _deprecated/ 已 git mv 且 staged
- FAQ_KAM.md 已 git rm 且 staged
- _deprecated/README.md 未 staged

## 相关文件

- `GPT-SoVITS/PIPELINE/BACKLOG.md` — WEB-01 详情 + 源码阅读记录
- `GPT-SoVITS/PIPELINE/README_KISHIN.md` — Sprint 8 学习记录
- `GPT-SoVITS/_deprecated/` — api.py + .pre-commit-config.yaml
- `GPT-SoVITS/api_v2.py` — 源码阅读对象（未修改）
- `GPT-SoVITS/GPT_SoVITS/TTS_infer_pack/TTS.py` — 源码阅读对象（未修改）

## 下一步建议

Sprint 7b 收尾 commit 后，直接进入 WEB-01。架构已确定（ECS Flask ↔ SSH 隧道 ↔ Mac api_v2），实现的起点是：在 ECS 上写一个最小 Flask app 验证隧道转发是否通。

---

# Session — 2026-06-10

## 会话总结
Sprint 7b 代码归档 + 项目清理提交 + 全局话题关闭。

### 交付
- Sprint 7b 全部变更 commit + push：`430ab15` → origin/custom
  - `pool_selector.py` SQLite 重写
  - `init_pools_db.py` 种子数据幂等导入
  - `switcher.py` iCloud 路径修正
  - `llm_provider.py`/`setup.py` pools_dir → pools_db_path 迁移
  - 清理：`api.py` → `_deprecated/`, `.pre-commit-config.yaml` → `_deprecated/`, `FAQ_KAM.md` 删除

### 验证
- `git status`: 工作区干净
- `git log`: `430ab15 [macOS][feat][All]: finalize Sprint 7b with SQLite pool infra and deprecated cleanup`

## 进度状态
- Sprint 7b: ✅ committed + pushed
- BACKLOG: 全部保留（WEB-01 P1 07-09 截止等）

## 上下文快照
- 分支: `custom`（up-to-date with origin/custom）
- 工作区: clean
