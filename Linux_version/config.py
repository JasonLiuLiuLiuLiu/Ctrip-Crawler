"""
Configuration module for Ctrip Flight Scraper
Centralized configuration management for better maintainability
"""

import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ScrapingConfig:
    """Configuration for flight scraping parameters"""
    # Cities to crawl
    crawl_cities: List[str] = None
    
    # Date range configuration
    begin_date: Optional[str] = None  # Format: '2023-12-01'
    end_date: Optional[str] = None    # Format: '2023-12-31'
    start_interval: int = 1           # T+N days
    crawl_days: int = 60              # Number of days to crawl
    days_interval: int = 1            # Interval between dates
    
    # Timing configuration
    crawl_interval: int = 1           # Interval between city crawls (seconds)
    max_wait_time: int = 10           # Max page load wait time (seconds)
    max_retry_time: int = 5           # Max retry attempts
    
    # Flight filtering
    direct_flight_only: bool = True   # Only crawl direct flights
    include_comfort_data: bool = False # Include flight comfort information
    
    # Data processing
    delete_unimportant_info: bool = False  # Remove unimportant columns
    rename_columns: bool = True            # Rename DataFrame columns
    
    def __post_init__(self):
        if self.crawl_cities is None:
            self.crawl_cities = ["上海", "香港", "东京"]


@dataclass
class ProxyConfig:
    """Configuration for proxy settings"""
    enabled: bool = True
    ipv6_count: int = 120
    base_interface: str = "eth0"
    ip_mode: str = "normal"  # "random" or "normal"
    delete_interface: bool = False
    
    # New proxy server settings
    proxy_port: int = 1080
    proxy_bind_address: str = "0.0.0.0"
    control_port: int = 1081
    control_bind_address: str = "127.0.0.1"
    test_address: str = "2400:3200::1"
    max_retries: int = 3
    timeout: int = 5


@dataclass
class LoginConfig:
    """Configuration for login settings"""
    allowed: bool = True
    accounts: List[str] = None
    passwords: List[str] = None
    cookies_file: str = "cookies.json"
    required_cookies: List[str] = None
    
    def __post_init__(self):
        if self.accounts is None:
            self.accounts = ['', '']
        if self.passwords is None:
            self.passwords = ['', '']
        if self.required_cookies is None:
            self.required_cookies = [
                "AHeadUserInfo", "DUID", "IsNonUser", 
                "_udl", "cticket", "login_type", "login_uid"
            ]


@dataclass
class DebugConfig:
    """Configuration for debugging and logging"""
    enable_screenshot: bool = False
    log_level: str = "INFO"
    log_file: Optional[str] = None


@dataclass
class AppConfig:
    """Main application configuration"""
    scraping: ScrapingConfig = None
    proxy: ProxyConfig = None
    login: LoginConfig = None
    debug: DebugConfig = None
    
    def __post_init__(self):
        if self.scraping is None:
            self.scraping = ScrapingConfig()
        if self.proxy is None:
            self.proxy = ProxyConfig()
        if self.login is None:
            self.login = LoginConfig()
        if self.debug is None:
            self.debug = DebugConfig()


# Global configuration instance
config = AppConfig()


def load_config_from_env():
    """Load configuration from environment variables"""
    # Scraping config
    if os.getenv('CRAWL_CITIES'):
        config.scraping.crawl_cities = os.getenv('CRAWL_CITIES').split(',')
    
    if os.getenv('BEGIN_DATE'):
        config.scraping.begin_date = os.getenv('BEGIN_DATE')
    
    if os.getenv('END_DATE'):
        config.scraping.end_date = os.getenv('END_DATE')
    
    if os.getenv('CRAWL_DAYS'):
        config.scraping.crawl_days = int(os.getenv('CRAWL_DAYS'))
    
    # Proxy config
    if os.getenv('ENABLE_PROXY'):
        config.proxy.enabled = os.getenv('ENABLE_PROXY').lower() == 'true'
    
    if os.getenv('IPV6_COUNT'):
        config.proxy.ipv6_count = int(os.getenv('IPV6_COUNT'))
    
    # Login config
    if os.getenv('LOGIN_ACCOUNTS'):
        config.login.accounts = os.getenv('LOGIN_ACCOUNTS').split(',')
    
    if os.getenv('LOGIN_PASSWORDS'):
        config.login.passwords = os.getenv('LOGIN_PASSWORDS').split(',')


def load_config_from_file(config_file: str = "config.json"):
    """Load configuration from JSON file"""
    if os.path.exists(config_file):
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update config with file data
        if 'scraping' in data:
            for key, value in data['scraping'].items():
                if hasattr(config.scraping, key):
                    setattr(config.scraping, key, value)
        
        if 'proxy' in data:
            for key, value in data['proxy'].items():
                if hasattr(config.proxy, key):
                    setattr(config.proxy, key, value)
        
        if 'login' in data:
            for key, value in data['login'].items():
                if hasattr(config.login, key):
                    setattr(config.login, key, value)
        
        if 'debug' in data:
            for key, value in data['debug'].items():
                if hasattr(config.debug, key):
                    setattr(config.debug, key, value)


# Load configuration on module import
load_config_from_env()
load_config_from_file()

