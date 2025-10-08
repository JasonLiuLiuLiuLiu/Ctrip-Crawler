"""
Data processing module for Ctrip Flight Scraper
Handles flight data extraction, processing, and storage
"""

import json
import gzip
import io
import logging
import os
import magic
import pandas as pd
from datetime import datetime as dt
from typing import Dict, List, Optional, Any

from config import config
from utils import get_current_timestamp, create_directory_if_not_exists


class DataProcessor:
    """Handles flight data processing and storage"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.flight_data = None
        self.price_data = None
        self.comfort_data = None
    
    def process_flight_data(self, raw_data: Dict[str, Any]) -> bool:
        """Process raw flight data from API response"""
        try:
            self.logger.info("Processing flight data...")
            
            # Extract flight itineraries
            flight_itineraries = raw_data.get("data", {}).get("flightItineraryList", [])
            
            if not flight_itineraries:
                self.logger.warning("No flight itineraries found in response")
                return False
            
            # Filter direct flights if required
            if config.scraping.direct_flight_only:
                flight_itineraries = self._filter_direct_flights(flight_itineraries)
            
            if not flight_itineraries:
                self.logger.warning("No direct flights found after filtering")
                return False
            
            # Process flight segments
            self.flight_data = self._process_flight_segments(flight_itineraries)
            
            # Process price data
            self.price_data = self._process_price_data(flight_itineraries)
            
            self.logger.info(f"Processed {len(flight_itineraries)} flight itineraries")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process flight data: {e}")
            return False
    
    def _filter_direct_flights(self, flight_itineraries: List[Dict]) -> List[Dict]:
        """Filter to keep only direct flights"""
        direct_flights = []
        for itinerary in flight_itineraries:
            flight_segments = itinerary.get("flightSegments", [])
            if flight_segments and flight_segments[0].get("transferCount", 0) == 0:
                direct_flights.append(itinerary)
        
        self.logger.info(f"Filtered to {len(direct_flights)} direct flights from {len(flight_itineraries)} total")
        return direct_flights
    
    def _process_flight_segments(self, flight_itineraries: List[Dict]) -> pd.DataFrame:
        """Process flight segment data into DataFrame"""
        flights_df = pd.DataFrame()
        
        for itinerary in flight_itineraries:
            flight_segments = itinerary.get("flightSegments", [])
            if not flight_segments:
                continue
            
            flight_list = flight_segments[0].get("flightList", [])
            if not flight_list:
                continue
            
            flight_unit = flight_list[0]  # Get first flight in the segment
            
            # Process flight data
            processed_flight = self._process_single_flight(flight_unit)
            
            # Add to DataFrame
            flights_df = pd.concat([
                flights_df,
                pd.DataFrame([processed_flight])
            ], ignore_index=True)
        
        self.logger.info(f"Processed {len(flights_df)} flight segments")
        return flights_df
    
    def _process_single_flight(self, flight_unit: Dict) -> Dict:
        """Process a single flight unit"""
        # Parse departure and arrival times
        departure_datetime = flight_unit.get("departureDateTime", "").split(" ")
        arrival_datetime = flight_unit.get("arrivalDateTime", "").split(" ")
        
        processed_flight = {
            "departureday": departure_datetime[0] if len(departure_datetime) > 0 else "",
            "departuretime": departure_datetime[1] if len(departure_datetime) > 1 else "",
            "arrivalday": arrival_datetime[0] if len(arrival_datetime) > 0 else "",
            "arrivaltime": arrival_datetime[1] if len(arrival_datetime) > 1 else "",
        }
        
        # Process stop information
        stop_info = self._process_stop_info(flight_unit.get("stopList", []))
        processed_flight["stopInfo"] = stop_info
        
        # Add all other flight data
        for key, value in flight_unit.items():
            if key not in ["departureDateTime", "arrivalDateTime", "stopList"]:
                processed_flight[key] = value
        
        # Remove unimportant information if configured
        if config.scraping.delete_unimportant_info:
            processed_flight = self._remove_unimportant_fields(processed_flight)
        
        return processed_flight
    
    def _process_stop_info(self, stop_list: List[Dict]) -> str:
        """Process stop information into readable format"""
        if not stop_list:
            return "无中转"
        
        stop_info_parts = []
        for stop in stop_list:
            city_name = stop.get("cityName", "")
            airport_name = stop.get("airportName", "")
            duration = stop.get("duration", "")
            stop_info_parts.append(f"{city_name}({airport_name}, {duration}分钟)")
        
        return " -> ".join(stop_info_parts)
    
    def _remove_unimportant_fields(self, flight_data: Dict) -> Dict:
        """Remove unimportant fields from flight data"""
        unimportant_fields = [
            "sequenceNo", "marketAirlineCode", "departureProvinceId",
            "departureCityId", "departureCityCode", "departureAirportShortName",
            "departureTerminal", "arrivalProvinceId", "arrivalCityId",
            "arrivalCityCode", "arrivalAirportShortName", "arrivalTerminal",
            "transferDuration", "stopList", "leakedVisaTagSwitch",
            "trafficType", "highLightPlaneNo", "mealType",
            "operateAirlineCode", "operateFlightNo", "operateAirlineName"
        ]
        
        for field in unimportant_fields:
            flight_data.pop(field, None)
        
        return flight_data
    
    def _process_price_data(self, flight_itineraries: List[Dict]) -> pd.DataFrame:
        """Process price data into DataFrame"""
        prices_df = pd.DataFrame()
        
        for itinerary in flight_itineraries:
            itinerary_id = itinerary.get("itineraryId", "")
            flight_no = itinerary_id.split("_")[0] if "_" in itinerary_id else ""
            
            price_list = itinerary.get("priceList", [])
            if not price_list:
                continue
            
            # Process prices for different cabin classes
            price_info = self._process_price_list(price_list)
            price_info["flightNo"] = flight_no
            
            # Add to DataFrame
            prices_df = pd.concat([
                prices_df,
                pd.DataFrame([price_info])
            ], ignore_index=True)
        
        self.logger.info(f"Processed {len(prices_df)} price records")
        return prices_df
    
    def _process_price_list(self, price_list: List[Dict]) -> Dict:
        """Process a list of prices for different cabin classes"""
        economy_prices = []
        business_prices = []
        
        for price in price_list:
            cabin = price.get("cabin", "")
            adult_price = price.get("adultPrice", 0)
            adult_tax = price.get("adultTax", 0)
            misery_index = price.get("miseryIndex", 0)
            total_price = adult_price + adult_tax
            
            if cabin == "Y":  # Economy class
                economy_prices.append({
                    "price": adult_price,
                    "tax": adult_tax,
                    "total": total_price,
                    "full_price": misery_index
                })
            elif cabin == "C":  # Business class
                business_prices.append({
                    "price": adult_price,
                    "tax": adult_tax,
                    "total": total_price,
                    "full_price": misery_index
                })
        
        # Find minimum prices
        economy_info = self._find_minimum_price(economy_prices, "economy")
        business_info = self._find_minimum_price(business_prices, "business")
        
        return {**economy_info, **business_info}
    
    def _find_minimum_price(self, prices: List[Dict], prefix: str) -> Dict:
        """Find minimum price from a list of prices"""
        if not prices:
            return {
                f"{prefix}_origin": "",
                f"{prefix}_tax": "",
                f"{prefix}_total": "",
                f"{prefix}_full": ""
            }
        
        min_price = min(prices, key=lambda x: x["total"])
        return {
            f"{prefix}_origin": min_price["price"],
            f"{prefix}_tax": min_price["tax"],
            f"{prefix}_total": min_price["total"],
            f"{prefix}_full": min_price["full_price"]
        }
    
    def merge_data(self) -> pd.DataFrame:
        """Merge flight data and price data"""
        try:
            if self.flight_data is None or self.price_data is None:
                self.logger.error("Flight data or price data is missing")
                return pd.DataFrame()
            
            # Merge on flight number
            merged_df = self.flight_data.merge(self.price_data, on="flightNo", how="inner")
            
            # Add data collection timestamp
            merged_df["dateGetTime"] = dt.now().strftime("%Y-%m-%d")
            
            # Add comfort data if available
            if self.comfort_data:
                merged_df = self._merge_comfort_data(merged_df)
            
            # Rename columns if configured
            if config.scraping.rename_columns:
                merged_df = self._rename_columns(merged_df)
            
            self.logger.info(f"Merged data shape: {merged_df.shape}")
            return merged_df
            
        except Exception as e:
            self.logger.error(f"Failed to merge data: {e}")
            return pd.DataFrame()
    
    def _merge_comfort_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Merge comfort data with flight data"""
        try:
            if not self.comfort_data:
                return df
            
            comfort_df = pd.DataFrame.from_dict(self.comfort_data, orient='index')
            comfort_df.reset_index(inplace=True)
            comfort_df.rename(columns={'index': 'flight_no'}, inplace=True)
            
            # Create matching column for merge
            if 'operateFlightNo' in df.columns:
                df['match_flight_no'] = df['operateFlightNo'].fillna(df['flightNo'])
            else:
                df['match_flight_no'] = df['flightNo']
            
            # Merge comfort data
            df = df.merge(comfort_df, left_on='match_flight_no', right_on='flight_no', how='left')
            
            # Clean up temporary columns
            df.drop(['match_flight_no', 'flight_no'], axis=1, inplace=True, errors='ignore')
            
            self.logger.info("Comfort data merged successfully")
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to merge comfort data: {e}")
            return df
    
    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename DataFrame columns to Chinese"""
        column_mapping = {
            "dateGetTime": "数据获取日期",
            "flightNo": "航班号",
            "marketAirlineName": "航空公司",
            "departureday": "出发日期",
            "departuretime": "出发时间",
            "arrivalday": "到达日期",
            "arrivaltime": "到达时间",
            "duration": "飞行时长",
            "departureCountryName": "出发国家",
            "departureCityName": "出发城市",
            "departureAirportName": "出发机场",
            "departureAirportCode": "出发机场三字码",
            "arrivalCountryName": "到达国家",
            "arrivalCityName": "到达城市",
            "arrivalAirportName": "到达机场",
            "arrivalAirportCode": "到达机场三字码",
            "aircraftName": "飞机型号",
            "aircraftSize": "飞机尺寸",
            "aircraftCode": "飞机型号三字码",
            "arrivalPunctuality": "到达准点率",
            "stopCount": "停留次数",
            "stopInfo": "中转信息"
        }
        
        # Add comfort data column mapping
        comfort_columns = {
            'departure_delay_time': '出发延误时间',
            'departure_bridge_rate': '出发廊桥率',
            'arrival_delay_time': '到达延误时间',
            'plane_type': '飞机类型',
            'plane_width': '飞机宽度',
            'plane_age': '飞机机龄',
            'Y_has_meal': '经济舱是否有餐食',
            'Y_seat_tilt': '经济舱座椅倾斜度',
            'Y_seat_width': '经济舱座椅宽度',
            'Y_seat_pitch': '经济舱座椅间距',
            'Y_meal_msg': '经济舱餐食信息',
            'Y_power': '经济舱电源',
            'C_has_meal': '商务舱是否有餐食',
            'C_seat_tilt': '商务舱座椅倾斜度',
            'C_seat_width': '商务舱座椅宽度',
            'C_seat_pitch': '商务舱座椅间距',
            'C_meal_msg': '商务舱餐食信息',
            'C_power': '商务舱电源',
        }
        
        column_mapping.update(comfort_columns)
        df = df.rename(columns=column_mapping)
        
        return df
    
    def save_data(self, df: pd.DataFrame, flight_date: str, origin_city: str, destination_city: str) -> bool:
        """Save processed data to CSV file"""
        try:
            # Create directory structure
            files_dir = os.path.join(
                os.getcwd(), 
                flight_date, 
                dt.now().strftime("%Y-%m-%d")
            )
            create_directory_if_not_exists(files_dir)
            
            # Create filename
            filename = os.path.join(files_dir, f"{origin_city}-{destination_city}.csv")
            
            # Save to CSV
            df.to_csv(filename, encoding="UTF-8", index=False)
            
            self.logger.info(f"Data saved successfully: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            return False
    
    def decode_response_data(self, response_body: bytes) -> Dict[str, Any]:
        """Decode response data from bytes to dictionary"""
        try:
            # Check MIME type
            mime = magic.Magic()
            file_type = mime.from_buffer(response_body)
            
            buf = io.BytesIO(response_body)
            
            if "gzip" in file_type:
                # Decompress gzipped data
                gf = gzip.GzipFile(fileobj=buf)
                decoded_data = gf.read().decode("UTF-8")
            elif "JSON data" in file_type:
                # Direct JSON data
                decoded_data = buf.read().decode("UTF-8")
            else:
                self.logger.error(f"Unknown compression format: {file_type}")
                return {}
            
            # Parse JSON
            return json.loads(decoded_data)
            
        except Exception as e:
            self.logger.error(f"Failed to decode response data: {e}")
            return {}
    
    def set_comfort_data(self, comfort_data: Dict[str, Any]):
        """Set comfort data for merging"""
        self.comfort_data = comfort_data

