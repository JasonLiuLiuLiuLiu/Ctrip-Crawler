"""
Main flight scraper class for Ctrip Flight Scraper
Refactored version with improved structure and error handling
"""

import logging
import time
from typing import Tuple, Optional, Dict, Any

from config import config
from utils import get_current_timestamp, format_error_message, retry_on_exception
from webdriver_manager import WebDriverManager
from login_manager import LoginManager
from page_handler import PageHandler
from data_processor import DataProcessor


class FlightScraper:
    """Main flight scraper class with improved structure"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver_manager = WebDriverManager()
        self.login_manager = None
        self.page_handler = None
        self.data_processor = DataProcessor()
        self.error_count = 0
        self.current_city_pair = None
        self.current_date = None
    
    def initialize(self) -> bool:
        """Initialize the scraper components"""
        try:
            self.logger.info("Initializing flight scraper...")
            
            # Create WebDriver
            self.driver_manager.create_driver()
            
            # Initialize managers
            self.login_manager = LoginManager(self.driver_manager.driver)
            self.page_handler = PageHandler(self.driver_manager.driver)
            
            self.logger.info("Flight scraper initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize scraper: {format_error_message(e)}")
            return False
    
    def scrape_flight_data(self, origin_city: str, destination_city: str, flight_date: str) -> bool:
        """Scrape flight data for a specific route and date"""
        try:
            self.current_city_pair = (origin_city, destination_city)
            self.current_date = flight_date
            
            self.logger.info(f"Starting to scrape: {origin_city} -> {destination_city} on {flight_date}")
            
            # Check if data already exists
            if self._data_already_exists(origin_city, destination_city, flight_date):
                self.logger.info("Data already exists, skipping...")
                return True
            
            # Navigate to homepage if needed
            if not self._ensure_homepage():
                return False
            
            # Perform login if needed
            if not self._ensure_logged_in():
                return False
            
            # Setup flight search
            if not self._setup_flight_search():
                return False
            
            # Fill search form
            if not self._fill_search_form(origin_city, destination_city, flight_date):
                return False
            
            # Get flight data
            if not self._get_flight_data():
                return False
            
            # Process and save data
            if not self._process_and_save_data():
                return False
            
            self.logger.info(f"Successfully scraped data for {origin_city} -> {destination_city}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to scrape flight data: {format_error_message(e)}")
            return False
    
    def _data_already_exists(self, origin_city: str, destination_city: str, flight_date: str) -> bool:
        """Check if data already exists for the given parameters"""
        import os
        filename = os.path.join(
            os.getcwd(), 
            flight_date, 
            time.strftime("%Y-%m-%d"), 
            f"{origin_city}-{destination_city}.csv"
        )
        return os.path.exists(filename)
    
    def _ensure_homepage(self) -> bool:
        """Ensure we're on the homepage"""
        try:
            current_url = self.driver_manager.get_current_url()
            
            if current_url == "data:," or "flights.ctrip.com" not in current_url:
                self.logger.info("Navigating to homepage...")
                return self.page_handler.navigate_to_homepage()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to ensure homepage: {format_error_message(e)}")
            return False
    
    def _ensure_logged_in(self) -> bool:
        """Ensure user is logged in"""
        try:
            # Check if login is required
            if not config.login.allowed:
                return True
            
            # Check if already logged in
            if self._is_logged_in():
                return True
            
            # Perform login
            return self.login_manager.login()
            
        except Exception as e:
            self.logger.error(f"Failed to ensure login: {format_error_message(e)}")
            return False
    
    def _is_logged_in(self) -> bool:
        """Check if user is currently logged in"""
        try:
            # Check for login modal
            if self.page_handler.check_verification_required():
                return False
            
            # Try to access user info page
            self.driver_manager.navigate_to('https://my.ctrip.com/myinfo/home')
            time.sleep(2)
            
            current_url = self.driver_manager.get_current_url()
            return current_url == 'https://my.ctrip.com/myinfo/home'
            
        except:
            return False
    
    def _setup_flight_search(self) -> bool:
        """Setup the flight search interface"""
        try:
            return self.page_handler.setup_flight_search()
        except Exception as e:
            self.logger.error(f"Failed to setup flight search: {format_error_message(e)}")
            return False
    
    def _fill_search_form(self, origin_city: str, destination_city: str, flight_date: str) -> bool:
        """Fill the flight search form"""
        try:
            # Fill city form
            if not self.page_handler.fill_city_form(origin_city, destination_city):
                return False
            
            # Select date
            if not self.page_handler.select_date(flight_date):
                return False
            
            # Remove popups
            self.page_handler.remove_popups()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to fill search form: {format_error_message(e)}")
            return False
    
    @retry_on_exception(max_retries=3, delay=2.0)
    def _get_flight_data(self) -> bool:
        """Get flight data from the API"""
        try:
            self.logger.info("Waiting for flight data...")
            
            # Wait for the API request
            request = self.driver_manager.wait_for_request(
                "/international/search/api/search/batchSearch?.*",
                timeout=config.scraping.max_wait_time
            )
            
            # Get comfort data if enabled
            if config.scraping.include_comfort_data:
                comfort_data = self._get_comfort_data()
                self.data_processor.set_comfort_data(comfort_data)
            
            # Decode response data
            raw_data = self.data_processor.decode_response_data(request.body)
            
            if not raw_data:
                self.logger.error("Failed to decode response data")
                return False
            
            # Process flight data
            if not self.data_processor.process_flight_data(raw_data):
                self.logger.error("Failed to process flight data")
                return False
            
            # Clear request history
            self.driver_manager.clear_requests()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to get flight data: {format_error_message(e)}")
            return False
    
    def _get_comfort_data(self) -> Optional[Dict[str, Any]]:
        """Get flight comfort data"""
        try:
            self.logger.info("Getting comfort data...")
            
            # Scroll to load all content
            self._scroll_to_load_content()
            
            # Analyze requests for comfort data
            comfort_data = {}
            requests = self.driver_manager.driver.requests
            
            for request in requests:
                if "/search/api/flight/comfort/getFlightComfort" in request.url:
                    comfort_data.update(self._process_comfort_request(request))
            
            self.logger.info(f"Retrieved comfort data for {len(comfort_data)} flights")
            return comfort_data
            
        except Exception as e:
            self.logger.error(f"Failed to get comfort data: {format_error_message(e)}")
            return None
    
    def _scroll_to_load_content(self):
        """Scroll page to load all content"""
        try:
            last_height = self.driver_manager.execute_javascript("return document.body.scrollHeight")
            
            while True:
                # Scroll in steps
                for i in range(10):
                    scroll_height = last_height * (i + 1) / 3
                    self.driver_manager.execute_javascript(f"window.scrollTo(0, {scroll_height});")
                    time.sleep(0.5)
                
                time.sleep(3)
                
                new_height = self.driver_manager.execute_javascript("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            self.logger.error(f"Failed to scroll page: {format_error_message(e)}")
    
    def _process_comfort_request(self, request) -> Dict[str, Any]:
        """Process a single comfort request"""
        try:
            import json
            import gzip
            
            if not request.response:
                return {}
            
            body = request.response.body
            if request.response.headers.get('Content-Encoding', '').lower() == 'gzip':
                body = gzip.decompress(body)
            
            json_data = json.loads(body.decode('utf-8'))
            
            if json_data.get('status') != 0:
                return {}
            
            flight_comfort = json_data.get('data', {})
            flight_no = json_data.get('flightNo', 'Unknown')
            
            # Extract comfort information
            comfort_info = {
                'departure_delay_time': flight_comfort.get('punctualityInfo', {}).get('departureDelaytime'),
                'departure_bridge_rate': flight_comfort.get('punctualityInfo', {}).get('departureBridge'),
                'arrival_delay_time': flight_comfort.get('punctualityInfo', {}).get('arrivalDelaytime'),
                'plane_type': flight_comfort.get('planeInfo', {}).get('planeTypeName'),
                'plane_width': flight_comfort.get('planeInfo', {}).get('planeWidthCategory'),
                'plane_age': flight_comfort.get('planeInfo', {}).get('planeAge')
            }
            
            # Process cabin information
            cabin_info = {cabin['cabin']: cabin for cabin in flight_comfort.get('cabinInfoList', [])}
            
            for cabin_type in ['Y', 'C']:
                if cabin_type in cabin_info:
                    cabin = cabin_info[cabin_type]
                    comfort_info.update({
                        f'{cabin_type}_has_meal': cabin.get('hasMeal'),
                        f'{cabin_type}_seat_tilt': cabin.get('seatTilt', {}).get('value'),
                        f'{cabin_type}_seat_width': cabin.get('seatWidth', {}).get('value'),
                        f'{cabin_type}_seat_pitch': cabin.get('seatPitch', {}).get('value'),
                        f'{cabin_type}_meal_msg': cabin.get('mealMsg'),
                        f'{cabin_type}_power': cabin.get('power')
                    })
            
            return {flight_no: comfort_info}
            
        except Exception as e:
            self.logger.error(f"Failed to process comfort request: {format_error_message(e)}")
            return {}
    
    def _process_and_save_data(self) -> bool:
        """Process and save the scraped data"""
        try:
            # Merge data
            merged_df = self.data_processor.merge_data()
            
            if merged_df.empty:
                self.logger.error("No data to save")
                return False
            
            # Save data
            origin_city, destination_city = self.current_city_pair
            return self.data_processor.save_data(merged_df, self.current_date, origin_city, destination_city)
            
        except Exception as e:
            self.logger.error(f"Failed to process and save data: {format_error_message(e)}")
            return False
    
    def handle_error(self, error: Exception, context: str = "") -> bool:
        """Handle errors with retry logic"""
        self.error_count += 1
        error_msg = format_error_message(error, context)
        self.logger.error(f"Error {self.error_count}/{config.scraping.max_retry_time}: {error_msg}")
        
        if self.error_count >= config.scraping.max_retry_time:
            self.logger.error("Max retry attempts reached, giving up")
            return False
        
        # Take screenshot for debugging
        self.driver_manager.take_screenshot()
        
        # Refresh page and retry
        try:
            self.driver_manager.refresh_driver()
            time.sleep(config.scraping.crawl_interval)
            return True
        except Exception as e:
            self.logger.error(f"Failed to refresh driver: {format_error_message(e)}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.driver_manager:
                self.driver_manager.quit_driver()
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {format_error_message(e)}")
    
    def __enter__(self):
        """Context manager entry"""
        if not self.initialize():
            raise RuntimeError("Failed to initialize scraper")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()

