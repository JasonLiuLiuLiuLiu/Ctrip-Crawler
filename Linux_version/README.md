# Ctrip Flight Scraper - Linux Version
# 携程航班爬虫 - Linux 版本

## 📚 文档 | Documentation

所有文档已移至 `doc/` 目录。请查看：

All documentation has been moved to the `doc/` directory. Please see:

### 快速开始 | Quick Start

**立即开始？看这里！| Want to start immediately? Look here!**

👉 **[快速开始指南 Quick Start Guide](doc/QUICKSTART.md)**

### 一键安装 | One-Click Installation

```bash
cd /home/ubuntu/Ctrip-Crawler/Linux_version
sudo bash setup_environment.sh
```

---

## 📖 完整文档列表 | Full Documentation List

### 主要文档 | Main Documentation

1. **[README_SETUP.md](doc/README_SETUP.md)** - 文档索引 | Documentation Index
   - 📋 从这里开始浏览所有文档
   - 📋 Start here to browse all documentation

2. **[QUICKSTART.md](doc/QUICKSTART.md)** - 快速开始指南 | Quick Start Guide
   - ⚡ 最快速的入门方式
   - ⚡ Fastest way to get started

3. **[环境配置说明.md](doc/环境配置说明.md)** - 详细配置指南 | Detailed Setup Guide
   - 📖 完整的安装和配置说明
   - 📖 Complete installation and configuration instructions

4. **[DEPENDENCIES.md](doc/DEPENDENCIES.md)** - 依赖清单 | Dependencies List
   - 📦 所有依赖的详细信息
   - 📦 Detailed information about all dependencies

5. **[README.md](doc/README.md)** - 项目说明 | Project Documentation
   - 📚 项目结构和功能说明
   - 📚 Project structure and features

---

## 🚀 快速开始流程 | Quick Start Process

### 1. 安装环境 | Install Environment

```bash
# 运行自动化安装脚本
# Run automated installation script
sudo bash setup_environment.sh
```

### 2. 配置项目 | Configure Project

```bash
# 复制配置模板
# Copy configuration template
cp config.json.example config.json

# 编辑配置
# Edit configuration
nano config.json
```

### 3. 运行项目 | Run Project

```bash
# 方式 1: 使用运行脚本（推荐）
# Method 1: Use run script (recommended)
./run.sh

# 方式 2: 手动激活环境
# Method 2: Manual activation
source activate_env.sh
python main.py
deactivate
```

---

## 📋 系统要求 | System Requirements

- **操作系统 | OS**: Ubuntu 24.04 Desktop (minimal install)
- **内存 | RAM**: 2 GB+ (推荐 4GB+ | recommended 4GB+)
- **存储 | Storage**: 5 GB+ free space
- **网络 | Network**: Internet connection (IPv6 optional)

---

## 🔧 主要文件 | Main Files

```
Linux_version/
├── setup_environment.sh    # 环境安装脚本 | Environment setup script
├── main.py                 # 主程序 | Main program
├── config.json.example     # 配置模板 | Configuration template
├── requirements.txt        # Python 依赖 | Python dependencies
├── doc/                    # 📚 所有文档 | All documentation
│   ├── README_SETUP.md     # 文档索引 | Documentation index
│   ├── QUICKSTART.md       # 快速开始 | Quick start
│   ├── 环境配置说明.md      # 详细配置 | Detailed setup
│   ├── DEPENDENCIES.md     # 依赖清单 | Dependencies
│   └── README.md           # 项目说明 | Project docs
├── *.py                    # Python 模块 | Python modules
└── proxy/                  # 代理相关 | Proxy related

安装后生成的文件 | Generated after installation:
├── venv/                   # Python 虚拟环境 | Virtual environment
├── data/                   # 数据目录 | Data directory
├── logs/                   # 日志目录 | Logs directory
├── screenshot/             # 截图目录 | Screenshots directory
├── activate_env.sh         # 环境激活脚本 | Activation script
└── run.sh                  # 快速运行脚本 | Quick run script
```

---

## ⚠️ 重要提示 | Important Notes

### 代理功能 | Proxy Feature
- 需要 IPv6 支持 | Requires IPv6 support
- 需要 root 权限 | Requires root privileges  
- 可选功能 | Optional feature
- 在 `config.json` 中可以禁用 | Can be disabled in `config.json`

### 配置文件 | Configuration
- 必须创建 `config.json` | Must create `config.json`
- 包含敏感信息 | Contains sensitive information
- 已添加到 `.gitignore` | Added to `.gitignore`

---

## 🆘 需要帮助？ | Need Help?

### 查看文档 | Check Documentation

1. **安装问题** | Installation Issues → [QUICKSTART.md](doc/QUICKSTART.md)
2. **配置问题** | Configuration Issues → [环境配置说明.md](doc/环境配置说明.md)
3. **依赖问题** | Dependency Issues → [DEPENDENCIES.md](doc/DEPENDENCIES.md)
4. **项目使用** | Project Usage → [doc/README.md](doc/README.md)

### 常见问题 | Common Issues

| 问题 Issue | 解决方案 Solution |
|-----------|------------------|
| ChromeDriver 版本不匹配 | `sudo apt-get install --reinstall chromium-chromedriver` |
| 缺少 Python 库 | `sudo apt-get install build-essential python3-dev` |
| IPv6 不可用 | 在 config.json 中设置 `proxy.enabled: false` |
| 权限错误 | 使用 `sudo` 运行脚本 |

---

## 📝 快速命令参考 | Quick Command Reference

```bash
# 安装环境 | Install environment
sudo bash setup_environment.sh

# 激活环境 | Activate environment
source activate_env.sh

# 运行项目 | Run project
./run.sh

# 查看日志 | View logs
tail -f logs/scraper.log

# 验证安装 | Verify installation
google-chrome --version
chromedriver --version
python3 --version
```

---

## 📄 许可 | License

本项目仅供教育和研究使用。请遵守相关法律法规和网站服务条款。

This project is for educational and research purposes only. Please comply with all applicable laws and website terms of service.

---

**🎯 开始使用 | Get Started**: [doc/QUICKSTART.md](doc/QUICKSTART.md)

**📚 浏览所有文档 | Browse All Docs**: [doc/README_SETUP.md](doc/README_SETUP.md)

