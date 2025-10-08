"""
Page handling module for Ctrip Flight Scraper
Handles page navigation, element interaction, and form filling
"""

import logging
import time
from typing import Tuple, Optional
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


class PageHandler:
    """Handles page navigation and interaction"""
    
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        self.error_count = 0
    
    def navigate_to_homepage(self) -> bool:
        """Navigate to the flight search homepage"""
        try:
            self.logger.info("Navigating to homepage...")
            start_time = time.time()
            
            self.driver.get("https://flights.ctrip.com/online/channel/domestic")
            
            end_time = time.time()
            self.logger.info(f"Navigation completed in {end_time - start_time:.2f} seconds")
            
            return self._wait_for_page_load()
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to homepage: {format_error_message(e)}")
            return False
    
    def _wait_for_page_load(self) -> bool:
        """Wait for the page to load completely"""
        try:
            self.logger.info("Waiting for page to load...")
            
            # Wait for the main flight search element
            wait_for_element_present(self.driver, Selectors.HOME_PLANE_ICON, config.scraping.max_wait_time)
            
            self.logger.info("Page loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Page load timeout: {format_error_message(e)}")
            return False
    
    def setup_flight_search(self) -> bool:
        """Setup the flight search form"""
        try:
            self.logger.info("Setting up flight search...")
            
            # Click on plane icon to return to main interface
            safe_click_element(self.driver, Selectors.HOME_PLANE_ICON)
            self.logger.info("Clicked plane icon")
            
            # Select one-way flight
            safe_click_element(self.driver, Selectors.ONE_WAY_RADIO)
            self.logger.info("Selected one-way flight")
            
            # Click search button
            safe_click_element(self.driver, Selectors.SEARCH_BUTTON)
            self.logger.info("Clicked search button")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup flight search: {format_error_message(e)}")
            return False
    
    def fill_city_form(self, origin_city: str, destination_city: str) -> bool:
        """Fill the city selection form"""
        try:
            self.logger.info(f"Filling city form: {origin_city} -> {destination_city}")
            
            # Wait for form to be ready
            wait_for_element_present(self.driver, Selectors.FORM_INPUT, config.scraping.max_wait_time)
            
            # Fill origin city
            if not self._fill_city_field(0, origin_city):
                return False
            
            # Fill destination city
            if not self._fill_city_field(1, destination_city):
                return False
            
            self.logger.info("City form filled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to fill city form: {format_error_message(e)}")
            return False
    
    def _fill_city_field(self, field_index: int, city_name: str) -> bool:
        """Fill a specific city field"""
        try:
            form_inputs = self.driver.find_elements(*Selectors.FORM_INPUT)
            if len(form_inputs) <= field_index:
                self.logger.error(f"City field {field_index} not found")
                return False
            
            current_field = form_inputs[field_index]
            
            # Check if city is already correct
            current_value = current_field.get_attribute("value")
            if city_name in current_value:
                self.logger.info(f"City field {field_index} already has correct value: {current_value}")
                return True
            
            # Clear and fill the field
            current_field.click()
            current_field.send_keys(Keys.CONTROL + "a")
            current_field.send_keys(city_name)
            
            # Wait for city to be selected (indicated by parentheses in the value)
            max_attempts = 10
            for attempt in range(max_attempts):
                time.sleep(0.5)
                current_value = current_field.get_attribute("value")
                if "(" in current_value:
                    self.logger.info(f"City field {field_index} filled successfully: {current_value}")
                    return True
            
            self.logger.warning(f"City field {field_index} may not have been filled correctly")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to fill city field {field_index}: {format_error_message(e)}")
            return False
    
    def select_date(self, target_date: str) -> bool:
        """Select the departure date"""
        try:
            self.logger.info(f"Selecting date: {target_date}")
            
            # Parse target date
            year, month, day = self._parse_date(target_date)
            
            # Click on date selector
            safe_click_element(self.driver, Selectors.DATE_SELECTOR)
            
            # Navigate to correct year and month
            if not self._navigate_to_date(year, month):
                return False
            
            # Select the day
            if not self._select_day(day):
                return False
            
            self.logger.info("Date selected successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to select date: {format_error_message(e)}")
            return False
    
    def _parse_date(self, date_str: str) -> Tuple[int, int, int]:
        """Parse date string into year, month, day"""
        parts = date_str.split('-')
        return int(parts[0]), int(parts[1]), int(parts[2])
    
    def _navigate_to_date(self, target_year: int, target_month: int) -> bool:
        """Navigate to the target year and month"""
        try:
            date_pickers = self.driver.find_elements(*Selectors.DATE_PICKER)
            if len(date_pickers) < 2:
                self.logger.error("Date picker not found")
                return False
            
            # Use the second date picker (departure date)
            date_picker = date_pickers[1]
            
            # Navigate to correct year
            while True:
                current_year = int(date_picker.find_element(By.CLASS_NAME, "year").text[:-1])
                if current_year == target_year:
                    break
                elif current_year < target_year:
                    safe_click_element(self.driver, Selectors.NEXT_MONTH)
                else:
                    safe_click_element(self.driver, Selectors.PREV_MONTH)
                time.sleep(0.5)
            
            # Navigate to correct month
            while True:
                current_month = int(date_picker.find_element(By.CLASS_NAME, "month").text[:-1])
                if current_month == target_month:
                    break
                elif current_month < target_month:
                    safe_click_element(self.driver, Selectors.NEXT_MONTH)
                else:
                    safe_click_element(self.driver, Selectors.PREV_MONTH)
                time.sleep(0.5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to date: {format_error_message(e)}")
            return False
    
    def _select_day(self, target_day: int) -> bool:
        """Select the target day"""
        try:
            date_pickers = self.driver.find_elements(*Selectors.DATE_PICKER)
            for date_picker in date_pickers:
                day_elements = date_picker.find_elements(*Selectors.DATE_DAY)
                for day_element in day_elements:
                    if int(day_element.text) == target_day:
                        safe_click_element(self.driver, (By.XPATH, f"//span[text()='{target_day}']"))
                        return True
            
            self.logger.error(f"Day {target_day} not found in date picker")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to select day: {format_error_message(e)}")
            return False
    
    def remove_popups(self):
        """Remove various popups and notices"""
        try:
            # Remove notice boxes
            self.driver.execute_script(
                "document.querySelectorAll('.notice-box').forEach(element => element.remove());"
            )
            
            # Remove online customer service
            self.driver.execute_script(
                "document.querySelectorAll('.shortcut, .shortcut-link').forEach(element => element.remove());"
            )
            
            # Remove share links
            self.driver.execute_script(
                "document.querySelectorAll('.shareline').forEach(element => element.remove());"
            )
            
            self.logger.info("Popups removed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to remove popups: {format_error_message(e)}")
    
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
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        return self.driver.current_url
    
    def get_page_title(self) -> str:
        """Get current page title"""
        return self.driver.title

