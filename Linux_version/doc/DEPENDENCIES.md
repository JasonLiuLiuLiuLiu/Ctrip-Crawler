# Dependencies List | 依赖清单

## System Dependencies | 系统依赖

### Core System Tools | 核心系统工具

| Package | Version | Purpose | 用途 |
|---------|---------|---------|------|
| build-essential | latest | Compilation tools | 编译工具 |
| software-properties-common | latest | Software repository management | 软件源管理 |
| apt-transport-https | latest | HTTPS support for apt | apt HTTPS 支持 |
| ca-certificates | latest | SSL certificates | SSL 证书 |
| curl | latest | Data transfer tool | 数据传输工具 |
| wget | latest | Download tool | 下载工具 |
| gnupg | latest | Encryption tool | 加密工具 |
| lsb-release | latest | Linux Standard Base info | LSB 信息 |
| git | latest | Version control | 版本控制 |
| unzip | latest | Archive extraction | 压缩文件解压 |
| xz-utils | latest | XZ compression | XZ 压缩工具 |

### Python Environment | Python 环境

| Package | Version | Purpose | 用途 |
|---------|---------|---------|------|
| python3 | 3.10+ | Python interpreter | Python 解释器 |
| python3-pip | latest | Python package manager | Python 包管理器 |
| python3-dev | latest | Python development headers | Python 开发头文件 |
| python3-venv | latest | Virtual environment | 虚拟环境 |
| python3-setuptools | latest | Python setuptools | Python 安装工具 |

### Chrome/Selenium Dependencies | Chrome/Selenium 依赖

| Package | Version | Purpose | 用途 |
|---------|---------|---------|------|
| google-chrome-stable | latest | Chrome browser | Chrome 浏览器 |
| chromium-chromedriver | latest | WebDriver for Chrome | Chrome 驱动 |

**Note | 注意**: ChromeDriver version must match Chrome version | ChromeDriver 版本必须与 Chrome 版本匹配

### System Libraries | 系统库

| Package | Version | Purpose | 用途 |
|---------|---------|---------|------|
| libmagic1 | latest | File type detection library | 文件类型检测库 |
| libmagic-dev | latest | Magic library development files | Magic 库开发文件 |
| file | latest | File type command | 文件类型命令 |
| libxml2-dev | latest | XML processing library | XML 处理库 |
| libxslt1-dev | latest | XSLT processing library | XSLT 处理库 |
| zlib1g-dev | latest | Compression library | 压缩库 |

### Network Tools | 网络工具

| Package | Version | Purpose | 用途 |
|---------|---------|---------|------|
| iproute2 | latest | IP routing utilities | IP 路由工具 |
| iptables | latest | Firewall administration | 防火墙管理 |
| net-tools | latest | Network tools | 网络工具集 |
| iputils-ping | latest | Ping utility | Ping 工具 |
| dnsutils | latest | DNS utilities | DNS 工具 |
| netcat-openbsd | latest | Network utility | 网络工具 |
| tcpdump | latest | Network traffic analyzer | 网络流量分析 |

## Python Dependencies | Python 依赖

### Direct Dependencies | 直接依赖

Defined in `requirements.txt` | 定义在 `requirements.txt` 中:

| Package | Version | Purpose | 用途 |
|---------|---------|---------|------|
| pandas | 2.2.3 | Data analysis and manipulation | 数据分析和处理 |
| selenium-wire | 5.1.0 | Enhanced Selenium with request interception | 增强版 Selenium（支持请求拦截）|
| python-magic | 0.4.27 | File type identification | 文件类型识别 |

### Transitive Dependencies | 间接依赖

Automatically installed by selenium-wire | 由 selenium-wire 自动安装:

| Package | Purpose | 用途 |
|---------|---------|------|
| selenium | Web automation | Web 自动化 |
| blinker | Signal support | 信号支持 |
| h2 | HTTP/2 protocol | HTTP/2 协议 |
| hyperframe | HTTP/2 framing | HTTP/2 帧 |
| kaitaistruct | Binary data parsing | 二进制数据解析 |
| pyasn1 | ASN.1 parsing | ASN.1 解析 |
| pyOpenSSL | SSL/TLS support | SSL/TLS 支持 |
| wsproto | WebSocket protocol | WebSocket 协议 |

## Network Requirements | 网络要求

### Required | 必需

- **Internet Connection | 互联网连接**: Stable connection for data scraping | 稳定的网络连接用于数据采集
- **DNS Resolution | DNS 解析**: Must be able to resolve domain names | 必须能够解析域名

### Optional | 可选

- **IPv6 Support | IPv6 支持**: Required for proxy functionality | 代理功能需要
- **IPv6 Interfaces | IPv6 接口**: Multiple IPv6 addresses for IP rotation | 多个 IPv6 地址用于 IP 轮换

### Ports | 端口

| Port | Protocol | Purpose | 用途 |
|------|----------|---------|------|
| 1080 | SOCKS5 | Proxy server | 代理服务器 |
| 1081 | HTTP | Proxy control | 代理控制 |
| 443 | HTTPS | Web scraping | 网页采集 |

## Optional Features | 可选功能

### With Proxy | 使用代理

**Requirements | 要求**:
- IPv6 enabled | 启用 IPv6
- Root privileges | Root 权限
- Network interface configuration | 网络接口配置

**Configuration | 配置**:
```json
{
  "proxy": {
    "enabled": true,
    "ipv6_count": 120,
    "base_interface": "eth0"
  }
}
```

### Without Proxy | 不使用代理

**Requirements | 要求**:
- Only basic network connectivity | 仅需基本网络连接

**Configuration | 配置**:
```json
{
  "proxy": {
    "enabled": false
  }
}
```

## Installation Commands | 安装命令

### Automatic Installation | 自动安装

```bash
sudo bash setup_environment.sh
```

### Manual Installation | 手动安装

#### 1. System Update | 系统更新
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### 2. Core Tools | 核心工具
```bash
sudo apt-get install -y build-essential software-properties-common \
    apt-transport-https ca-certificates curl wget gnupg lsb-release \
    git unzip xz-utils
```

#### 3. Python | Python
```bash
sudo apt-get install -y python3 python3-pip python3-dev python3-venv \
    python3-setuptools
python3 -m pip install --upgrade pip
```

#### 4. System Libraries | 系统库
```bash
sudo apt-get install -y libmagic1 libmagic-dev file \
    libxml2-dev libxslt1-dev zlib1g-dev
```

#### 5. Chrome | Chrome 浏览器
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb
```

#### 6. ChromeDriver | Chrome 驱动
```bash
sudo apt-get install -y chromium-chromedriver
```

#### 7. Network Tools | 网络工具
```bash
sudo apt-get install -y iproute2 iptables net-tools iputils-ping \
    dnsutils netcat-openbsd tcpdump
```

#### 8. Python Virtual Environment | Python 虚拟环境
```bash
cd /home/ubuntu/Ctrip-Crawler/Linux_version
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

## Verification | 验证

### Check Installed Packages | 检查已安装的包

```bash
# Python version
python3 --version

# pip version
pip3 --version

# Chrome version
google-chrome --version

# ChromeDriver version
chromedriver --version

# Check IPv6
ip -6 addr show

# Check network tools
which ip iptables ping dig
```

### Verify Python Packages | 验证 Python 包

```bash
source venv/bin/activate
pip list | grep -E "(pandas|selenium|magic)"
python3 -c "import pandas; import seleniumwire; import magic; print('All imports successful!')"
deactivate
```

## Disk Space Requirements | 磁盘空间需求

| Component | Size | Description | 描述 |
|-----------|------|-------------|------|
| System packages | ~500 MB | OS-level dependencies | 系统级依赖 |
| Chrome | ~200 MB | Chrome browser | Chrome 浏览器 |
| Python venv | ~500 MB | Virtual environment + packages | 虚拟环境 + 包 |
| Project files | ~50 MB | Source code | 源代码 |
| Working space | ~1 GB | Logs, data, screenshots | 日志、数据、截图 |
| **Total** | **~2.5 GB** | **Minimum required** | **最少需要** |

**Recommended | 推荐**: 5 GB+ free space | 5 GB+ 可用空间

## Memory Requirements | 内存需求

| Scenario | RAM Required | Description | 描述 |
|----------|--------------|-------------|------|
| Minimal | 2 GB | Without proxy, single instance | 无代理，单实例 |
| Standard | 4 GB | With proxy, normal operation | 有代理，正常运行 |
| Heavy Load | 8 GB+ | Multiple instances, large datasets | 多实例，大数据集 |

## Version Compatibility | 版本兼容性

### Tested On | 已测试

- ✅ Ubuntu 24.04 LTS (Noble Numbat)
- ✅ Ubuntu 22.04 LTS (Jammy Jellyfish)
- ✅ Ubuntu 20.04 LTS (Focal Fossa)

### Should Work | 应该可用

- ⚠️ Debian 12 (Bookworm)
- ⚠️ Debian 11 (Bullseye)
- ⚠️ Linux Mint 21+
- ⚠️ Pop!_OS 22.04+

### Not Tested | 未测试

- ❓ Other Debian-based distributions
- ❓ Red Hat-based distributions (RHEL, CentOS, Fedora)
- ❓ Arch Linux
- ❓ openSUSE

**Note | 注意**: For non-Ubuntu distributions, package names may differ | 对于非 Ubuntu 发行版，包名可能不同

## Update Commands | 更新命令

### Update All Dependencies | 更新所有依赖

```bash
# System packages
sudo apt-get update
sudo apt-get upgrade -y

# Chrome
sudo apt-get install --only-upgrade google-chrome-stable

# ChromeDriver
sudo apt-get install --only-upgrade chromium-chromedriver

# Python packages
cd /home/ubuntu/Ctrip-Crawler/Linux_version
source venv/bin/activate
pip install --upgrade -r requirements.txt
deactivate
```

## Uninstallation | 卸载

### Remove Project Environment | 删除项目环境

```bash
cd /home/ubuntu/Ctrip-Crawler/Linux_version
rm -rf venv/ data/ logs/ screenshot/ cookies/ config.json
```

### Remove System Packages | 删除系统包

```bash
sudo apt-get remove google-chrome-stable chromium-chromedriver
sudo apt-get autoremove -y
sudo apt-get autoclean
```

---

**Last Updated | 最后更新**: 2025-10-11
**Document Version | 文档版本**: 1.0

