from typing import Dict
import requests
from model.input_data import InputData
from utils.address_converter_service import AddressConverter
from model.tomtom_output_data import TomTomResponse, RouteSummary, LegSummary, Leg, Route 
from datetime import datetime, timedelta
from loguru import logger
import os
import urllib.parse as urlparse

class TomTomParams:
    
    @staticmethod
    def request_params(input_data: InputData) -> str:
        """This method takes an InputData object and returns a query parameter string formatted to build the request URL."""
        location_str = AddressConverter.address_to_coordinates_converter(input_data.location)    
    
        return (
            location_str
            + "/json?routeType=" + input_data.routeType           
            + "&travelMode=" + input_data.travelMode          
            + "&routeRepresentation=" + str(input_data.routeRepresentation)
            + "&departAt=" + urlparse.quote(input_data.departAt)
            + "&computeBestOrder=" + str(input_data.ordered)
        ) 
             
    
    @staticmethod
    def tomtom_request(request_params: str, input_data: InputData) -> TomTomResponse:
        """This method receives a query parameter string (obtained from the request_params method), appends it to the base URL and adds the API key.
            It constructs the complete URL for making the request to the TomTom API and retrieves information from the service."""
        
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
            # Get response's JSON
            jsonResult = response.json()
            
            # Create a common RouteSummary object
            route_summary = RouteSummary(
                lengthInMeters=jsonResult['routes'][0]['summary'].get('lengthInMeters'),
                travelTimeInSeconds=jsonResult['routes'][0]['summary'].get('travelTimeInSeconds'),
                trafficDelayInSeconds=jsonResult['routes'][0]['summary'].get('trafficDelayInSeconds'),
                trafficLengthInMeters=jsonResult['routes'][0]['summary'].get('trafficLengthInMeters'),
                departureTime=jsonResult['routes'][0]['summary'].get('departureTime'),
                arrivalTime=jsonResult['routes'][0]['summary'].get('arrivalTime')
            )

            # Add start and end addresses if ordered is False
            if input_data.ordered == 'false':
                start_address = input_data.location[0]
                end_address = input_data.location[-1]
                route_summary.startAddress = (
                    f"{start_address.address}, {start_address.house_number}, {start_address.city}, "
                    f"{start_address.district}, {start_address.zip_code}"
                )
                route_summary.endAddress = (
                    f"{end_address.address}, {end_address.house_number}, {end_address.city}, "
                    f"{end_address.district}, {end_address.zip_code}"
                )

            legs = []
            for i, leg_data in enumerate(jsonResult['routes'][0]['legs']):
                leg_summary = LegSummary(
                    lengthInMeters=leg_data['summary'].get('lengthInMeters'),
                    travelTimeInSeconds=leg_data['summary'].get('travelTimeInSeconds'),
                    trafficDelayInSeconds=leg_data['summary'].get('trafficDelayInSeconds'),
                    trafficLengthInMeters=leg_data['summary'].get('trafficLengthInMeters'),
                    departureTime=leg_data['summary'].get('departureTime'),
                    arrivalTime=leg_data['summary'].get('arrivalTime'),
                    originalWaypointIndexAtEndOfLeg=leg_data['summary'].get('originalWaypointIndexAtEndOfLeg', 0)
                )

                # Add departure and arrival addresses if ordered is False
                if input_data.ordered == 'false':
                    departure_address = input_data.location[i]
                    arrival_address = input_data.location[i + 1]
                    leg_summary.departureAddress = (
                        f"{departure_address.address}, {departure_address.house_number}, "
                        f"{departure_address.city}, {departure_address.district}, {departure_address.zip_code}"
                    )
                    leg_summary.arrivalAddress = (
                        f"{arrival_address.address}, {arrival_address.house_number}, "
                        f"{arrival_address.city}, {arrival_address.district}, {arrival_address.zip_code}"
                    )

                legs.append(Leg(summary=leg_summary))

            # Create Route and TomTomResponse objects
            route = Route(summary=route_summary, legs=legs)
            tomtom_response = TomTomResponse(formatVersion="0.0.12", routes=[route])
            
            return tomtom_response
        else:
            raise ValueError(f"Request failed with status code: {response.status_code}")
        
    @staticmethod    
    def add_delay_to_time(time_str: str, delay_in_seconds: int) -> str:
        """This method takes an ISO-format time string and a delay in seconds. It converts the time string to a datetime object, 
            applies the delay using timedelta, and returns the updated time as an ISO-format string."""
        time_format = "%Y-%m-%dT%H:%M:%S%z"
        time_obj = datetime.strptime(time_str, time_format)
        new_time_obj = time_obj + timedelta(seconds=delay_in_seconds)
        return new_time_obj.strftime(time_format)
        
    
    @staticmethod
    def calculate_definitive_eta(response: TomTomResponse, zip_code_delays: Dict[str, int]) -> TomTomResponse:
        """This method takes a TomTomResponse object and a list of cap delays to update the travelTimeInSeconds variable. 
            It adjusts travel times and arrival/departure times based on the accumulated delays.""" 
        
        logger.debug("Starting definitive ETA calculation.")

        for route in response.routes:
            logger.info(f"Processing the route: {route.summary.startAddress} a {route.summary.endAddress}")
            total_delay = 0
            previous_zip_code = None        
            
            for leg in route.legs:
                # extracting the departure zip_code from the address
                zip_code = leg.summary.departureAddress.split(',')[-1].strip()
                logger.info(f"departure zip_code: {zip_code}")
                
                # checking if the next zip_code is different from the previous one
                if zip_code != previous_zip_code:
                    # recovering the zip_code delay
                    delay = zip_code_delays.get(zip_code, 0)
                    logger.info(f"delay for zip_code {zip_code}: {delay} seconds")
                
                    # adding delay to time
                    leg.summary.travelTimeInSeconds += delay
                    total_delay += delay
                
                    # updating the time of arrival
                    leg.summary.arrivalTime = TomTomParams.add_delay_to_time(leg.summary.departureTime, leg.summary.travelTimeInSeconds)
                
                #updating the previous zip-code
                previous_zip_code = zip_code  
                
                logger.info(f"Update: time of travel: {leg.summary.travelTimeInSeconds} seconds, "
                            f"time of arrival: {leg.summary.arrivalTime}")

            # updating the travel time
            route.summary.travelTimeInSeconds += total_delay
            route.summary.arrivalTime = TomTomParams.add_delay_to_time(route.summary.departureTime, route.summary.travelTimeInSeconds)
            
            logger.info(f"Update: Total time travel: {route.summary.travelTimeInSeconds} seconds, "
                        f"Arrival time: {route.summary.arrivalTime}")
        
        logger.info("Definitive ETA calculatioon completed.")
        return response