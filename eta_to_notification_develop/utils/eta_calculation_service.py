import requests
from utils.address_converter_service import AddressConverter
from model.input_data import InputData
from model.tomtom_output_data import TomTomResponse, RouteSummary, Point, LegSummary, Leg, Section, Route
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
            + "&computeBestOrder=" + str(input_data.computeBestOrder).lower()
            + "&departAt=" + urlparse.quote(input_data.departAt)
        )        
        
    
    @staticmethod
    def tomtom_request(request_params: str) -> TomTomResponse:
        """This method receives a query parameter string (obtained from the request_params method), appends it to the base URL and adds the API key.
            It constructs the complete URL for making the request to the TomTom API and retrieves information from the service."""
        baseUrl = "https://api.tomtom.com/routing/1/calculateRoute/" 
        API_KEY = os.getenv("TOMTOM_API_KEY")
        logger.info(API_KEY)    
            
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

            # Construct the RouteSummary
            route_summary = RouteSummary(
                lengthInMeters=jsonResult['routes'][0]['summary']['lengthInMeters'],
                travelTimeInSeconds=jsonResult['routes'][0]['summary']['travelTimeInSeconds'],
                trafficDelayInSeconds=jsonResult['routes'][0]['summary']['trafficDelayInSeconds'],
                trafficLengthInMeters=jsonResult['routes'][0]['summary']['trafficLengthInMeters'],
                departureTime=jsonResult['routes'][0]['summary']['departureTime'],
                arrivalTime=jsonResult['routes'][0]['summary']['arrivalTime']
            )
            # Construct the Legs
            legs = []
            for leg_data in jsonResult['routes'][0]['legs']:
                leg_summary = LegSummary(
                    lengthInMeters=leg_data['summary']['lengthInMeters'],
                    travelTimeInSeconds=leg_data['summary']['travelTimeInSeconds'],
                    trafficDelayInSeconds=leg_data['summary']['trafficDelayInSeconds'],
                    trafficLengthInMeters=leg_data['summary']['trafficLengthInMeters'],
                    departureTime=leg_data['summary']['departureTime'],
                    arrivalTime=leg_data['summary']['arrivalTime'],
                    originalWaypointIndexAtEndOfLeg=leg_data['summary'].get('originalWaypointIndexAtEndOfLeg', 0)
                )                
               
                # Include only the first and last points
                points = []
                if leg_data['points']:
                    points.append(Point(latitude=leg_data['points'][0]['latitude'], longitude=leg_data['points'][0]['longitude']))
                    if len(leg_data['points']) > 1:
                        points.append(Point(latitude=leg_data['points'][-1]['latitude'], longitude=leg_data['points'][-1]['longitude']))
                                            
                leg = Leg(
                    summary=leg_summary,
                    points=points
                )
                legs.append(leg)

            # Construct the Sections
            sections = [
                Section(
                    startPointIndex=section['startPointIndex'],
                    endPointIndex=section['endPointIndex'],
                    sectionType=section['sectionType'],
                    travelMode=section['travelMode']
                )
                for section in jsonResult['routes'][0]['sections']
            ]

            # Construct the Route
            route = Route(
                summary=route_summary,
                legs=legs,
                sections=sections
            )

            # Construct the optimized waypoints
            optimized_waypoints = jsonResult.get('optimizedWaypoints', [])

            # Construct the TomTomResponse
            tomtom_response = TomTomResponse(
                formatVersion="0.0.12",
                routes=[route],
                optimizedWaypoints=optimized_waypoints
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
    def calculate_definitive_eta(response: TomTomResponse, cap_delays: list[int]) -> TomTomResponse:
        """This method takes a TomTomResponse object and a list of cap delays to update the travelTimeInSeconds variable. 
            It adjusts travel times and arrival/departure times based on the accumulated delays.""" 
        for route in response.routes:
            total_delay = 0
            for i, leg in enumerate(route.legs):                
                total_delay += cap_delays[i]
                leg.summary.travelTimeInSeconds += total_delay
                leg.summary.arrivalTime = TomTomParams.add_delay_to_time(leg.summary.arrivalTime, total_delay)               
               
                if i < len(route.legs) - 1:
                    next_leg = route.legs[i + 1]
                    next_leg.summary.departureTime = TomTomParams.add_delay_to_time(next_leg.summary.departureTime, total_delay)
                    
            route.summary.travelTimeInSeconds += total_delay
            route.summary.arrivalTime = TomTomParams.add_delay_to_time(route.summary.arrivalTime, total_delay)
        
        return response
