# Ctrip Flight Scraper - Setup Guide Index
# 携程航班爬虫 - 安装指南索引

## 📚 Documentation Overview | 文档概览

This directory contains all the documentation you need to set up and run the Ctrip Flight Scraper on Ubuntu 24.04.

本目录包含在 Ubuntu 24.04 上设置和运行携程航班爬虫所需的所有文档。

---

## 🚀 Quick Start | 快速开始

**For users who want to get started immediately | 想要立即开始的用户**

👉 **See**: [`QUICKSTART.md`](QUICKSTART.md)

### One Command Installation | 一键安装

```bash
cd /home/ubuntu/Ctrip-Crawler/Linux_version
sudo bash setup_environment.sh
```

---

## 📖 Available Documentation | 可用文档

### 1. **QUICKSTART.md** - Quick Start Guide | 快速开始指南
   - ⚡ **For**: Users who want to start immediately
   - ⚡ **适用**: 想要立即开始的用户
   - **Content**: One-command setup, basic configuration, running instructions
   - **内容**: 一键设置、基本配置、运行说明
   - **Language**: 中文 + English

### 2. **环境配置说明.md** - Detailed Environment Setup Guide | 详细环境配置指南
   - 📋 **For**: Users who want complete information
   - 📋 **适用**: 想要了解完整信息的用户
   - **Content**: 
     - Complete requirements
     - Manual and automatic installation
     - Configuration details
     - Troubleshooting
     - Performance optimization
   - **内容**:
     - 完整需求说明
     - 手动和自动安装
     - 详细配置说明
     - 问题排查
     - 性能优化
   - **Language**: 中文

### 3. **DEPENDENCIES.md** - Dependencies Reference | 依赖参考
   - 📦 **For**: Users who need detailed package information
   - 📦 **适用**: 需要详细包信息的用户
   - **Content**:
     - Complete list of system and Python dependencies
     - Package versions and purposes
     - Installation commands
     - Version compatibility
     - Update and uninstall procedures
   - **内容**:
     - 系统和 Python 依赖的完整列表
     - 包版本和用途
     - 安装命令
     - 版本兼容性
     - 更新和卸载步骤
   - **Language**: 中文 + English

### 4. **setup_environment.sh** - Automated Setup Script | 自动化安装脚本
   - 🔧 **For**: One-click automated installation
   - 🔧 **适用**: 一键自动化安装
   - **What it does** | 功能:
     - ✅ Updates system
     - ✅ Installs all system dependencies
     - ✅ Installs Python and packages
     - ✅ Installs Chrome and ChromeDriver
     - ✅ Configures network tools
     - ✅ Creates virtual environment
     - ✅ Sets up project structure
     - ✅ Creates helper scripts
   - **Usage** | 使用:
     ```bash
     sudo bash setup_environment.sh
     ```

### 5. **config.json.example** - Configuration Template | 配置模板
   - ⚙️ **For**: Reference for project configuration
   - ⚙️ **适用**: 项目配置参考
   - **Usage** | 使用:
     ```bash
     cp config.json.example config.json
     nano config.json
     ```

### 6. **doc/README.md** - Project Documentation | 项目文档
   - 📚 **For**: Understanding project structure and features
   - 📚 **适用**: 了解项目结构和功能
   - **Content**: Code structure, module descriptions, usage examples
   - **内容**: 代码结构、模块说明、使用示例

---

## 🎯 Choose Your Path | 选择你的路径

### Path 1: Fast Track | 快速通道 ⚡

**Best for**: Experienced users who want minimal reading

**适合**: 有经验的用户，想要快速开始

1. Read [`QUICKSTART.md`](QUICKSTART.md) (2 minutes)
2. Run `sudo bash setup_environment.sh` (10-15 minutes)
3. Configure `config.json`
4. Run `./run.sh`

### Path 2: Detailed Path | 详细路径 📖

**Best for**: Users who want to understand everything

**适合**: 想要了解所有细节的用户

1. Read [`环境配置说明.md`](环境配置说明.md) (10 minutes)
2. Review [`DEPENDENCIES.md`](DEPENDENCIES.md) (5 minutes)
3. Run `sudo bash setup_environment.sh` OR follow manual installation
4. Configure according to detailed guide
5. Test and optimize

### Path 3: Reference Path | 参考路径 📦

**Best for**: Troubleshooting or customizing installation

**适合**: 故障排查或自定义安装

1. Check [`DEPENDENCIES.md`](DEPENDENCIES.md) for specific packages
2. Refer to [`环境配置说明.md`](环境配置说明.md) for detailed procedures
3. Use [`QUICKSTART.md`](QUICKSTART.md) for quick command reference

---

## 🛠️ Generated Scripts | 生成的脚本

After running `setup_environment.sh`, you'll have these helper scripts:

运行 `setup_environment.sh` 后，你会得到这些辅助脚本：

### **activate_env.sh** - Environment Activation | 环境激活
```bash
source activate_env.sh
```
Activates the Python virtual environment | 激活 Python 虚拟环境

### **run.sh** - Quick Run Script | 快速运行脚本
```bash
./run.sh
```
Runs the scraper with environment auto-activation | 自动激活环境并运行爬虫

---

## 📋 System Requirements Summary | 系统要求摘要

### Minimum | 最低要求
- **OS**: Ubuntu 24.04 Desktop (minimal install)
- **RAM**: 2 GB
- **Storage**: 5 GB free space
- **Network**: Internet connection

### Recommended | 推荐配置
- **OS**: Ubuntu 24.04 Desktop
- **RAM**: 4 GB+
- **Storage**: 10 GB+ free space
- **Network**: Stable connection with IPv6 support

---

## 🔍 Key Dependencies | 关键依赖

### System Level | 系统级
- Python 3.10+
- Google Chrome
- ChromeDriver
- libmagic
- Network tools (iproute2, iptables)

### Python Packages | Python 包
- pandas 2.2.3
- selenium-wire 5.1.0
- python-magic 0.4.27

See [`DEPENDENCIES.md`](DEPENDENCIES.md) for complete list | 查看完整列表请参阅 [`DEPENDENCIES.md`](DEPENDENCIES.md)

---

## ⚠️ Important Notes | 重要提示

### 1. Proxy Feature | 代理功能
- **Requires**: IPv6 support and root privileges
- **需要**: IPv6 支持和 root 权限
- **Optional**: Can be disabled in config.json
- **可选**: 可在 config.json 中禁用

### 2. Permissions | 权限
- Setup script requires `sudo`
- 安装脚本需要 `sudo`
- Proxy features require root access
- 代理功能需要 root 权限

### 3. Configuration | 配置
- Must create `config.json` before running
- 运行前必须创建 `config.json`
- See `config.json.example` for template
- 参考 `config.json.example` 模板

---

## 🆘 Getting Help | 获取帮助

### Quick Solutions | 快速解决方案

1. **Installation Issues** | 安装问题
   - Check [`QUICKSTART.md`](QUICKSTART.md) - Troubleshooting section
   - 查看 [`QUICKSTART.md`](QUICKSTART.md) - 故障排查部分

2. **Dependency Issues** | 依赖问题
   - Check [`DEPENDENCIES.md`](DEPENDENCIES.md) - Verification section
   - 查看 [`DEPENDENCIES.md`](DEPENDENCIES.md) - 验证部分

3. **Configuration Issues** | 配置问题
   - Check [`环境配置说明.md`](环境配置说明.md) - Configuration section
   - 查看 [`环境配置说明.md`](环境配置说明.md) - 配置部分

4. **Runtime Issues** | 运行时问题
   - Check [`环境配置说明.md`](环境配置说明.md) - Troubleshooting section
   - 查看 [`环境配置说明.md`](环境配置说明.md) - 故障排查部分

### Common Issues | 常见问题

| Issue | Solution | Document |
|-------|----------|----------|
| ChromeDriver version mismatch | Reinstall chromedriver | QUICKSTART.md |
| IPv6 not available | Disable proxy in config | 环境配置说明.md |
| Permission denied | Run with sudo | QUICKSTART.md |
| Missing libraries | Install build-essential | DEPENDENCIES.md |
| Virtual environment error | Recreate venv | 环境配置说明.md |

---

## 📈 Next Steps After Installation | 安装后的下一步

1. ✅ Verify installation
   ```bash
   google-chrome --version
   chromedriver --version
   python3 --version
   ```

2. ✅ Configure project
   ```bash
   cp config.json.example config.json
   nano config.json
   ```

3. ✅ Test run
   ```bash
   ./run.sh
   ```

4. ✅ Check logs
   ```bash
   tail -f logs/scraper.log
   ```

5. ✅ Optimize settings
   - Read performance tips in 环境配置说明.md
   - 阅读性能优化建议

---

## 📝 Documentation Maintenance | 文档维护

These documents are maintained to help users set up the environment successfully.

这些文档旨在帮助用户成功设置环境。

**Last Updated** | 最后更新: 2025-10-11  
**Version** | 版本: 1.0  
**For Project Version** | 项目版本: Linux_version

---

## 📄 License & Legal | 许可与法律

- This project is for educational and research purposes only
- 本项目仅供教育和研究使用
- Please comply with all applicable laws and website terms of service
- 请遵守所有适用的法律和网站服务条款
- See main README for full license information
- 完整许可信息请参阅主 README

---

**Happy Scraping! | 祝使用愉快！** 🚀

