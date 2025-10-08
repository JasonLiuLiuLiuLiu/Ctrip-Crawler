"""
WebDriver management module for Ctrip Flight Scraper
Handles WebDriver initialization, configuration, and cleanup
"""

import logging
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from config import config


class WebDriverManager:
    """Manages WebDriver lifecycle and configuration"""
    
    def __init__(self):
        self.driver = None
        self.logger = logging.getLogger(__name__)
    
    def create_driver(self):
        """Create and configure Chrome WebDriver"""
        try:
            options = self._create_chrome_options()
            self.driver = webdriver.Chrome(options=options)
            self._configure_driver()
            self.logger.info("WebDriver created successfully")
            return self.driver
        except Exception as e:
            self.logger.error(f"Failed to create WebDriver: {e}")
            raise
    
    def _create_chrome_options(self) -> Options:
        """Create Chrome options with configuration"""
        options = Options()
        
        # Basic options
        options.add_argument("--incognito")  # Incognito mode
        options.add_argument("--headless")   # Headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--pageLoadStrategy=eager")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-certificate-errors-spki-list")
        options.add_argument("--ignore-ssl-errors")
        
        # Disable images for faster loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
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
            
            # Set window size
            self.driver.set_window_size(1280, 480)
    
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

