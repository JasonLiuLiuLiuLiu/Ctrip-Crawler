"""
Main entry point for Ctrip Flight Scraper
Refactored version with improved structure and error handling
"""

import logging
import threading
import time
from typing import List, Tuple

import gen_proxy_servers
from config import config, load_config_from_file
from utils import setup_logging, kill_driver_processes, generate_city_pairs, generate_flight_dates
from flight_scraper import FlightScraper


class CtripFlightScraperApp:
    """Main application class for the flight scraper"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.proxy_thread = None
        self.scraper = None
    
    def initialize(self) -> bool:
        """Initialize the application"""
        try:
            # Setup logging
            setup_logging(
                log_level=config.debug.log_level,
                log_file=config.debug.log_file
            )
            
            self.logger.info("Initializing Ctrip Flight Scraper...")
            
            # Kill existing driver processes
            kill_driver_processes()
            
            # Start proxy if enabled
            if config.proxy.enabled:
                self._start_proxy()
            
            # Initialize scraper
            self.scraper = FlightScraper()
            if not self.scraper.initialize():
                self.logger.error("Failed to initialize scraper")
                return False
            
            self.logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            return False
    
    def _start_proxy(self):
        """Start the proxy server"""
        try:
            self.logger.info("Starting proxy server...")
            
            self.proxy_thread = threading.Thread(
                target=lambda: gen_proxy_servers.run_proxy(
                    mode=config.proxy.ip_mode,
                    port=1080,
                    bind_address="0.0.0.0",
                    base_interface=config.proxy.base_interface,
                    num_interfaces=config.proxy.ipv6_count,
                    delete_iface=config.proxy.delete_interface
                ),
                daemon=True
            )
            
            self.proxy_thread.start()
            self.logger.info("Proxy server started successfully")
            
            # Wait for proxy to start
            time.sleep(5)
            
        except Exception as e:
            self.logger.error(f"Failed to start proxy server: {e}")
            raise
    
    def run(self):
        """Run the main scraping process"""
        try:
            self.logger.info("Starting flight data scraping...")
            
            # Generate city pairs and flight dates
            city_pairs = generate_city_pairs(config.scraping.crawl_cities)
            flight_dates = generate_flight_dates(
                config.scraping.crawl_days,
                config.scraping.begin_date,
                config.scraping.end_date,
                config.scraping.start_interval,
                config.scraping.days_interval
            )
            
            self.logger.info(f"Generated {len(city_pairs)} city pairs and {len(flight_dates)} flight dates")
            
            # Scrape data for each combination
            total_combinations = len(city_pairs) * len(flight_dates)
            current_combination = 0
            
            for city_pair in city_pairs:
                origin_city, destination_city = city_pair
                
                for flight_date in flight_dates:
                    current_combination += 1
                    
                    self.logger.info(
                        f"Processing combination {current_combination}/{total_combinations}: "
                        f"{origin_city} -> {destination_city} on {flight_date}"
                    )
                    
                    try:
                        # Scrape flight data
                        success = self.scraper.scrape_flight_data(
                            origin_city, destination_city, flight_date
                        )
                        
                        if success:
                            self.logger.info(f"Successfully scraped data for {origin_city} -> {destination_city}")
                        else:
                            self.logger.warning(f"Failed to scrape data for {origin_city} -> {destination_city}")
                        
                        # Switch IP if proxy is enabled
                        if config.proxy.enabled:
                            gen_proxy_servers.switch_proxy_server()
                        
                        # Wait between requests
                        time.sleep(config.scraping.crawl_interval)
                        
                    except Exception as e:
                        self.logger.error(f"Error processing {origin_city} -> {destination_city}: {e}")
                        continue
            
            self.logger.info("Flight data scraping completed")
            
        except Exception as e:
            self.logger.error(f"Error during scraping process: {e}")
            raise
    
    def cleanup(self):
        """Cleanup application resources"""
        try:
            self.logger.info("Cleaning up application resources...")
            
            if self.scraper:
                self.scraper.cleanup()
            
            # Proxy cleanup is handled by the daemon thread
            self.logger.info("Application cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def main():
    """Main entry point"""
    app = None
    
    try:
        # Load configuration from file if it exists
        load_config_from_file("config.json")
        
        # Create and initialize application
        app = CtripFlightScraperApp()
        
        if not app.initialize():
            logging.error("Failed to initialize application")
            return 1
        
        # Run the scraping process
        app.run()
        
        return 0
        
    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
        return 0
        
    except Exception as e:
        logging.error(f"Application error: {e}")
        return 1
        
    finally:
        if app:
            app.cleanup()


if __name__ == "__main__":
    exit(main())

