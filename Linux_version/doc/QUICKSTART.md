# 快速开始 Quick Start

## 中文说明

### 一键安装（推荐）

```bash
cd /home/ubuntu/Ctrip-Crawler/Linux_version
sudo bash setup_environment.sh
```

安装脚本会自动完成所有依赖的安装和配置，大约需要 5-15 分钟。

### 配置项目

```bash
# 复制配置文件模板
cp config.json.example config.json

# 编辑配置（修改城市、日期、账号等）
nano config.json
```

### 运行项目

```bash
# 方式 1: 使用运行脚本（最简单）
./run.sh

# 方式 2: 手动激活虚拟环境
source activate_env.sh
python main.py
deactivate
```

### 重要提示

1. **代理功能**: 如果不需要使用代理或没有 IPv6，请在 `config.json` 中设置 `"proxy.enabled": false`
2. **权限问题**: 如果使用代理功能，需要 root 权限运行：`sudo ./run.sh`
3. **详细文档**: 查看 `环境配置说明.md` 了解完整信息

---

## English Instructions

### One-Click Installation (Recommended)

```bash
cd /home/ubuntu/Ctrip-Crawler/Linux_version
sudo bash setup_environment.sh
```

The setup script will automatically install all dependencies and configure the environment. This takes about 5-15 minutes.

### Configure Project

```bash
# Copy configuration template
cp config.json.example config.json

# Edit configuration (modify cities, dates, accounts, etc.)
nano config.json
```

### Run Project

```bash
# Method 1: Use run script (simplest)
./run.sh

# Method 2: Manual activation
source activate_env.sh
python main.py
deactivate
```

### Important Notes

1. **Proxy Feature**: If you don't need proxy or don't have IPv6, set `"proxy.enabled": false` in `config.json`
2. **Permission Issues**: If using proxy features, run with root privileges: `sudo ./run.sh`
3. **Detailed Documentation**: See `环境配置说明.md` for complete information

---

## System Requirements | 系统要求

- **OS | 操作系统**: Ubuntu 24.04 Desktop (minimal install or full)
- **Memory | 内存**: 2GB+ RAM (4GB+ recommended)
- **Storage | 存储**: 5GB+ free space
- **Network | 网络**: Stable internet connection (IPv6 support optional)

## Troubleshooting | 故障排查

### Chrome/ChromeDriver version mismatch | 版本不匹配

```bash
sudo apt-get install --reinstall chromium-chromedriver
```

### Missing libraries | 缺少库

```bash
sudo apt-get install build-essential python3-dev libmagic1 libmagic-dev
```

### Permission denied | 权限错误

```bash
sudo ./run.sh
```

### IPv6 not available | IPv6 不可用

Edit `config.json` and set | 编辑 `config.json` 设置:
```json
{
  "proxy": {
    "enabled": false
  }
}
```

---

## Support | 技术支持

- Full documentation | 完整文档: `环境配置说明.md`
- Project README | 项目说明: `doc/README.md`
- Configuration example | 配置示例: `config.json.example`

