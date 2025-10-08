"""
Utility functions for Ctrip Flight Scraper
Common helper functions and utilities
"""

import os
import time
import logging
from datetime import datetime as dt, timedelta
from typing import List, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup structured logging"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            *([logging.FileHandler(log_file)] if log_file else [])
        ]
    )
    return logging.getLogger(__name__)


def kill_driver_processes():
    """Kill existing driver processes"""
    commands = [
        """ps -ef | grep selenium | grep -v grep | awk '{print "kill -9" $2}'| sh""",
        """ps -ef | grep chromium | grep -v grep | awk '{print "kill -9" $2}'| sh""",
        """ps -ef | grep chromedriver | grep -v grep | awk '{print "kill -9" $2}'| sh"""
    ]
    
    for cmd in commands:
        os.system(cmd)


def generate_city_pairs(cities: List[str]) -> List[Tuple[str, str]]:
    """Generate all possible city pairs from the given cities list"""
    city_pairs = []
    reversed_cities = list(reversed(cities))
    
    for origin in cities:
        for destination in reversed_cities:
            if origin != destination:
                city_pairs.append((origin, destination))
    
    return city_pairs


def generate_flight_dates(
    num_days: int, 
    begin_date: str = None, 
    end_date: str = None, 
    start_interval: int = 1, 
    days_interval: int = 1
) -> List[str]:
    """Generate list of flight dates based on configuration"""
    flight_dates = []
    
    # Determine start date
    if begin_date:
        start_date = dt.strptime(begin_date, "%Y-%m-%d")
    elif start_interval:
        start_date = dt.now() + timedelta(days=start_interval)
    else:
        start_date = dt.now()
    
    # Generate dates
    for i in range(0, num_days, days_interval):
        flight_date = start_date + timedelta(days=i)
        flight_dates.append(flight_date.strftime("%Y-%m-%d"))
    
    # Apply end date filter if specified
    if end_date:
        end_date_obj = dt.strptime(end_date, "%Y-%m-%d")
        flight_dates = [
            date for date in flight_dates 
            if dt.strptime(date, "%Y-%m-%d") <= end_date_obj
        ]
        
        # Continue generating dates until reaching end date
        while dt.strptime(flight_dates[-1], "%Y-%m-%d") < end_date_obj:
            next_date = dt.strptime(flight_dates[-1], "%Y-%m-%d") + timedelta(days=days_interval)
            if next_date <= end_date_obj:
                flight_dates.append(next_date.strftime("%Y-%m-%d"))
            else:
                break
    
    return flight_dates


def element_to_be_clickable(element):
    """Custom expected condition for element clickability"""
    def check_clickable(driver):
        try:
            if element.is_enabled() and element.is_displayed():
                return element
            else:
                return False
        except:
            return False
    return check_clickable


def wait_for_element_clickable(driver, locator, timeout: int = 10):
    """Wait for element to be clickable"""
    return WebDriverWait(driver, timeout).until(
        element_to_be_clickable(driver.find_element(*locator))
    )


def wait_for_element_present(driver, locator, timeout: int = 10):
    """Wait for element to be present"""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(locator)
    )


def safe_click_element(driver, locator, timeout: int = 10):
    """Safely click an element with error handling"""
    try:
        element = wait_for_element_clickable(driver, locator, timeout)
        element.click()
        return True
    except Exception as e:
        logging.error(f"Failed to click element {locator}: {e}")
        return False


def safe_send_keys(driver, locator, text: str, timeout: int = 10):
    """Safely send keys to an element with error handling"""
    try:
        element = wait_for_element_clickable(driver, locator, timeout)
        element.clear()
        element.send_keys(text)
        return True
    except Exception as e:
        logging.error(f"Failed to send keys to element {locator}: {e}")
        return False


def get_current_timestamp() -> str:
    """Get current timestamp in formatted string"""
    return time.strftime("%Y-%m-%d_%H-%M-%S")


def create_directory_if_not_exists(directory_path: str):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logging.info(f"Created directory: {directory_path}")


def check_file_exists(file_path: str) -> bool:
    """Check if file exists"""
    return os.path.exists(file_path)


def format_error_message(error: Exception, context: str = "") -> str:
    """Format error message with context"""
    error_type = type(error).__name__
    error_msg = str(error).split("Stacktrace:")[0] if "Stacktrace:" in str(error) else str(error)
    
    if context:
        return f"{context}: {error_type} - {error_msg}"
    else:
        return f"{error_type} - {error_msg}"


def retry_on_exception(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying functions on exception"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


class Selectors:
    """CSS selectors and locators used in the application"""
    
    # Login related selectors
    LOGIN_MODAL = (By.CLASS_NAME, "lg_loginbox_modal")
    LOGIN_WRAPPER = (By.CLASS_NAME, "tl_nfes_home_header_login_wrapper_siwkn")
    LOGIN_WRAP = (By.CLASS_NAME, "lg_loginwrap")
    USERNAME_INPUT = (By.CLASS_NAME, "r_input.bbz-js-iconable-input")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "div[data-testid='accountPanel'] input[data-testid='passwordInput']")
    AGREEMENT_CHECKBOX = (By.CSS_SELECTOR, '[for="checkboxAgreementInput"]')
    LOGIN_BUTTON = (By.CLASS_NAME, "form_btn.form_btn--block")
    
    # Verification code selectors
    VERIFICATION_CODE = (By.ID, "verification-code")
    ALERT_TITLE = (By.CLASS_NAME, "alert-title")
    DOUBLE_AUTH_SWITCHER = (By.CSS_SELECTOR, "[data-testid='doubleAuthSwitcherBox']")
    SEND_CODE_BUTTON = (By.CSS_SELECTOR, "[data-testid='doubleAuthSwitcherBox'] dl[data-testid='dynamicCodeInput'] a.btn-primary-s")
    CODE_INPUT = (By.CSS_SELECTOR, "[data-testid='doubleAuthSwitcherBox'] input[data-testid='verifyCodeInput']")
    VERIFY_BUTTON = (By.CSS_SELECTOR, "[data-testid='doubleAuthSwitcherBox'] dl[data-testid='dynamicVerifyButton'] input[type='submit']")
    
    # Flight search selectors
    HOME_PLANE_ICON = (By.CLASS_NAME, "pc_home-jipiao")
    ONE_WAY_RADIO = (By.CLASS_NAME, "radio-label")
    SEARCH_BUTTON = (By.CLASS_NAME, "search-btn")
    FORM_INPUT = (By.CLASS_NAME, "form-input-v3")
    DATE_SELECTOR = (By.CLASS_NAME, "modifyDate.depart-date")
    DATE_PICKER = (By.CLASS_NAME, "date-picker.date-picker-block")
    DATE_DAY = (By.CLASS_NAME, "date-d")
    LOW_PRICE_REMIND = (By.CLASS_NAME, "low-price-remind")
    
    # Navigation selectors
    NEXT_MONTH = (By.CLASS_NAME, "in-date-picker.icon.next-ico.iconf-right")
    PREV_MONTH = (By.CLASS_NAME, "in-date-picker.icon.prev-ico.iconf-left")
    
    # Notice and popup selectors
    NOTICE_BOX = (By.CLASS_NAME, "notice-box")
    SHORTCUT = (By.CLASS_NAME, "shortcut")
    SHORTCUT_LINK = (By.CLASS_NAME, "shortcut-link")
    SHARELINE = (By.CLASS_NAME, "shareline")

