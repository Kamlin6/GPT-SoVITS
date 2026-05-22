# FAQ_KAM — GPT-SoVITS 环境问题排查手册

> 记录日期：2026-05-22
> 环境：macOS + miniconda3 + Python 3.10 + GPT-SoVITS

---

## Q1：启动后报 `APIInfoParseError: Cannot parse schema True`

### 症状
```
gradio_client.utils.APIInfoParseError: Cannot parse schema True
ERROR: Exception in ASGI application
```
前端所有组件显示 ERROR，页面无法正常使用。

### 根本原因
`gradio_client` 的 `_json_schema_to_python_type()` 函数在处理
`additionalProperties: true` 时，把 `True`（bool）当成 schema dict
递归传入，导致 `get_type(True)` 崩溃。

### 修复方法（Patch 源码）

在终端执行以下命令：

```bash
python3 - << 'EOF'
path = "/Users/zhuanzmima0000/miniconda3/envs/GPTSoVITS/lib/python3.10/site-packages/gradio_client/utils.py"
with open(path, "r") as f:
    content = f.read()

old = '''        if "additionalProperties" in schema:
            des += [
                f"str, {_json_schema_to_python_type(schema['additionalProperties'], defs)}"
            ]'''

new = '''        if "additionalProperties" in schema:
            add_props = schema["additionalProperties"]
            if isinstance(add_props, dict):
                des += [
                    f"str, {_json_schema_to_python_type(add_props, defs)}"
                ]
            else:
                des += ["str, Any"]'''

if old in content:
    content = content.replace(old, new)
    with open(path, "w") as f:
        f.write(content)
    print("✅ Patch 成功！")
else:
    print("❌ 未找到目标代码，请手动检查")
EOF
```

### 验证
```bash
grep -A 5 "additionalProperties" \
  /Users/zhuanzmima0000/miniconda3/envs/GPTSoVITS/lib/python3.10/site-packages/gradio_client/utils.py
# 期望看到 isinstance(add_props, dict) 这行
```

---

## Q2：报 `ValueError: When localhost is not accessible, a shareable link must be created`

### 症状
```
ValueError: When localhost is not accessible, a shareable link must be created.
Please set share=True or check your proxy settings to allow access to localhost.
```

### 根本原因
**这是 Q1 的连锁反应**，并非真正的代理问题。  
API info 解析失败 → Gradio 认为本地服务不可用 → 抛出此错误。

### 修复方法
修复 Q1 后此错误自动消失。  
若修复 Q1 后仍出现，执行：

```bash
export no_proxy="localhost,127.0.0.1,0.0.0.0"
export NO_PROXY="localhost,127.0.0.1,0.0.0.0"
python GPT_SoVITS/inference_webui.py zh_CN
```

---

## Q3：`gradio_client` 版本选择与 `gradio` 的配对关系

### 正确配对
| gradio | gradio_client |
|--------|--------------|
| `3.50.x` | `0.6.1` |
| `4.44.1` | `1.3.0` ✅ 当前使用 |
| `5.x` | `1.4.x+` |

### 安装命令
```bash
pip uninstall gradio gradio_client -y
pip install "gradio==4.44.1" "gradio_client==1.3.0"
```

> ⚠️ 注意：安装后需重新执行 Q1 的 Patch，因为 pip 安装会覆盖修改。

---

## Q4：升级 `gradio` 或 `gradio_client` 后 Patch 失效

### 症状
更新包后重新出现 Q1 的报错。

### 原因
`pip install` 会覆盖已修改的 `utils.py`。

### 修复方法
重新执行 Q1 中的 Patch 命令即可。

---

## Q5：macOS 上 `DYLD_LIBRARY_PATH` 导致的库冲突

### 症状
启动时出现 ffmpeg / 音频相关的动态库报错。

### 修复方法
```bash
export DYLD_LIBRARY_PATH=""
python GPT_SoVITS/inference_webui.py zh_CN
```

---

## 📋 标准启动命令（推荐）

每次启动前执行：

```bash
export DYLD_LIBRARY_PATH=""
export no_proxy="localhost,127.0.0.1,0.0.0.0"
export NO_PROXY="localhost,127.0.0.1,0.0.0.0"
python GPT_SoVITS/inference_webui.py zh_CN
```

---

## 🔖 环境信息备档

| 项目 | 版本 |
|------|------|
| Python | 3.10 |
| gradio | 4.44.1 |
| gradio_client | 1.3.0（已 Patch） |
| 系统 | macOS |
| conda 环境 | GPTSoVITS |
| 模型路径 | `/Users/zhuanzmima0000/user/GPT-SoVITS/` |