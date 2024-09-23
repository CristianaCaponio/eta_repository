from typing import Dict, List
import requests
from model.geopy_input_data import GeopyInputData
from model.db_models import StopSummary, Summary, TravelData
from utils.address_converter_service import AddressConverter
from datetime import datetime, timedelta
from loguru import logger
import os
import urllib.parse as urlparse

class TomTomParams:
    
    @staticmethod
    def request_params(coordinates_travel_data: List[GeopyInputData]) -> str:
        logger.info("sono entrato in request_param di TomTomParams")
        """This method takes all coordinates from travel data (considered parameter -> stops: List[stopSummary] )and returns a query parameter string formatted to build the request URL."""
        location_str = AddressConverter.address_to_coordinates_converter(coordinates_travel_data)        
        
        return (
            location_str
            + "/json?routeType=fastest"    
            + "&travelMode=car"   
            + "&routeRepresentation=polyline" 
            + "&departAt=now" 
            + "&computeBestOrder=true"                       
        ) 
    logger.info("sono uscito da request_param di TomTomParams")
               
    @staticmethod
    def tomtom_request(request_params: str) -> TravelData:
        logger.info("sono entrato in tomtom_request di TomTomParams")
        baseUrl = "https://api.tomtom.com/routing/1/calculateRoute/" 
        API_KEY = os.getenv("TOMTOM_API_KEY")           
        if not API_KEY:
            raise ValueError("TOMTOM_API_KEY environment variable is not set.")
            
        requestUrl = baseUrl + request_params + "&key=" + API_KEY
        logger.info("Request URL: " + requestUrl + "\n")        
    
        response = requests.get(requestUrl)
        logger.info(response)
        response.raise_for_status()

        if response.status_code == 200:
            jsonResult = response.json()
            
            # Get start and end coordinates from TomTom
            tomtom_start_latitude = jsonResult["routes"][0]["legs"][0]["points"][0]["latitude"]
            tomtom_start_longitude = jsonResult["routes"][0]["legs"][0]["points"][0]["longitude"]
            tomtom_end_latitude = jsonResult['routes'][0]['legs'][-1]['points'][-1]["latitude"]
            tomtom_end_longitude = jsonResult['routes'][0]['legs'][-1]['points'][-1]["longitude"]
            
            # Construct the Summary
            route_summary = Summary(
                travelMode = jsonResult["routes"][0]["sections"][0]["travelMode"],  # Corrected
                lengthInMeters = jsonResult["routes"][0]["summary"]["lengthInMeters"],
                travelTimeInSeconds = jsonResult["routes"][0]["summary"]["travelTimeInSeconds"],
                trafficDelayInSeconds = jsonResult["routes"][0]["summary"]["trafficDelayInSeconds"],
                trafficLengthInMeters = jsonResult["routes"][0]["summary"]["trafficLengthInMeters"],
                startAddress = GeopyInputData(address = "address1",city = "city1",district = "disctrict1",house_number = "number1",zip_code = "zip_code1"),
                startLatitude = tomtom_start_latitude,
                startLongitude = tomtom_start_longitude,
                endAddress = GeopyInputData(address = "address1",city = "city1",district = "disctrict1",house_number = "number1",zip_code = "zip_code1"),
                endLatitude = tomtom_end_latitude,
                endLongitude = tomtom_end_longitude,
                departureTime = jsonResult["routes"][0]["summary"]["departureTime"],
                arrivalTime = jsonResult["routes"][0]["summary"]["arrivalTime"]
            )

            # Construct the Stops
            stops = []
            for leg_data in jsonResult["routes"][0]["legs"]:
                tomtom_departure_latitude = leg_data["points"][0]["latitude"]
                tomtom_departure_longitude = leg_data["points"][0]["longitude"]
                tomtom_arrival_latitude = leg_data['points'][-1]["latitude"]
                tomtom_arrival_longitude = leg_data['points'][-1]["longitude"]
                
                stop_summary = StopSummary(
                    gsin = "some_gsin",  # Placeholder, replace with real data
                    lengthInMeters = leg_data["summary"]["lengthInMeters"],
                    travelTimeInSeconds = leg_data["summary"]["travelTimeInSeconds"],
                    trafficDelayInSeconds = leg_data["summary"]["trafficDelayInSeconds"],
                    departureAddress = GeopyInputData(address = "address1",city = "city1",district = "disctrict1",house_number = "number1",zip_code = "zip_code1"),
                    departureLatitude = tomtom_departure_latitude,
                    departureLongitude = tomtom_departure_longitude,
                    arrivalAddress = GeopyInputData(address = "address1",city = "city1",district = "disctrict1",house_number = "number1",zip_code = "zip_code1"),
                    arrivalLatitude = tomtom_arrival_latitude,
                    arrivalLongitude = tomtom_arrival_longitude,
                    trafficLengthInMeters=leg_data["summary"]["trafficLengthInMeters"],
                    departureTime = leg_data["summary"]["departureTime"],
                    arrivalTime = leg_data["summary"]["arrivalTime"],
                    delivered = False  # Placeholder, adjust as needed
                )
                stops.append(stop_summary)
            
            # Populating TravelData
            tomtom_travel_data = TravelData(  
                personal_id="banana",                                          
                summary=route_summary,  # Corrected field name
                stops=stops  # Corrected field name
            )
            
            return tomtom_travel_data

        else:
            raise ValueError(f"Request failed with status code: {response.status_code}")
    logger.info("sono uscito da tomtom_request di TomTomParams")

        
    """the next part is about addig delay from cap and changing the departure/arrival time. This is commented """

        
    # @staticmethod    
    # def add_delay_to_time(time_str: str, delay_in_seconds: int) -> str:
    #     """This method takes an ISO-format time string and a delay in seconds. It converts the time string to a datetime object, 
    #         applies the delay using timedelta, and returns the updated time as an ISO-format string."""
    #     time_format = "%Y-%m-%dT%H:%M:%S%z"
    #     time_obj = datetime.strptime(time_str, time_format)
    #     new_time_obj = time_obj + timedelta(seconds=delay_in_seconds)
    #     return new_time_obj.strftime(time_format)
        
    
    # @staticmethod
    # def calculate_definitive_eta(response: TomTomResponse, zip_code_delays: Dict[str, int]) -> TomTomResponse:
    #     """This method takes a TomTomResponse object and a list of cap delays to update the travelTimeInSeconds variable. 
    #         It adjusts travel times and arrival/departure times based on the accumulated delays.""" 
        
    #     logger.debug("Starting definitive ETA calculation.")

    #     for route in response.routes:
    #         logger.info(f"Processing the route: {route.summary.startAddress} a {route.summary.endAddress}")
    #         total_delay = 0     
    #         previous_zip_code = None        
            
           
            
    #         for leg in route.legs:
    #             # extracting the departure zip_code from the address
    #             zip_code = leg.summary.departureAddress.split(',')[-1].strip()
    #             logger.info(f"departure zip_code: {zip_code}")
                
    #             # checking if the next zip_code is different from the previous one
    #             if zip_code is not None:
    #                 # recovering the zip_code delay
    #                 delay = zip_code_delays.get(zip_code, 0)
    #                 logger.info(f"delay for zip_code {zip_code}: {delay} seconds")
                
    #                 # adding delay to time
    #                 leg.summary.travelTimeInSeconds += delay
    #                 total_delay += delay
                
    #                 # updating the time of arrival
    #                 leg.summary.arrivalTime = TomTomParams.add_delay_to_time(leg.summary.departureTime, leg.summary.travelTimeInSeconds)
                                 
    #             #updating the previous zip-code
    #             previous_zip_code = zip_code  

    #             logger.info(f"Update: time of travel: {leg.summary.travelTimeInSeconds} seconds, "
    #                         f"time of arrival: {leg.summary.arrivalTime}")

    #         # updating the travel time
    #         route.summary.travelTimeInSeconds += total_delay
    #         route.summary.arrivalTime = TomTomParams.add_delay_to_time(route.summary.departureTime, route.summary.travelTimeInSeconds)
            
    #         logger.info(f"Update: Total time travel: {route.summary.travelTimeInSeconds} seconds, "
    #                     f"Arrival time: {route.summary.arrivalTime}")
        
    #     logger.info("Definitive ETA calculatioon completed.")
    #     return response
