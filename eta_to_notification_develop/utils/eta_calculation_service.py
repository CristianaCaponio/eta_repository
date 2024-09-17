from fastapi import HTTPException
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
            
            if input_data.ordered == 'true' and input_data.routeRepresentation == 'polyline':
                # takes the first and the last coordinates  ('points') of the leg array in class Route
                departure_coords = jsonResult['routes'][0]['legs'][0]['points'][0]
                arrival_coords = jsonResult['routes'][0]['legs'][-1]['points'][-1]
                start_address = f"{departure_coords['latitude']}, {departure_coords['longitude']}"
                end_address = f"{arrival_coords['latitude']}, {arrival_coords['longitude']}"
            elif input_data.ordered == 'false' and input_data.routeRepresentation == 'summaryOnly':
                # takes the first and the last address of the array locations 
                start_location = input_data.location[0]
                end_location = input_data.location[-1]
                start_address = f"{start_location.address}, {start_location.house_number}, {start_location.city}, {start_location.district}, {start_location.zip_code}"
                end_address = f"{end_location.address}, {end_location.house_number}, {end_location.city}, {end_location.district}, {end_location.zip_code}"
            else:
                 raise HTTPException(
                    status_code=400,
                    detail="Wrong parameters combination. The right combination is: computeBestOrder = true and routeRepresentation = polyline or computeBestOrder = false and routeRepresentation = summaryOnly"
                )
            # Construct the RouteSummary
            route_summary = RouteSummary(
                lengthInMeters=jsonResult['routes'][0]['summary']['lengthInMeters'],
                travelTimeInSeconds=jsonResult['routes'][0]['summary']['travelTimeInSeconds'],
                trafficDelayInSeconds=jsonResult['routes'][0]['summary']['trafficDelayInSeconds'],
                trafficLengthInMeters=jsonResult['routes'][0]['summary']['trafficLengthInMeters'],
                startAddress=start_address,
                endAddress=end_address,
                departureTime=jsonResult['routes'][0]['summary']['departureTime'],
                arrivalTime=jsonResult['routes'][0]['summary']['arrivalTime']
            )
            # Construct the Legs
            legs = []
            i = 0
            for leg_data in jsonResult['routes'][0]['legs']:                
                 
                if input_data.ordered == 'true' and input_data.routeRepresentation == 'polyline':
                    departure_coords = leg_data['points'][0]
                    arrival_coords = leg_data['points'][-1]
                    departure_address = f"{departure_coords['latitude']}, {departure_coords['longitude']}"
                    arrival_address = f"{arrival_coords['latitude']}, {arrival_coords['longitude']}"
                elif input_data.ordered == 'false' and input_data.routeRepresentation == 'summaryOnly':
                    # Usa gli indirizzi se ordered == 'false' o routeRepresentation == 'summaryOnly'
                    departure_address = input_data.location[i]
                    arrival_address = input_data.location[i + 1]
                    departure_address = f"{departure_address.address}, {departure_address.house_number},{departure_address.city}, {departure_address.district}, {departure_address.zip_code}"
                    arrival_address = f"{arrival_address.address}, {arrival_address.house_number}, {arrival_address.city}, {arrival_address.district}, {arrival_address.zip_code}"
                else:
                    raise HTTPException(
                    status_code=400,
                    detail="Wrong parameters combination. The right combination is: computeBestOrder = true and routeRepresentation = polyline or computeBestOrder = false and routeRepresentation = summaryOnly"
                )
                
                leg_summary = LegSummary(
                    lengthInMeters=leg_data['summary']['lengthInMeters'],
                    travelTimeInSeconds=leg_data['summary']['travelTimeInSeconds'],
                    trafficDelayInSeconds=leg_data['summary']['trafficDelayInSeconds'],
                    departureAddress= departure_address,
                    arrivalAddress= arrival_address,
                    trafficLengthInMeters=leg_data['summary']['trafficLengthInMeters'],
                    departureTime=leg_data['summary']['departureTime'],
                    arrivalTime=leg_data['summary']['arrivalTime'],
                    originalWaypointIndexAtEndOfLeg=leg_data['summary'].get('originalWaypointIndexAtEndOfLeg', 0)
                )            
                                                                        
                leg = Leg(
                    summary=leg_summary,                    
                )
                legs.append(leg)
                i= i + 1                
           
            # Construct the Route
            route = Route(
                summary=route_summary,
                legs=legs,                
            )
           
            # Construct the TomTomResponse
            tomtom_response = TomTomResponse(
                formatVersion="0.0.12",
                routes=[route],                
            )         
          
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
                if zip_code is not None:
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
