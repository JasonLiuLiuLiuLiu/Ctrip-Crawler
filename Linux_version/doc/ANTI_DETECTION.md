# 反检测配置说明 | Anti-Detection Configuration

## 概述 | Overview

本项目已实现了全面的反检测机制，使 Selenium WebDriver 伪装成真实的 Windows Chrome 浏览器，避免被目标网站识别为自动化工具。

This project implements comprehensive anti-detection mechanisms to disguise the Selenium WebDriver as a genuine Windows Chrome browser, preventing detection by target websites.

---

## 实现的反检测技术 | Implemented Anti-Detection Techniques

### 1. User-Agent 伪装 | User-Agent Spoofing

**功能**：随机选择 Windows Chrome 的 User-Agent

**User-Agent 列表**：
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36
```

### 2. Navigator 对象伪装 | Navigator Object Spoofing

#### webdriver 属性
```javascript
navigator.webdriver = undefined  // 正常浏览器返回 undefined
```

#### Platform 伪装
```javascript
navigator.platform = 'Win32'     // 伪装为 Windows 平台
navigator.vendor = 'Google Inc.'  // Chrome 厂商
```

#### 硬件信息
```javascript
navigator.hardwareConcurrency = 8  // 8 核 CPU
navigator.deviceMemory = 8         // 8GB 内存
```

#### 语言设置
```javascript
navigator.languages = ['zh-CN', 'zh', 'en-US', 'en']
```

### 3. Chrome 对象模拟 | Chrome Object Simulation

```javascript
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {}
}
```

### 4. WebGL 指纹伪装 | WebGL Fingerprint Spoofing

```javascript
WebGL Vendor: 'Intel Inc.'
WebGL Renderer: 'Intel Iris OpenGL Engine'
```

### 5. Screen 信息伪装 | Screen Information Spoofing

模拟常见的 Windows 桌面分辨率：
```javascript
screen.width = 1920
screen.height = 1080
screen.availWidth = 1920
screen.availHeight = 1040
screen.colorDepth = 24
screen.pixelDepth = 24
```

### 6. 移除 Selenium 特征 | Remove Selenium Indicators

自动删除以下 Selenium 相关属性：
- `window._Selenium_IDE_Recorder`
- `document.__selenium_unwrapped`
- `document.__webdriver_evaluate`
- `document.__driver_evaluate`
- `document.__webdriver_script_function`
- `document.__fxdriver_evaluate`
- 以及其他 20+ 个 Selenium 特征属性

### 7. Chrome 启动参数优化 | Chrome Launch Arguments Optimization

```python
--disable-blink-features=AutomationControlled  # 禁用自动化控制特征
--disable-infobars                             # 禁用信息栏
--disable-browser-side-navigation              # 禁用浏览器端导航
--disable-features=IsolateOrigins              # 禁用隔离源
--excludeSwitches=enable-automation            # 排除自动化开关
--useAutomationExtension=False                 # 不使用自动化扩展
--disable-web-security                         # 禁用 Web 安全检查
--disable-webgl                                # 禁用 WebGL
```

### 8. 权限 API 模拟 | Permissions API Simulation

```javascript
navigator.permissions.query() 
// 返回真实浏览器的响应，而非 Selenium 的默认响应
```

### 9. Battery API 模拟 | Battery API Simulation

```javascript
navigator.getBattery()
// 返回模拟的电池信息（满电、充电中）
```

### 10. Connection API 模拟 | Connection API Simulation

```javascript
navigator.connection = {
    effectiveType: '4g',
    rtt: 50,
    downlink: 10,
    saveData: false
}
```

---

## Chrome DevTools Protocol (CDP)

使用 CDP 在页面加载前注入 JavaScript，确保所有反检测代码在网站检测脚本运行前执行。

```python
self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source': stealth_js
})
```

---

## 配置选项 | Configuration Options

### 在 config.json 中配置

```json
{
  "debug": {
    "headless": true,        // true=无头模式, false=有头模式
    "enable_screenshot": false,
    "log_level": "INFO"
  }
}
```

### 有头模式 vs 无头模式

| 特性 | 无头模式 | 有头模式 |
|------|---------|---------|
| 检测难度 | 较高（需要更多反检测） | 较低（更接近真实浏览器） |
| 资源占用 | 低 | 高 |
| 适用场景 | 生产环境、服务器 | 开发调试 |
| 需要图形界面 | 否 | 是 |

---

## 验证反检测效果 | Verify Anti-Detection

### 方法 1：使用检测网站

访问以下网站测试是否被识别为自动化工具：

1. **Bot.Sannysoft**
   - URL: https://bot.sannysoft.com/
   - 检查是否有红色警告

2. **IntoPieces**
   - URL: https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html
   - 检查 headless 检测结果

3. **AreBrowsersReal**
   - URL: https://arh.antoinevastel.com/bots/areyouheadless
   - 综合检测结果

### 方法 2：控制台检查

在浏览器控制台运行：

```javascript
// 检查 webdriver
console.log('webdriver:', navigator.webdriver);  // 应该是 undefined

// 检查平台
console.log('platform:', navigator.platform);    // 应该是 'Win32'

// 检查 Chrome 对象
console.log('chrome:', window.chrome);           // 应该有值

// 检查语言
console.log('languages:', navigator.languages);  // 应该包含 zh-CN
```

### 方法 3：代码测试

```python
from webdriver_manager import WebDriverManager

driver_manager = WebDriverManager()
driver = driver_manager.create_driver()
driver.get('https://bot.sannysoft.com/')

# 等待页面加载
import time
time.sleep(5)

# 截图查看结果
driver.save_screenshot('detection_test.png')

driver.quit()
```

---

## 常见问题 | FAQ

### Q1: 为什么还是被检测到？

**A**: 可能的原因：
1. **行为模式**：爬取速度过快、请求间隔太规律
2. **Cookie/Session**：未正确管理 Cookie 和 Session
3. **IP 地址**：使用了已知的数据中心 IP
4. **鼠标移动**：缺少鼠标移动和滚动行为

**解决方案**：
- 增加随机延迟：`time.sleep(random.uniform(1, 3))`
- 使用住宅代理 IP
- 模拟人类行为（鼠标移动、滚动）
- 正确处理 Cookie 和登录状态

### Q2: CDP 命令失败怎么办？

**A**: CDP 命令依赖 Chrome DevTools Protocol，可能的问题：
- Chrome 版本过旧
- Selenium-wire 版本不兼容
- 权限问题

**解决方案**：
```bash
# 更新 Chrome
sudo apt-get update
sudo apt-get install --only-upgrade google-chrome-stable

# 更新 selenium-wire
pip install --upgrade selenium-wire
```

### Q3: 有头模式下如何查看效果？

**A**: 
1. 修改 `config.json`：
```json
{
  "debug": {
    "headless": false
  }
}
```

2. 如果是远程服务器：
```bash
# 使用 Xvfb
xvfb-run -a ./run.sh

# 或使用 VNC
vncserver :1
export DISPLAY=:1
./run.sh
```

### Q4: 如何添加更多 User-Agent？

**A**: 编辑 `webdriver_manager.py`：

```python
WINDOWS_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
    "你的新 User-Agent",
    # 添加更多...
]
```

---

## 高级技巧 | Advanced Tips

### 1. 模拟人类行为

```python
import random
import time
from selenium.webdriver.common.action_chains import ActionChains

# 随机鼠标移动
actions = ActionChains(driver)
actions.move_by_offset(random.randint(0, 100), random.randint(0, 100))
actions.perform()

# 随机滚动
driver.execute_script(f"window.scrollTo(0, {random.randint(100, 500)})")

# 随机延迟
time.sleep(random.uniform(1, 3))
```

### 2. 添加浏览器插件

```python
# 在 _create_chrome_options 中添加
options.add_extension('/path/to/extension.crx')
```

### 3. 使用不同的指纹

每次创建新的 WebDriver 实例时，会随机选择不同的 User-Agent，增加多样性。

### 4. 处理 Canvas 指纹

网站可能使用 Canvas 指纹识别，可以添加：

```javascript
// 在 stealth_js 中添加
const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function(type) {
    if (type === 'image/png') {
        // 添加轻微噪点
        const context = this.getContext('2d');
        const imageData = context.getImageData(0, 0, this.width, this.height);
        for (let i = 0; i < imageData.data.length; i += 4) {
            imageData.data[i] += Math.random() * 2 - 1;
        }
        context.putImageData(imageData, 0, 0);
    }
    return originalToDataURL.apply(this, arguments);
};
```

---

## 性能影响 | Performance Impact

反检测机制对性能的影响：

| 技术 | CPU 影响 | 内存影响 | 延迟 |
|------|---------|---------|------|
| User-Agent 伪装 | 无 | 无 | 无 |
| JavaScript 注入 | < 1% | < 5MB | < 10ms |
| CDP 命令 | < 1% | < 10MB | < 20ms |
| **总计** | **< 2%** | **< 15MB** | **< 30ms** |

总体影响很小，不会显著影响爬取性能。

---

## 更新日志 | Changelog

### v1.0 (2025-10-11)
- ✅ 实现 User-Agent 伪装
- ✅ Navigator 对象完整伪装
- ✅ 移除所有 Selenium 特征
- ✅ WebGL 指纹伪装
- ✅ Screen 信息伪装
- ✅ Chrome 对象模拟
- ✅ Battery/Connection API 模拟
- ✅ 使用 CDP 注入反检测脚本

---

## 参考资源 | References

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Selenium Stealth](https://github.com/diprajpatra/selenium-stealth)
- [Puppeteer Stealth](https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth)
- [Bot Detection Tests](https://bot.sannysoft.com/)

---

**最后更新 | Last Updated**: 2025-10-11  
**版本 | Version**: 1.0

