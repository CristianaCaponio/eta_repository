from typing import Dict, List
import requests
from model.delivery import Address
from model.db_models import StopSummary, Summary, TravelData
from datetime import datetime
from loguru import logger
import os
import urllib.parse as urlparse


class TomTom:

    @staticmethod
    def order_travel_data(coordinates: List[str]) -> TravelData:
        tomtom_url = TomTom.create_request_string(coordinates)
        json_response = TomTom.tomtom_request(tomtom_url)
        ordered_travel_data = TomTom.parse_tomtom_response(
            json_response)
        return ordered_travel_data

    @staticmethod
    def create_request_string(coordinate_list: List[str]) -> str:
        # logger.info("sono entrato in request_param di TomTomParams")
        """This method takes all coordinates from travel data (considered parameter -> stops: List[stopSummary] )and returns a query parameter string formatted to build the request URL."""
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
        # logger.info("sono entrato in tomtom_request di TomTomParams")
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

        # Get start and end coordinates from TomTom
        tomtom_start_latitude = json_response["routes"][0]["legs"][0]["points"][0]["latitude"]
        tomtom_start_longitude = json_response["routes"][0]["legs"][0]["points"][0]["longitude"]
        tomtom_end_latitude = json_response['routes'][0]['legs'][-1]['points'][-1]["latitude"]
        tomtom_end_longitude = json_response['routes'][0]['legs'][-1]['points'][-1]["longitude"]

        # Construct the Summary
        route_summary = Summary(
            # Corrected
            travelMode=json_response["routes"][0]["sections"][0]["travelMode"],
            lengthInMeters=json_response["routes"][0]["summary"]["lengthInMeters"],
            travelTimeInSeconds=json_response["routes"][0]["summary"]["travelTimeInSeconds"],
            trafficDelayInSeconds=json_response["routes"][0]["summary"]["trafficDelayInSeconds"],
            trafficLengthInMeters=json_response["routes"][0]["summary"]["trafficLengthInMeters"],
            startAddress=Address(
                address="address1", city="city1", district="disctrict1", house_number="number1", zip_code="zip_code1"),
            startLatitude=tomtom_start_latitude,
            startLongitude=tomtom_start_longitude,
            endAddress=Address(
                address="address1", city="city1", district="disctrict1", house_number="number1", zip_code="zip_code1"),
            endLatitude=tomtom_end_latitude,
            endLongitude=tomtom_end_longitude,
            departureTime=json_response["routes"][0]["summary"]["departureTime"],
            arrivalTime=json_response["routes"][0]["summary"]["arrivalTime"]
        )

        # Construct the Stops
        stops = []
        for leg_data in json_response["routes"][0]["legs"]:
            tomtom_departure_latitude = leg_data["points"][0]["latitude"]
            tomtom_departure_longitude = leg_data["points"][0]["longitude"]
            tomtom_arrival_latitude = leg_data['points'][-1]["latitude"]
            tomtom_arrival_longitude = leg_data['points'][-1]["longitude"]

            stop_summary = StopSummary(
                gsin="some_gsin",  # Placeholder, replace with real data
                lengthInMeters=leg_data["summary"]["lengthInMeters"],
                travelTimeInSeconds=leg_data["summary"]["travelTimeInSeconds"],
                trafficDelayInSeconds=leg_data["summary"]["trafficDelayInSeconds"],
                departureAddress=Address(
                    address="address1", city="city1", district="disctrict1", house_number="number1", zip_code="zip_code1"),
                departureLatitude=tomtom_departure_latitude,
                departureLongitude=tomtom_departure_longitude,
                arrivalAddress=Address(
                    address="address1", city="city1", district="disctrict1", house_number="number1", zip_code="zip_code1"),
                arrivalLatitude=tomtom_arrival_latitude,
                arrivalLongitude=tomtom_arrival_longitude,
                trafficLengthInMeters=leg_data["summary"]["trafficLengthInMeters"],
                departureTime=leg_data["summary"]["departureTime"],
                arrivalTime=leg_data["summary"]["arrivalTime"],
                delivered=False  # Placeholder, adjust as needed
            )
            stops.append(stop_summary)

            # Populating TravelData
        tomtom_travel_data = TravelData(
            personal_id=datetime.now().strftime("%m_%d_%Y_%H_%M_%S"),
            summary=route_summary,  # Corrected field name
            stops=stops  # Corrected field name
        )

        return tomtom_travel_data
