# Server Configuration Journal

> 完整复现指南。只记录被坑过的，不堆砌成功步骤。

---

## Q1: SSH 连接被拒绝

**现象**：`ssh user@1.2.3.4` 返回 `Permission denied`

**排查**：本地 `~/.ssh/config` 已配置 `IdentityFile` 和 `User`，使用 hostname 连接可通。

**根因**：裸 IP 连接时 OpenSSH 不匹配 `Host` 块。

**解决方案**：始终使用 `~/.ssh/config` 中定义的 Host 名称连接，不要用 IP。

```bash
# 正确
ssh myserver

# 错误——不走 Host 配置，等于没有 IdentityFile
ssh user@1.2.3.4
```

**验证**：`ssh myserver` 直接登录无需密码。

---

## Q2: Clash Verge DEB 在无头服务器上不工作

**现象**：`dpkg -i clash-verge*.deb` 成功安装但无法启动，无日志输出。

**根因**：Clash Verge 是 GUI 应用（Tauri + WebView），服务器无桌面环境。

**解决方案**：卸载后安装纯 CLI 核心 mihomo（MetaCubeX 维护的 clash-meta 内核）。

```bash
# 卸载 GUI
sudo dpkg -r clash-verge

# 确认最新版本 https://github.com/MetaCubeX/mihomo/releases/latest
# 当前最新：v1.19.25
wget https://github.com/MetaCubeX/mihomo/releases/download/v1.19.25/mihomo-linux-amd64-v1.19.25.deb
sudo dpkg -i mihomo-linux-amd64-v1.19.25.deb
```

**验证**：`mihomo --version` 输出版本号。

---

## Q3: 供应商订阅内容无法被 mihomo 直接解析

**现象**：
```
FATA Parse config error: yaml: unmarshal errors:
  line 1: cannot unmarshal !!str `vless:/...` into config.RawConfig
```

**根因**：供应商链接返回的是 vless:// vmess:// 分享链接文本（一行一个），不是 Clash YAML 配置。mihomo 期望 YAML 格式。

**排查**：
```bash
# 看前 100 字符判断格式
curl -s "你的订阅链接" | head -c 100
# 输出如：vless://xxxx@server:port?... → 是分享链接，不是 YAML
```

**解决方案**：用 mihomo 的 `proxy-providers` 机制，指定 `type: file` 加载分享链接文件。

```bash
# 保存原始订阅内容
curl -s "你的订阅链接" -o ~/.config/mihomo/subscription.txt

# 写包装配置
cat > ~/.config/mihomo/config.yaml << 'EOF'
mixed-port: 7897
allow-lan: false
mode: rule
log-level: info

proxy-providers:
  provider:
    type: file
    path: ./subscription.txt
    health-check:
      enable: true
      url: https://www.gstatic.com/generate_204
      interval: 300

proxy-groups:
  - name: Proxy
    type: select
    proxies:
      - AUTO
    use:
      - provider
  - name: AUTO
    type: url-test
    use:
      - provider
    url: https://www.gstatic.com/generate_204
    interval: 300

rules:
  - MATCH,Proxy
EOF
```

**注意**：`path: ./subscription.txt` 是相对于 `-d` 指定目录的路径。

---

## Q4: 端口配置缺失

**现象**：订阅的分享链接中不含端口字段，mihomo 无法确定监听端口。

**根因**：本地 Clash Verge 的 `mixed-port: 7897` 配置没有出现在服务器上。

**解决方案**：在本地 Clash Verge → 导出/查看 config.yaml → 提取关键字段全量注入服务器配置。

```yaml
# 本地 Clash Verge 中提取的关键字段示例
mixed-port: 7897
allow-lan: false
mode: rule
```

**验证**：`grep mixed-port ~/.config/mihomo/config.yaml` 必须有输出。

---

## 代理测试

每次调整配置后验证三层连通性：

```bash
# 层 1: mihomo 进程存活
ps aux | grep mihomo

# 层 2: 本地端口监听
ss -tlnp | grep 7897

# 层 3: 代理生效
source /usr/local/bin/proxy.sh
curl -I https://discord.com/api
# 期望: HTTP/2 200
```

---

## Stow 跟踪内容

Server dotfiles 包结构（target: `/`）：

```
~/dotfiles/server-dotfiles/
├── etc/
│   ├── pip.conf                          → /etc/pip.conf
│   └── apt/
│       └── sources.list.d/
│           └── mirrors.list              → /etc/apt/sources.list.d/mirrors.list
└── usr/
    └── local/
        └── bin/
            └── proxy.sh                  → /usr/local/bin/proxy.sh
```

### etc/pip.conf
```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
```

### etc/apt/sources.list.d/mirrors.list
```
deb https://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse
```

### usr/local/bin/proxy.sh
```bash
#!/bin/bash
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897
export all_proxy=socks5://127.0.0.1:7897
export no_proxy=localhost,127.0.0.1
```

### 部署命令
```bash
sudo apt install stow -y
stow -t / -d ~/dotfiles server-dotfiles
sudo apt update   # 验证 apt 镜像
pip config list   # 验证 pip 镜像
```

---

## 最终验证：Discord Webhook

morning server 启动前确保代理已 source：

```bash
source /usr/local/bin/proxy.sh
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
python server.py
# 期望: Listening on 0.0.0.0:5000
```

Mac 端跑 `morning.py` → `curl -I https://discord.com/api` 在服务器上验证代理 → 管线全通。

---

> 日期：2026-05-28  |  服务器：Ubuntu 22.04 LTS  |  代理：mihomo v1.19.25
