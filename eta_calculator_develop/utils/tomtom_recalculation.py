import requests
from model.travel_data import TravelData
from model.device_message import DeliveryMessage
from datetime import datetime
from loguru import logger
import os
import pytz

class TomTomRecalculation:
    """
    This class is responsible for recalculating the route for a specific travel based on updated delivery status
    and coordinates. It interacts with the TomTom API to fetch the updated route and estimated times of arrival (ETAs).

    Key Responsibilities:
    1. Updating travel data with the delivery status and recalculating the route.
    2. Making requests to the TomTom API to get route details, wxcepting for the computation of the best route order.
    3. Parsing the response from TomTom to update the travel data and stop details with accurate ETAs.
    4. Updating the status of delivered stops and reordering the route accordingly.
    """

    @staticmethod
    def order_travel_data(travel_data: TravelData) -> TravelData:
        """
        Updates the delivery status of a specific order and recalculates route details.

        Steps:
        1. Check if any stop is not delivered.
        2. If undelivered stops exist, updates the travel data and calls TomTom's API.
        3. Recalculates the route using TomTom’s services.
        4. Adjusts the ETA based on the updated route data.

        Args:
            travel_data (TravelData): The travel data containing the current route and stops.

        Returns:
            TravelData: The updated travel data with new ETAs and route details.

        Raises:
            Exception: If no undelivered stops are found or an issue occurs during request/response handling.
        """
        if travel_data.stops:

            new_travel_data = TomTomRecalculation.update_travel_data_delivers(
                travel_data)
            tomtom_url = TomTomRecalculation.create_request_string(
                new_travel_data)
            json_response = TomTomRecalculation.tomtom_request(tomtom_url)
            ordered_travel_data = TomTomRecalculation.parse_tomtom_response(
                json_response, new_travel_data)
            return ordered_travel_data
        else:
            logger.info("All deliveries were done")
            return travel_data

    @staticmethod
    def create_request_string(travel_data: TravelData) -> str:
        """
        Creates the request string to call the TomTom API for recalculating the route.

        Steps:
        1. Collects the departure and arrival coordinates for all undelivered stops.
        2. Builds the request URL for the API call.

        Args:
            travel_data (TravelData): The travel data containing the current stops.

        Returns:
            str: The formatted request string for the TomTom API.
        """

        departure_coordinates = None
        arrival_coordinates = []

        for single_stop in travel_data.stops:

            if single_stop.delivered is False:

                if departure_coordinates is None:
                    departure_coordinates = [
                        single_stop.departureLatitude, single_stop.departureLongitude]
                    logger.info(f"the departure coordinate is {departure_coordinates}")  # nopep8

                arrival_coordinates.append(
                    [single_stop.arrivalLatitude, single_stop.arrivalLongitude])

        coordinate_list = [departure_coordinates] + arrival_coordinates
        coordinate_str = ":".join(
            [f"{coord[0]},{coord[1]}" for coord in coordinate_list])

        return (
            coordinate_str
            + "/json?routeType=fastest"
            + "&travelMode=car"
            + "&routeRepresentation=summaryOnly"
            + "&departAt=now"
            + "&computeBestOrder=false"
            + "&traffic=true"
        )

    @staticmethod
    def tomtom_request(request_params: str) -> TravelData:
        """
        Sends a request to the TomTom API to get route details.

        Steps:
        1. Builds the full URL using the base URL, request parameters, and API key.
        2. Sends the GET request to TomTom's API and processes the response.

        Args:
            request_params (str): The request parameters to be appended to the TomTom URL.

        Returns:
            TravelData: The updated travel data returned from TomTom’s API.

        Raises:
            ValueError: If the TomTom API key is not set.
            requests.exceptions.RequestException: If there's an issue with the HTTP request.
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
    def parse_tomtom_response(json_response: dict, travel_data: TravelData) -> TravelData:
        """
        Parses the response from TomTom and updates the travel data with route details.

        Steps:
        1. Extracts route and leg summary data (distance, time, delays, etc.) from the response.
        2. Updates the travel data with this information, including start and end times.

        Args:
            json_response (dict): The JSON response returned by the TomTom API.
            travel_data (TravelData): The travel data to be updated with the new route information.

        Returns:
            TravelData: The updated travel data with the parsed route details.
        """
        tomtom_length_in_meters = json_response["routes"][0]["summary"]["lengthInMeters"]
        tomtom_travel_time_in_seconds = json_response["routes"][0]["summary"]["travelTimeInSeconds"]
        tomtom_traffic_delay_in_seconds = json_response["routes"][0]["summary"]["trafficDelayInSeconds"]
        tomtom_traffic_length_in_meters = json_response["routes"][0]["summary"]["trafficLengthInMeters"]
        start_time_iso = datetime.fromisoformat(
            json_response["routes"][0]["summary"]["departureTime"])
        end_time_iso = datetime.fromisoformat(
            json_response["routes"][0]["summary"]["arrivalTime"])

        travel_data.summary.lengthInMeters = tomtom_length_in_meters
        travel_data.summary.travelTimeInSeconds = tomtom_travel_time_in_seconds
        travel_data.summary.trafficDelayInSeconds = tomtom_traffic_delay_in_seconds
        travel_data.summary.trafficLengthInMeters = tomtom_traffic_length_in_meters
        travel_data.summary.departureTime = start_time_iso
        # logger.info(f"the departure time of the summary is {travel_data.summary.departureTime}")  # nopep8
        travel_data.summary.arrivalTime = end_time_iso
        # logger.info(f"the arrival time of the summary is {travel_data.summary.arrivalTime}")  # nopep8

        for leg_index, leg_data in enumerate(json_response["routes"][0]["legs"]):
            stop = travel_data.stops[leg_index]

            stop.lengthInMeters = leg_data["summary"]["lengthInMeters"]
            stop.travelTimeInSeconds = leg_data["summary"]["travelTimeInSeconds"]
            stop.trafficDelayInSeconds = leg_data["summary"]["trafficDelayInSeconds"]
            stop.trafficLengthInMeters = leg_data["summary"]["trafficLengthInMeters"]
            stop.departureTime = datetime.fromisoformat(
                leg_data["summary"]["departureTime"])
            # logger.info(f"the departure time of the stop is {stop.departureTime}")
            stop.arrivalTime = datetime.fromisoformat(
                leg_data["summary"]["arrivalTime"])
            # logger.info(f"the arrival time of the stop is {stop.arrivalTime}")

        travel_data.summary.startAddress = travel_data.stops[0].departureAddress
        travel_data.summary.endAddress = travel_data.stops[-1].arrivalAddress

        return travel_data


    @staticmethod
    def update_route(travel_data: TravelData, update: DeliveryMessage) -> TravelData:
        """
        Updates the route with delivery information for a specific stop.

        Steps:
        1. Finds the stop based on the GSIN and updates the delivered status and delivery time.
        2. Recalculates the route if the stop is successfully marked as delivered.

        Args:
            travel_data (TravelData): The travel data containing the stops.
            update (DeliveryMessage): The message containing delivery information (ginc, gsin and delivery time).

        Returns:
            TravelData: The updated travel data with the new delivery details.
        """

        gsin = update.gsin
        delivered_at = update.delivery_time

        for stop in travel_data.stops:
            if stop.gsin == gsin:
                if stop.delivered is False:

                    stop.delivered_at = delivered_at
                    stop.delivered = True
                else:
                    logger.info(
                        "not possible to update route file, shipment already delivered")
                    return travel_data

        for stop in travel_data.delivered_stops:
            logger.info(f"Stop GSIN {stop.gsin} - Delivered_at: {stop.delivered_at}")
            if stop.gsin == gsin:
                logger.info(
                    "not possible to update route file, shipment already delivered")
                return travel_data

        new_travel_data = TomTomRecalculation.update_travel_data_delivers(
            travel_data)

        #logger.info(f"il travel data inside tomtom_recalculation after the update is: {new_travel_data}")
        return new_travel_data

    @staticmethod
    def update_travel_data_delivers(travel_data: TravelData) -> TravelData:
        """
        Updates the travel data by moving delivered stops to a separate list called 'delivered_stops'.

        Steps:
        1. Iterates through the stops to identify the delivered ones.
        2. Moves delivered stops to the `delivered_stops` list and removes them from `stops`.

        Args:
            travel_data (TravelData): The travel data containing the stops.

        Returns:
            TravelData: The updated travel data with delivered stops moved to `delivered_stops`.
        """

        for stop in travel_data.stops:
            if stop.delivered:
                travel_data.delivered_stops.append(stop)
                del travel_data.stops[travel_data.stops.index(stop)]

        return travel_data
