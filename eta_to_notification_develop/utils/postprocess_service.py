from geopy import distance
from model.travel_data import TravelData
from model.response import Response, Delivery_ETA
from loguru import logger
from datetime import datetime, timedelta
from typing import Dict, List
from io import StringIO
import csv


class PostProcess():
    """
    The `PostProcess` class contains functionality to process travel data after the main processing step. 
    It is responsible for associating addresses to the travel data, updating estimated times of arrival (ETAs), 
    and preparing the final response with the necessary delivery information.

    Key Responsibilities:
    1. **Address Association**: Associate delivery addresses to their respective stops in the ordered travel data.
    2. **Delay Handling**: Apply delays to the departure and arrival times based on zip codes.
    3. **ETA Calculation**: Calculate and update the estimated time of arrival for each delivery stop.
    4. **Response Creation**: Prepare a structured response containing all relevant delivery ETA details.
    """

    @staticmethod
    def associate_address(raw_travel_data: TravelData, ordered_travel_data: TravelData) -> TravelData:
        """
        This method associates the delivery addresses to the stops in the ordered travel data based on geographic proximity.

        It compares the departure and arrival locations of each stop in `raw_travel_data` with the corresponding stops in `ordered_travel_data`, 
        calculating the distance between them. The closest match is used to assign the correct address to each stop.

        Args:
            raw_travel_data (TravelData): The original unprocessed travel data.
            ordered_travel_data (TravelData): The ordered travel data that needs to be updated with addresses.

        Returns:
            TravelData: The updated `ordered_travel_data` with the correct addresses associated to each stop.
        """

        for stop in raw_travel_data.stops:
            departure_latitude = stop.departureLatitude
            departure_longitude = stop.departureLongitude
            arrival_latitude = stop.arrivalLatitude
            arrival_longitude = stop.arrivalLongitude

            dep_dist_list = []
            arr_dist_list = []

            for i in range(len(ordered_travel_data.stops)):

                ordered_departure_latitude = ordered_travel_data.stops[i].departureLatitude
                ordered_departure_longitude = ordered_travel_data.stops[i].departureLongitude
                ordered_arrival_latitude = ordered_travel_data.stops[i].arrivalLatitude
                ordered_arrival_longitude = ordered_travel_data.stops[i].arrivalLongitude

                dep_dist = distance.distance((departure_latitude, departure_longitude), (
                    ordered_departure_latitude, ordered_departure_longitude)).m
                # logger.info(f"departure distance:{dep_dist}")
                dep_dist_list.append(dep_dist)

                arr_dist = distance.distance(
                    (arrival_latitude, arrival_longitude), (ordered_arrival_latitude, ordered_arrival_longitude)).m
                # logger.info(f"arrival distance:{arr_dist}")
                arr_dist_list.append(arr_dist)

            departure_min_index = dep_dist_list.index(min(dep_dist_list))
            arrival_min_index = arr_dist_list.index(min(arr_dist_list))

            ordered_travel_data.stops[departure_min_index].departureAddress = stop.departureAddress
            ordered_travel_data.stops[arrival_min_index].arrivalAddress = stop.arrivalAddress
            ordered_travel_data.stops[arrival_min_index].gsin = stop.gsin
            ordered_travel_data.summary.startAddress = ordered_travel_data.stops[
                0].departureAddress
            ordered_travel_data.summary.endAddress = ordered_travel_data.stops[-1].arrivalAddress

        return ordered_travel_data

    @staticmethod
    def add_delay_to_time(time_obj: datetime, delay_in_seconds: int) -> datetime:
        """
        Adds a delay to the provided time object by a specified number of seconds.

        This method is useful for adjusting the estimated times of arrival (ETA) for each stop based on delays 
        due to factors like traffic or processing times.

        Args:
            time_obj (datetime): The original time object (either departure or arrival time).
            delay_in_seconds (int): The delay in seconds to be added to the time.

        Returns:
            datetime: The new time object with the delay applied.
        """
        new_time_obj = time_obj + timedelta(seconds=delay_in_seconds)

        return new_time_obj

    @staticmethod
    def update_eta(travel_data: TravelData, zip_code_delay: Dict[str, int], default_delay: int) -> TravelData:
        """
        Updates the ETAs for each stop in the travel data, considering delays based on zip code.

        The method checks the delay for each stop based on its zip code and adds it to both the departure and arrival times. 
        If no specific delay is found for a zip code, a default delay is applied.

        Args:
            travel_data (TravelData): The travel data containing the stops with their respective times.
            zip_code_delay (Dict[str, int]): A dictionary mapping zip codes to delay values (in seconds).
            default_delay (int): The default delay (in seconds) to be applied if no zip code-specific delay is found.

        Returns:
            TravelData: The updated travel data with the new ETAs.
        """
        logger.info(f'the default cap delay is {default_delay}')
        if not travel_data.stops:
            logger.info(
                "No stops available in travel_data. Skipping ETA update.")
            return travel_data

        for i in range(len(travel_data.stops)-1):
            zip_code = travel_data.stops[i+1].departureAddress.zip_code
            # delay = zip_code_delay[f"{zip_code}"]
            delay = zip_code_delay.get(zip_code, default_delay)

            for y in range(i+1, len(travel_data.stops)):
                dep_time = travel_data.stops[y].departureTime
                arr_time = travel_data.stops[y].arrivalTime
                travel_data.stops[y].departureTime = PostProcess.add_delay_to_time(
                    dep_time, delay)
                travel_data.stops[y].arrivalTime = PostProcess.add_delay_to_time(
                    arr_time, delay)
        travel_data.summary.arrivalTime = travel_data.stops[-1].arrivalTime

        return travel_data

    @staticmethod
    def process_stops(travel_data: TravelData) -> list[Delivery_ETA]:
        """
        Processes the stops in the travel data to create a list of `Delivery_ETA` objects.

        This method constructs a `Delivery_ETA` object for each stop, containing the delivery information 
        (such as GSIN, address, ETA, and delivery status). The resulting list can be used for reporting or 
        generating responses for external systems.

        Args:
            travel_data (TravelData): The travel data containing the stops to be processed.

        Returns:
            List[Delivery_ETA]: A list of `Delivery_ETA` objects representing the ETA details for each stop.
        """
        result = []
        all_stops = []
        if travel_data.delivered_stops:
            all_stops.extend(travel_data.delivered_stops)
        if travel_data.stops:
            all_stops.extend(travel_data.stops)

        for stop in all_stops:
            try:
                delivery_eta = Delivery_ETA(**{
                    'gsin': stop.gsin,
                    'address': stop.arrivalAddress,
                    'eta': stop.arrivalTime,
                    'delivered': stop.delivered,
                    'delivered_at': stop.delivered_at
                })
                result.append(delivery_eta)
            except AttributeError as e:
                logger.error(
                    f"Error during Delivery_ETA creation for {stop}: {e}")
        return result

    @staticmethod
    def create_response(travel_data: TravelData) -> Response:
        """
        Creates a structured `Response` object containing the travel data and delivery ETA information.

        This method aggregates the processed delivery ETAs into a response format that can be sent to clients 
        or used by other services. The response includes the travel summary, personal ID, GINC, and a list of 
        `Delivery_ETA` objects.

        Args:
            travel_data (TravelData): The travel data containing delivery stop details.

        Returns:
            Response: A structured response object containing the travel and delivery ETA data.
        """
        delivery = PostProcess.process_stops(travel_data)

        response = Response(**{
            'ginc': travel_data.ginc,
            'personal_id': travel_data.personal_id,
            'delivery': delivery
        })
        return response

    @staticmethod
    def generate_csv(travel_data: TravelData) -> StringIO:
        """
        Generates a CSV file containing delivery information.

        Args:
            travel_data (TravelData): A TravelData object containing delivery details.

        Returns:
            StringIO: In-memory CSV file containing delivery details.
        """
        csv_file = StringIO()
        csv_writer = csv.writer(csv_file)

        csv_writer.writerow([
            "id", "indirizzo", "città", "provincia", "numero civico", "cap", "telefono", "orario"
        ])

        if travel_data.stops:
            first_stop = travel_data.stops[0]
            departure_address = first_stop.departureAddress
            departure_time = first_stop.departureTime
            departure_gsin = first_stop.gsin

            csv_writer.writerow([
                departure_gsin,
                departure_address.address,
                departure_address.city,
                departure_address.district,
                departure_address.house_number,
                departure_address.zip_code,
                departure_address.telephone_number,
                departure_time.isoformat(),
            ])

            for single_delivery in travel_data.stops:

                arrival_address = single_delivery.arrivalAddress
                csv_writer.writerow([
                    single_delivery.gsin,
                    arrival_address.address,
                    arrival_address.city,
                    arrival_address.district,
                    arrival_address.house_number,
                    arrival_address.zip_code,
                    arrival_address.telephone_number,
                    single_delivery.arrivalTime.isoformat(),
                ])

        csv_file.seek(0)
        return csv_file
