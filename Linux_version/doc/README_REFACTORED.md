# Ctrip Flight Scraper - Refactored Version

## 概述

这是携程航班爬虫的重构版本，主要改进了代码结构、可读性和可维护性。重构后的代码采用模块化设计，将原来的单一文件拆分为多个职责明确的模块。

## 项目结构

```
Linux_version/
├── main.py                    # 主程序入口
├── config.py                  # 配置管理模块
├── utils.py                   # 工具函数和选择器
├── webdriver_manager.py       # WebDriver管理
├── login_manager.py           # 登录管理
├── page_handler.py            # 页面操作处理
├── data_processor.py          # 数据处理
├── flight_scraper.py          # 主爬虫类
├── gen_proxy_servers_v2.py    # 代理服务器（重构后）
├── config.json.example        # 配置文件示例
├── requirements.txt           # 依赖包
└── README_REFACTORED.md       # 本文档
```

## 主要改进

### 1. 模块化设计
- **config.py**: 集中管理所有配置参数，支持从环境变量和JSON文件加载
- **utils.py**: 通用工具函数和CSS选择器定义
- **webdriver_manager.py**: WebDriver生命周期管理
- **login_manager.py**: 用户登录和会话管理
- **page_handler.py**: 页面导航和元素操作
- **data_processor.py**: 数据提取、处理和存储
- **flight_scraper.py**: 主爬虫逻辑协调

### 2. 配置管理
- 使用dataclass定义配置结构
- 支持从JSON文件和环境变量加载配置
- 提供配置示例文件

### 3. 错误处理
- 统一的错误处理机制
- 结构化日志记录
- 重试装饰器支持

### 4. 代码质量
- 函数职责单一，长度合理
- 类型提示支持
- 详细的文档字符串
- 上下文管理器支持

## 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置设置

复制配置文件示例并修改：

```bash
cp config.json.example config.json
```

编辑 `config.json` 文件，设置你的配置参数：

```json
{
  "scraping": {
    "crawl_cities": ["上海", "香港", "东京"],
    "crawl_days": 30,
    "direct_flight_only": true
  },
  "login": {
    "accounts": ["your_account"],
    "passwords": ["your_password"]
  }
}
```

### 3. 运行程序

```bash
python main.py
```

### 4. 使用环境变量

你也可以通过环境变量设置配置：

```bash
export CRAWL_CITIES="上海,香港,东京"
export CRAWL_DAYS=30
export ENABLE_PROXY=true
python main.py
```

## 配置说明

### 爬取配置 (scraping)
- `crawl_cities`: 要爬取的城市列表
- `crawl_days`: 爬取的天数
- `direct_flight_only`: 是否只爬取直飞航班
- `include_comfort_data`: 是否包含舒适度数据
- `max_retry_time`: 最大重试次数

### 代理配置 (proxy)
- `enabled`: 是否启用代理
- `ipv6_count`: IPv6接口数量
- `ip_mode`: 代理模式 ("random" 或 "normal")

### 登录配置 (login)
- `allowed`: 是否允许登录
- `accounts`: 账号列表
- `passwords`: 密码列表

### 调试配置 (debug)
- `enable_screenshot`: 是否启用截图
- `log_level`: 日志级别
- `log_file`: 日志文件路径

## 主要类说明

### FlightScraper
主爬虫类，协调各个模块完成数据爬取任务。

```python
with FlightScraper() as scraper:
    scraper.scrape_flight_data("上海", "香港", "2024-01-01")
```

### WebDriverManager
WebDriver生命周期管理，支持上下文管理器。

```python
with WebDriverManager() as driver_manager:
    driver_manager.navigate_to("https://example.com")
```

### LoginManager
处理用户登录和会话管理。

```python
login_manager = LoginManager(driver)
success = login_manager.login()
```

### DataProcessor
处理航班数据的提取、转换和存储。

```python
processor = DataProcessor()
processor.process_flight_data(raw_data)
merged_df = processor.merge_data()
```

## 错误处理

重构后的代码包含完善的错误处理机制：

1. **重试机制**: 使用装饰器实现自动重试
2. **日志记录**: 结构化日志记录所有操作和错误
3. **资源清理**: 自动清理WebDriver和网络接口
4. **优雅降级**: 在部分功能失败时继续执行其他任务

## 扩展性

重构后的代码具有更好的扩展性：

1. **新功能添加**: 可以轻松添加新的页面处理器或数据处理器
2. **配置扩展**: 通过dataclass可以轻松添加新的配置项
3. **多站点支持**: 可以扩展支持其他航班网站
4. **数据格式**: 可以轻松添加新的数据输出格式

## 性能优化

1. **模块化加载**: 按需加载模块，减少内存占用
2. **连接复用**: WebDriver连接复用
3. **异步处理**: 代理服务器使用异步处理
4. **资源管理**: 及时释放不需要的资源

## 注意事项

1. **法律合规**: 请确保遵守相关法律法规和网站服务条款
2. **账号安全**: 不要在代码中硬编码账号密码
3. **系统权限**: 需要root权限创建网络接口
4. **网络环境**: 需要支持IPv6的网络环境

## 故障排除

### 常见问题

1. **WebDriver启动失败**: 检查Chrome浏览器和ChromeDriver是否正确安装
2. **代理连接失败**: 检查网络接口配置和IPv6支持
3. **登录失败**: 检查账号密码和验证码处理
4. **数据解析失败**: 检查网站结构是否发生变化

### 调试模式

启用调试模式获取更多信息：

```json
{
  "debug": {
    "enable_screenshot": true,
    "log_level": "DEBUG",
    "log_file": "scraper.log"
  }
}
```

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。在提交代码前，请确保：

1. 代码符合PEP 8规范
2. 添加适当的类型提示
3. 包含必要的文档字符串
4. 通过基本的测试验证

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

