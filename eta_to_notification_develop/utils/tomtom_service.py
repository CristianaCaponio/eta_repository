from typing import Dict, List
import requests
from model.delivery import Address
from model.travel_data import StopSummary, Summary, TravelData
from datetime import datetime
from loguru import logger
import os


class TomTom:
    """in this class are stored all the functions related to TomTom and the population of TravelData with the ETAs and information provided by tomTom routing api"""

    @staticmethod
    def order_travel_data(coordinates: List[str]) -> TravelData:
        """this function takes in input a list of strings (the coordinates in string format) and returns a TravelData object.
        I   t recalls all the following functions to create the coordinates string with the format requested by TomTom url, to make the request to TomTom
            and to parse the response in order to obtain a TravelData object populated with all TomTom informations and eta calculations"""

        tomtom_url = TomTom.create_request_string(coordinates)
        json_response = TomTom.tomtom_request(tomtom_url)
        ordered_travel_data = TomTom.parse_tomtom_response(
            json_response)
        return ordered_travel_data

    @staticmethod
    def create_request_string(coordinate_list: List[str]) -> str:        
        """This function takes all coordinates in string format and returns a string with the structure needed for TomTom url. An Example of this string
            is 43.12345,16.12345:43.678910:16.678910."""

        coordinate_str = ""
        for coordinate in coordinate_list:
            coordinate_str = coordinate_str + ":" + coordinate[0] + ","+coordinate[1]  # nopep8

        # logger.info(coordinate_str)

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
        """this function is used to make the request to TomTom and returns a json with the TomTom format"""

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
        """This function parses the reponse provided by TomTom and populates with its data the TravelData object"""
        
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

        )
        logger.info(tomtom_travel_data)
        return tomtom_travel_data
