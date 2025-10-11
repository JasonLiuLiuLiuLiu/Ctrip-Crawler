"""
WebDriver management module for Ctrip Flight Scraper
Handles WebDriver initialization, configuration, and cleanup
"""

import logging
import random
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from config import config


class WebDriverManager:
    """Manages WebDriver lifecycle and configuration"""
    
    # Windows Chrome User-Agent list
    WINDOWS_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    ]
    
    def __init__(self):
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.user_agent = random.choice(self.WINDOWS_USER_AGENTS)
    
    def create_driver(self):
        """Create and configure Chrome WebDriver"""
        try:
            options = self._create_chrome_options()
            self.driver = webdriver.Chrome(options=options)
            self._configure_driver()
            self._inject_stealth_js()
            self.logger.info("WebDriver created successfully with stealth mode")
            return self.driver
        except Exception as e:
            self.logger.error(f"Failed to create WebDriver: {e}")
            raise
    
    def _create_chrome_options(self) -> Options:
        """Create Chrome options with configuration"""
        options = Options()
        
        # Set User-Agent to Windows Chrome
        options.add_argument(f"user-agent={self.user_agent}")
        
        # Basic options
        options.add_argument("--incognito")  # Incognito mode
        
        # Headless mode (can be controlled via config)
        if config.debug.headless:
            options.add_argument("--headless=new")  # Use new headless mode
            # Add window size for headless mode to avoid detection
            options.add_argument("--window-size=1920,1080")
        
        # Anti-detection options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        
        # Remove automation flags
        options.add_experimental_option("excludeSwitches", [
            "enable-automation",
            "enable-logging"
        ])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Performance and stability options
        options.add_argument("--disable-extensions")
        options.add_argument("--pageLoadStrategy=eager")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-certificate-errors-spki-list")
        options.add_argument("--ignore-ssl-errors")
        
        # Additional stealth options
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-webgl")
        options.add_argument("--disable-popup-blocking")
        
        # Language and locale (Windows default)
        options.add_argument("--lang=zh-CN")
        options.add_experimental_option("prefs", {
            "intl.accept_languages": "zh-CN,zh,en-US,en",
            "profile.managed_default_content_settings.images": 2,  # Disable images
            "profile.default_content_setting_values.notifications": 2,  # Block notifications
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        })
        
        # Proxy configuration
        if config.proxy.enabled:
            options.add_argument("--proxy-server=socks5://127.0.0.1:1080")
        
        return options
    
    def _configure_driver(self):
        """Configure driver settings"""
        if self.driver:
            # Set page load timeout
            timeout = config.scraping.max_wait_time * config.scraping.max_retry_time
            self.driver.set_page_load_timeout(timeout)
            
            # Set window size (Windows typical resolution)
            if not config.debug.headless:
                self.driver.set_window_size(1920, 1080)
            else:
                self.driver.set_window_size(1920, 1080)
    
    def _inject_stealth_js(self):
        """Inject JavaScript to hide automation and simulate real browser"""
        if not self.driver:
            return
        
        try:
            # Stealth JavaScript to hide webdriver property and other automation indicators
            stealth_js = """
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Overwrite the `plugins` property to use a custom getter
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Overwrite the `languages` property to use a custom getter
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en-US', 'en']
                });
                
                // Overwrite the chrome property
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // Mock platform to Windows
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });
                
                // Mock vendor
                Object.defineProperty(navigator, 'vendor', {
                    get: () => 'Google Inc.'
                });
                
                // Add hardware concurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });
                
                // Add device memory
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8
                });
                
                // Mock permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Hide automation in Chrome
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false
                });
                
                // Prevent detection through toString
                const originalToString = Function.prototype.toString;
                Function.prototype.toString = function() {
                    if (this === window.navigator.permissions.query) {
                        return 'function query() { [native code] }';
                    }
                    return originalToString.call(this);
                };
                
                // Mock WebGL
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.call(this, parameter);
                };
                
                // Mock Battery API
                Object.defineProperty(navigator, 'getBattery', {
                    get: () => () => Promise.resolve({
                        charging: true,
                        chargingTime: 0,
                        dischargingTime: Infinity,
                        level: 1,
                        addEventListener: () => {},
                        removeEventListener: () => {},
                        dispatchEvent: () => true
                    })
                });
                
                // Add connection info
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10,
                        saveData: false
                    })
                });
                
                // Mock screen resolution (common Windows resolution)
                Object.defineProperty(screen, 'width', { get: () => 1920 });
                Object.defineProperty(screen, 'height', { get: () => 1080 });
                Object.defineProperty(screen, 'availWidth', { get: () => 1920 });
                Object.defineProperty(screen, 'availHeight', { get: () => 1040 });
                Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
                Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });
                
                // Remove Selenium IDE indicators
                delete window._Selenium_IDE_Recorder;
                delete window.document.__selenium_unwrapped;
                delete window.document.__webdriver_evaluate;
                delete window.document.__driver_evaluate;
                delete window.document.__webdriver_script_function;
                delete window.document.__webdriver_script_func;
                delete window.document.__webdriver_script_fn;
                delete window.document.__fxdriver_evaluate;
                delete window.document.__driver_unwrapped;
                delete window.document.__webdriver_unwrapped;
                delete window.document.__fxdriver_unwrapped;
                delete window.document.__selenium_evaluate;
                delete window.document.__selenium_evaluate__;
                
                // Mock mouse and touch events
                window.ontouchstart = null;
                
                console.log('Stealth mode activated');
            """
            
            # Execute stealth JavaScript using CDP (Chrome DevTools Protocol)
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': stealth_js
            })
            
            self.logger.info("Stealth JavaScript injected successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to inject stealth JavaScript: {e}")
            # Non-critical, continue execution
    
    def quit_driver(self):
        """Safely quit the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver quit successfully")
            except Exception as e:
                self.logger.error(f"Error quitting WebDriver: {e}")
            finally:
                self.driver = None
    
    def refresh_driver(self):
        """Refresh the current page"""
        if self.driver:
            try:
                self.driver.refresh()
                self.logger.info("Page refreshed successfully")
            except Exception as e:
                self.logger.error(f"Failed to refresh page: {e}")
                raise
    
    def take_screenshot(self, filename: str = None):
        """Take a screenshot for debugging"""
        if not config.debug.enable_screenshot:
            return
        
        if not self.driver:
            self.logger.warning("No driver available for screenshot")
            return
        
        try:
            if not filename:
                from utils import get_current_timestamp
                filename = f'screenshot/screenshot_{get_current_timestamp()}.png'
            
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        if self.driver:
            return self.driver.current_url
        return ""
    
    def get_page_title(self) -> str:
        """Get current page title"""
        if self.driver:
            return self.driver.title
        return ""
    
    def navigate_to(self, url: str):
        """Navigate to a specific URL"""
        if self.driver:
            try:
                self.driver.get(url)
                self.logger.info(f"Navigated to: {url}")
            except Exception as e:
                self.logger.error(f"Failed to navigate to {url}: {e}")
                raise
    
    def execute_javascript(self, script: str):
        """Execute JavaScript code"""
        if self.driver:
            try:
                return self.driver.execute_script(script)
            except Exception as e:
                self.logger.error(f"Failed to execute JavaScript: {e}")
                raise
    
    def add_cookie(self, cookie_dict: dict):
        """Add a cookie to the current session"""
        if self.driver:
            try:
                self.driver.add_cookie(cookie_dict)
            except Exception as e:
                self.logger.error(f"Failed to add cookie: {e}")
                raise
    
    def get_cookies(self) -> list:
        """Get all cookies from current session"""
        if self.driver:
            try:
                return self.driver.get_cookies()
            except Exception as e:
                self.logger.error(f"Failed to get cookies: {e}")
                return []
        return []
    
    def clear_cookies(self):
        """Clear all cookies"""
        if self.driver:
            try:
                self.driver.delete_all_cookies()
                self.logger.info("All cookies cleared")
            except Exception as e:
                self.logger.error(f"Failed to clear cookies: {e}")
    
    def wait_for_request(self, pattern: str, timeout: int = None):
        """Wait for a specific network request"""
        if not self.driver:
            raise RuntimeError("No driver available")
        
        if timeout is None:
            timeout = config.scraping.max_wait_time
        
        try:
            return self.driver.wait_for_request(pattern, timeout=timeout)
        except Exception as e:
            self.logger.error(f"Failed to wait for request {pattern}: {e}")
            raise
    
    def clear_requests(self):
        """Clear the request history"""
        if self.driver:
            try:
                del self.driver.requests
                self.logger.info("Request history cleared")
            except Exception as e:
                self.logger.error(f"Failed to clear requests: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        self.create_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.quit_driver()

