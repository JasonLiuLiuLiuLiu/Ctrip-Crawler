# 项目结构说明

## 目录结构

```
Linux_version/
├── doc/                          # 📚 文档目录
│   ├── README.md                 # 文档索引
│   ├── readme.md                 # 原始项目说明
│   ├── README_REFACTORED.md      # 重构后项目说明
│   ├── REFACTOR_SUMMARY.md       # 重构总结报告
│   ├── PROXY_REFACTOR_GUIDE.md   # 代理重构指南
│   ├── MIGRATION_GUIDE.md        # 迁移指南
│   └── CLEANUP_SUMMARY.md        # 清理总结
│
├── proxy/                        # 🔧 代理服务器模块
│   ├── __init__.py               # 模块导出
│   ├── config_manager.py         # 配置管理
│   ├── network_manager.py        # 网络接口管理
│   ├── connection_handler.py     # 连接处理
│   └── proxy_server.py           # 代理服务器
│
├── config.py                     # ⚙️ 配置管理
├── main.py                       # 🚀 主程序入口
├── utils.py                      # 🛠️ 工具函数
│
├── flight_scraper.py             # ✈️ 航班爬虫
├── data_processor.py             # 📊 数据处理
├── login_manager.py              # 🔐 登录管理
├── page_handler.py               # 📄 页面处理
├── webdriver_manager.py          # 🌐 WebDriver管理
│
├── gen_proxy_servers.py          # 📡 原始代理服务器
├── gen_proxy_servers_v2.py       # 📡 重构后代理服务器
├── test_proxy_refactor.py        # 🧪 代理重构测试
│
├── config.json.example           # 📋 配置示例
└── requirements.txt              # 📦 依赖包
```

## 目录说明

### 📚 doc/ - 文档目录
包含项目的所有文档，与代码分离，便于维护和阅读。

### 🔧 proxy/ - 代理服务器模块
重构后的代理服务器模块，采用模块化设计：
- **config_manager.py**: 配置管理和验证
- **network_manager.py**: 网络接口管理
- **connection_handler.py**: SOCKS5连接处理
- **proxy_server.py**: 主代理服务器协调

### ⚙️ 核心模块
- **config.py**: 全局配置管理
- **main.py**: 应用程序主入口
- **utils.py**: 通用工具函数

### ✈️ 爬虫模块
- **flight_scraper.py**: 主爬虫逻辑
- **data_processor.py**: 数据处理和存储
- **login_manager.py**: 用户登录管理
- **page_handler.py**: 页面操作处理
- **webdriver_manager.py**: WebDriver生命周期管理

### 📡 代理服务器
- **gen_proxy_servers.py**: 原始代理服务器（保留）
- **gen_proxy_servers_v2.py**: 重构后的代理服务器（向后兼容）

### 🧪 测试
- **test_proxy_refactor.py**: 代理重构测试套件

## 文件命名规范

### Python文件
- 使用小写字母和下划线：`flight_scraper.py`
- 模块名清晰表达功能：`config_manager.py`
- 测试文件以`test_`开头：`test_proxy_refactor.py`

### 文档文件
- 使用大写字母和下划线：`REFACTOR_SUMMARY.md`
- 描述性名称：`PROXY_REFACTOR_GUIDE.md`
- 索引文件：`README.md`

### 配置文件
- 示例文件以`.example`结尾：`config.json.example`
- 依赖文件：`requirements.txt`

## 模块依赖关系

```
main.py
├── config.py
├── utils.py
├── flight_scraper.py
│   ├── login_manager.py
│   ├── page_handler.py
│   ├── data_processor.py
│   └── webdriver_manager.py
└── gen_proxy_servers_v2.py
    └── proxy/
        ├── config_manager.py
        ├── network_manager.py
        ├── connection_handler.py
        └── proxy_server.py
```

## 代码组织原则

### 1. 单一职责
每个模块都有明确的单一职责，避免功能混杂。

### 2. 依赖注入
配置和依赖通过构造函数注入，提高可测试性。

### 3. 接口分离
公共接口与内部实现分离，便于维护和扩展。

### 4. 文档分离
所有文档集中在`doc/`目录，与代码分离。

## 扩展指南

### 添加新功能
1. 在相应模块中添加功能
2. 更新配置（如需要）
3. 添加测试
4. 更新文档

### 添加新模块
1. 创建新的Python文件
2. 遵循命名规范
3. 添加适当的导入导出
4. 更新相关文档

### 修改配置
1. 更新`config.py`中的配置类
2. 更新`config.json.example`
3. 更新相关文档

## 维护建议

### 定期维护
- 检查并更新依赖包
- 清理未使用的代码
- 更新文档

### 代码审查
- 确保遵循命名规范
- 检查模块职责是否清晰
- 验证测试覆盖率

### 文档维护
- 保持文档与代码同步
- 更新交叉引用
- 检查链接有效性
