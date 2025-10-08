"""
Login management module for Ctrip Flight Scraper
Handles user authentication and session management
"""

import json
import logging
import threading
import time
from typing import List, Optional, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import config
from utils import (
    Selectors, wait_for_element_clickable, wait_for_element_present,
    safe_click_element, safe_send_keys, get_current_timestamp,
    format_error_message
)


class LoginManager:
    """Manages user login and session handling"""
    
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        self.current_account_index = 0
        self.error_count = 0
    
    def login(self) -> bool:
        """Main login method"""
        if not config.login.allowed:
            self.logger.info("Login is disabled in configuration")
            return True
        
        try:
            # Try cookie-based login first
            if self._try_cookie_login():
                return True
            
            # Fall back to manual login
            return self._perform_manual_login()
            
        except Exception as e:
            self.logger.error(f"Login failed: {format_error_message(e)}")
            return False
    
    def _try_cookie_login(self) -> bool:
        """Try to login using saved cookies"""
        account = self._get_current_account()
        cookies = self._load_cookies(account)
        
        if not cookies:
            self.logger.info("No saved cookies found, proceeding with manual login")
            return False
        
        try:
            # Add cookies to driver
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            
            # Test login by navigating to user info page
            self.driver.get('https://my.ctrip.com/myinfo/home')
            
            WebDriverWait(self.driver, config.scraping.max_wait_time).until(
                lambda d: d.current_url == 'https://my.ctrip.com/myinfo/home'
            )
            
            self.logger.info("Successfully logged in using cookies")
            return True
            
        except Exception as e:
            self.logger.warning(f"Cookie login failed: {format_error_message(e)}")
            self._delete_cookies(account)
            return False
    
    def _perform_manual_login(self) -> bool:
        """Perform manual login with username and password"""
        try:
            # Check if login modal is already open
            if not self._is_login_modal_open():
                self._open_login_modal()
            
            # Fill login form
            self._fill_login_form()
            
            # Handle verification code if needed
            if self._handle_verification_code():
                self.logger.info("Login completed successfully")
                self._save_cookies()
                return True
            else:
                self.logger.error("Login failed during verification")
                return False
                
        except Exception as e:
            self.logger.error(f"Manual login failed: {format_error_message(e)}")
            return False
    
    def _is_login_modal_open(self) -> bool:
        """Check if login modal is currently open"""
        try:
            return len(self.driver.find_elements(*Selectors.LOGIN_MODAL)) > 0
        except:
            return False
    
    def _open_login_modal(self):
        """Open the login modal"""
        try:
            # Click on login wrapper to open modal
            wait_for_element_clickable(self.driver, Selectors.LOGIN_WRAPPER, config.scraping.max_wait_time)
            safe_click_element(self.driver, Selectors.LOGIN_WRAPPER)
            
            # Wait for login wrap to appear
            wait_for_element_present(self.driver, Selectors.LOGIN_WRAP, config.scraping.max_wait_time)
            
        except Exception as e:
            self.logger.error(f"Failed to open login modal: {format_error_message(e)}")
            raise
    
    def _fill_login_form(self):
        """Fill the login form with credentials"""
        account, password = self._get_current_credentials()
        
        # Fill username
        safe_send_keys(self.driver, Selectors.USERNAME_INPUT, account)
        self.logger.info("Username entered successfully")
        
        # Fill password
        safe_send_keys(self.driver, Selectors.PASSWORD_INPUT, password)
        self.logger.info("Password entered successfully")
        
        # Check agreement checkbox
        safe_click_element(self.driver, Selectors.AGREEMENT_CHECKBOX)
        self.logger.info("Agreement checkbox checked")
        
        # Click login button
        safe_click_element(self.driver, Selectors.LOGIN_BUTTON)
        self.logger.info("Login button clicked")
    
    def _handle_verification_code(self) -> bool:
        """Handle verification code if required"""
        try:
            # Check if verification code page appears
            WebDriverWait(self.driver, config.scraping.max_wait_time).until(
                EC.presence_of_element_located(Selectors.DOUBLE_AUTH_SWITCHER)
            )
            
            self.logger.info("Verification code page detected")
            
            # Click send code button
            send_btn = WebDriverWait(self.driver, config.scraping.max_wait_time).until(
                EC.element_to_be_clickable(Selectors.SEND_CODE_BUTTON)
            )
            send_btn.click()
            self.logger.info("Send verification code button clicked")
            
            # Get verification code from user
            verification_code = self._get_verification_code_from_user()
            if not verification_code:
                self.logger.error("No verification code provided")
                return False
            
            # Enter verification code
            code_input = WebDriverWait(self.driver, config.scraping.max_wait_time).until(
                EC.element_to_be_clickable(Selectors.CODE_INPUT)
            )
            code_input.send_keys(verification_code)
            self.logger.info("Verification code entered")
            
            # Click verify button
            verify_btn = WebDriverWait(self.driver, config.scraping.max_wait_time).until(
                EC.element_to_be_clickable(Selectors.VERIFY_BUTTON)
            )
            verify_btn.click()
            self.logger.info("Verify button clicked")
            
            # Wait for login completion
            WebDriverWait(self.driver, config.scraping.max_wait_time).until(
                EC.presence_of_element_located(Selectors.HOME_PLANE_ICON)
            )
            
            return True
            
        except Exception as e:
            # If no verification code page appears, assume login was successful
            self.logger.info("No verification code required, login completed")
            return True
    
    def _get_verification_code_from_user(self) -> Optional[str]:
        """Get verification code from user input"""
        verification_code = [None]
        user_input_completed = threading.Event()
        
        def wait_for_verification_input():
            verification_code[0] = input("请输入收到的验证码: ")
            user_input_completed.set()
        
        input_thread = threading.Thread(target=wait_for_verification_input)
        input_thread.start()
        
        timeout_seconds = config.scraping.crawl_interval * 100
        input_thread.join(timeout=timeout_seconds)
        
        if not user_input_completed.is_set():
            self.logger.error(f"Verification code input timeout after {timeout_seconds} seconds")
            return None
        
        return verification_code[0]
    
    def _get_current_account(self) -> str:
        """Get current account based on index"""
        accounts = config.login.accounts
        if not accounts or not accounts[0]:
            return "default"
        return accounts[self.current_account_index % len(accounts)]
    
    def _get_current_credentials(self) -> tuple:
        """Get current account credentials"""
        accounts = config.login.accounts
        passwords = config.login.passwords
        
        if not accounts or not passwords:
            raise ValueError("No accounts or passwords configured")
        
        account = accounts[self.current_account_index % len(accounts)]
        password = passwords[self.current_account_index % len(passwords)]
        
        return account, password
    
    def _save_cookies(self):
        """Save current session cookies"""
        try:
            account = self._get_current_account()
            all_cookies = self.driver.get_cookies()
            filtered_cookies = [
                cookie for cookie in all_cookies 
                if cookie.get("name") in config.login.required_cookies
            ]
            
            self._write_cookies(account, filtered_cookies)
            self.logger.info("Cookies saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save cookies: {format_error_message(e)}")
    
    def _load_cookies(self, account: str) -> List[Dict[str, Any]]:
        """Load saved cookies for an account"""
        try:
            if not self._cookies_file_exists():
                return []
            
            with open(config.login.cookies_file, "r", encoding="utf-8") as f:
                cookies_data = json.load(f)
            
            return cookies_data.get(account, [])
            
        except Exception as e:
            self.logger.error(f"Failed to load cookies: {format_error_message(e)}")
            return []
    
    def _write_cookies(self, account: str, cookies: List[Dict[str, Any]]):
        """Write cookies to file"""
        try:
            cookies_data = {}
            if self._cookies_file_exists():
                with open(config.login.cookies_file, "r", encoding="utf-8") as f:
                    cookies_data = json.load(f)
            
            cookies_data[account] = cookies
            
            with open(config.login.cookies_file, "w", encoding="utf-8") as f:
                json.dump(cookies_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to write cookies: {format_error_message(e)}")
    
    def _delete_cookies(self, account: str):
        """Delete cookies for a specific account"""
        try:
            if not self._cookies_file_exists():
                return
            
            with open(config.login.cookies_file, "r", encoding="utf-8") as f:
                cookies_data = json.load(f)
            
            if account in cookies_data:
                del cookies_data[account]
                
                with open(config.login.cookies_file, "w", encoding="utf-8") as f:
                    json.dump(cookies_data, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"Deleted cookies for account: {account}")
                
        except Exception as e:
            self.logger.error(f"Failed to delete cookies: {format_error_message(e)}")
    
    def _cookies_file_exists(self) -> bool:
        """Check if cookies file exists"""
        import os
        return os.path.exists(config.login.cookies_file)
    
    def switch_account(self):
        """Switch to next account"""
        self.current_account_index += 1
        self.logger.info(f"Switched to account index: {self.current_account_index}")
    
    def check_verification_required(self) -> bool:
        """Check if verification code is required"""
        try:
            verification_elements = (
                self.driver.find_elements(*Selectors.VERIFICATION_CODE) +
                self.driver.find_elements(*Selectors.ALERT_TITLE)
            )
            return len(verification_elements) > 0
        except:
            return False

