from typing import Dict, List
import requests
from model.delivery import Address
from model.travel_data import StopSummary, Summary, TravelData
from datetime import datetime
from loguru import logger
import os


class TomTom:
    """
    The TomTom class provides methods for interacting with the TomTom Routing API to calculate optimal routes
    and estimate travel times. It retrieves route details, including distance, time, traffic conditions, and 
    stop information, and processes this data into a structured `TravelData` object.

    Key Responsibilities:
    1. Generate API request strings to interact with TomTom's routing service.
    2. Make requests to the TomTom API to obtain routing information in JSON format.
    3. Parse the response from TomTom to extract useful information like route details, stop information, 
       and estimated travel times.
    4. Populate a `TravelData` object with the parsed route and stop details, which can then be used for 
       further processing or display.
    """

    @staticmethod
    def order_travel_data(coordinates: List[str]) -> TravelData:
        """
        Generate a TravelData object enriched with route details and ETAs using TomTom's API.

        Steps:
        1. Create a request URL with the provided coordinates.
        2. Send the request to TomTom's routing service and obtains in response a JSON.
        3. Parse the JSON response to extract route details and stop information.
        4. Populate a TravelData object with the calculated route data.

        Args:
            coordinates (List[str]): A list of coordinates (latitude, longitude) as strings.

        Returns:
            TravelData: The enriched TravelData object containing route and stop information.

        Raises:
            ValueError: If the TOMTOM_API_KEY environment variable is not set.
            HTTPError: If the TomTom API request fails.
        """

        tomtom_url = TomTom.create_request_string(coordinates)
        json_response = TomTom.tomtom_request(tomtom_url)
        ordered_travel_data = TomTom.parse_tomtom_response(
            json_response)
        
        return ordered_travel_data

    @staticmethod
    def create_request_string(coordinate_list: List[str]) -> str:        
        
        """
        Construct a TomTom API request string from a list of coordinates.

        Steps:
        1. Format the coordinates into a string structure acceptable by TomTom's API.
        2. Append additional query parameters required for the request.

        Args:
            coordinate_list (List[str]): A list of coordinates (latitude, longitude) as strings.

        Returns:
            str: A formatted request string to be used in the TomTom API URL.
        """

        coordinate_str = ""

        for coordinate in coordinate_list:
            coordinate_str = coordinate_str + ":" + coordinate[0] + ","+coordinate[1]  # nopep8

        return (
            coordinate_str[1:]
            + "/json?routeType=fastest"
            + "&travelMode=car"
            + "&routeRepresentation=polyline"
            + "&departAt=now"
            + "&computeBestOrder=true"
            + "&traffic=true"
        )

    @staticmethod
    def tomtom_request(request_params: str) -> TravelData:
        """
        Make a request to the TomTom API and return the JSON response.

        Steps:
        1. Construct the full request URL using the provided parameters.
        2. Send the request to TomTom's API.
        3. Obtains the response which is in JSON format.

        Args:
            request_params (str): The query string parameters for the TomTom request.

        Returns:
            dict: The JSON response from the TomTom API containing routing information.

        Raises:
            ValueError: If the TOMTOM_API_KEY environment variable is not set.
            HTTPError: If the TomTom API request fails.
        """

        baseUrl = "https://api.tomtom.com/routing/1/calculateRoute/"
        API_KEY = os.getenv("TOMTOM_API_KEY")

        if not API_KEY:
            raise ValueError("TOMTOM_API_KEY environment variable is not set.")

        requestUrl = baseUrl + request_params + "&key=" + API_KEY
        logger.info("Request URL: " + requestUrl + "\n")

        response = requests.get(requestUrl)
        # logger.info(response)
        response.raise_for_status()

        if response.status_code == 200:
            jsonResult = response.json()
            return jsonResult
        else:
            return None

    @staticmethod
    def parse_tomtom_response(json_response: dict) -> TravelData:
        """
        Parse the response from TomTom and populate a TravelData object.

        Steps:
        1. Extract relevant information from the JSON response (e.g., route summary, stop details).
        2. Create TravelData objects populated with the parsed data.

        Args:
            json_response (dict): The JSON response from TomTom's API containing routing information.

        Returns:
            TravelData: A TravelData object populated with parsed information, including summary and stops.
        """

        tomtom_start_latitude = json_response["routes"][0]["legs"][0]["points"][0]["latitude"]
        tomtom_start_longitude = json_response["routes"][0]["legs"][0]["points"][0]["longitude"]
        tomtom_end_latitude = json_response['routes'][0]['legs'][-1]['points'][-1]["latitude"]
        tomtom_end_longitude = json_response['routes'][0]['legs'][-1]['points'][-1]["longitude"]
        start_time_iso = datetime.fromisoformat(json_response["routes"][0]["summary"]["departureTime"])
        end_time_iso = datetime.fromisoformat(json_response["routes"][0]["summary"]["arrivalTime"])
       
        route_summary = Summary(
           
            travelMode = json_response["routes"][0]["sections"][0]["travelMode"],
            lengthInMeters = json_response["routes"][0]["summary"]["lengthInMeters"],
            travelTimeInSeconds = json_response["routes"][0]["summary"]["travelTimeInSeconds"],
            trafficDelayInSeconds = json_response["routes"][0]["summary"]["trafficDelayInSeconds"],
            trafficLengthInMeters = json_response["routes"][0]["summary"]["trafficLengthInMeters"],
            startAddress = Address(
                address = "address1", city = "city1", district = "disctrict1", house_number = "number1", zip_code = "zip_code1", telephone_number = "some_number"),
            startLatitude = tomtom_start_latitude,
            startLongitude = tomtom_start_longitude,
            endAddress = Address(
                address = "address1", city = "city1", district = "disctrict1", house_number = "number1", zip_code = "zip_code1", telephone_number = "some_other_number"),
            endLatitude = tomtom_end_latitude,
            endLongitude = tomtom_end_longitude,
            departureTime = start_time_iso,
            arrivalTime = end_time_iso 
        )
     
        stops = []

        for leg_data in json_response["routes"][0]["legs"]:
            tomtom_departure_latitude = leg_data["points"][0]["latitude"]
            tomtom_departure_longitude = leg_data["points"][0]["longitude"]
            tomtom_arrival_latitude = leg_data['points'][-1]["latitude"]
            tomtom_arrival_longitude = leg_data['points'][-1]["longitude"]             
            departure_time_iso = datetime.fromisoformat(leg_data["summary"]["departureTime"])
            arrival_time_iso = datetime.fromisoformat(leg_data["summary"]["arrivalTime"])

            stop_summary = StopSummary(
                gsin = "some_gsin",  
                lengthInMeters = leg_data["summary"]["lengthInMeters"],
                travelTimeInSeconds = leg_data["summary"]["travelTimeInSeconds"],
                trafficDelayInSeconds = leg_data["summary"]["trafficDelayInSeconds"],
                departureAddress = Address(
                    address = "address1", city = "city1", district = "disctrict1", house_number = "number1", zip_code = "zip_code1", telephone_number = "one_number"), 
                departureLatitude = tomtom_departure_latitude,
                departureLongitude = tomtom_departure_longitude,
                arrivalAddress = Address(
                    address = "address1", city = "city1", district = "disctrict1", house_number = "number1", zip_code = "zip_code1", telephone_number = "one_other_number"),
                arrivalLatitude = tomtom_arrival_latitude,
                arrivalLongitude = tomtom_arrival_longitude,
                trafficLengthInMeters = leg_data["summary"]["trafficLengthInMeters"],
                departureTime = departure_time_iso,#leg_data["summary"]["departureTime"],
                arrivalTime = arrival_time_iso,#leg_data["summary"]["arrivalTime"],
                delivered = False  
            )
            stops.append(stop_summary)
       
        tomtom_travel_data = TravelData(
            personal_id = datetime.now().strftime("%m_%d_%Y_%H_%M_%S"),    
            summary = route_summary,  
            ginc = "some_ginc",
            stops = stops, 
            delivered_stops = []                               

        )
        #logger.info(tomtom_travel_data)
        return tomtom_travel_data
