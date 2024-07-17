import requests
from utils.address_converter_service import AddressConverter
from model.input_data import InputData
from model.output_data import TomTomResponse, RouteSummary, Point, LegSummary, Leg, Section, Route
from loguru import logger
import os
import urllib.parse as urlparse

class TomTomParams:
    
    @staticmethod
    def request_params(input_data: InputData) -> str:
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
        
        #load_dotenv() 
         # Building the request URL
        baseUrl = "https://api.tomtom.com/routing/1/calculateRoute/" 
        API_KEY = os.getenv("TOMTOM_API_KEY")
        logger.info(API_KEY)        
        if not API_KEY:
            raise ValueError("TOMTOM_API_KEY environment variable is not set.")         
        requestUrl = baseUrl + request_params + "&key=" + API_KEY
        logger.info("Request URL: " + requestUrl + "\n")
        
        
        # Sending the request
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
