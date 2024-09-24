from typing import List, Tuple
import os
from io import StringIO
from model.db_models import StopSummary, Summary, TravelData
from geopy.geocoders import ArcGIS  # Nominatim
from model.delivery import Delivery, Address
from geopy.extra.rate_limiter import RateLimiter
from loguru import logger
import datetime


class PreProces:

    @staticmethod
    def populate_travel_data(delivery_list: List[Delivery]) -> Tuple[List[str], TravelData]:
        """Popola TravelData con coordinate e indirizzi."""

        coordinates = PreProces.address_to_coordinates_converter(
            delivery_list)

        if len(coordinates) < 2:
            raise ValueError(
                "La lista deve contenere almeno due indirizzi per start e end.")

        new_summary = Summary(
            startLatitude=coordinates[0][0],
            startLongitude=coordinates[0][1],
            endLatitude=coordinates[-1][0],
            endLongitude=coordinates[-1][1],
            startAddress=delivery_list[0].address,
            endAddress=delivery_list[-1].address
        )
        new_stops = []
        for i in range(len(delivery_list) - 1):

            address_stop = StopSummary(
                gsin=delivery_list[i+1].gsin,
                departureLatitude=coordinates[i][0],
                departureLongitude=coordinates[i][1],
                arrivalLatitude=coordinates[i + 1][0],
                arrivalLongitude=coordinates[i + 1][1],
                departureAddress=delivery_list[i].address,
                arrivalAddress=delivery_list[i + 1].address
            )
            new_stops.append(address_stop)

        travel_data = TravelData(
            personal_id="temporary_ID",
            summary=new_summary,
            stops=new_stops
        )

        return coordinates, travel_data

    # @staticmethod
    # def coordinate_to_string(coordinates: List[tuple]) -> str:

    #     if not coordinates or len(coordinates[0]) < 2:
    #         raise ValueError("La lista delle coordinate è vuota o malformata.")
    #     full_coordinates_list = StringIO()
    #     full_coordinates_list.write(f"{coordinates[0][0]},{coordinates[0][1]}")

    #     for single_coordinate in coordinates[1:]:
    #         full_coordinates_list.write(f":{single_coordinate[0]},{single_coordinate[1]}")  # nopep8

    #     return full_coordinates_list.getvalue()

    @staticmethod
    def address_to_coordinates_converter(delivery_list: List[Delivery]) -> List[str]:
        logger.info("enter in address to coordinate converter")
        request = os.environ.get("USER_AGENT", "my_agent")
        geolocator = ArcGIS(user_agent=request)
        geocode = RateLimiter(geolocator.geocode,
                              min_delay_seconds=1, max_retries=10)

        coordinates = []
        for delivery in delivery_list:
            add = delivery.address
            full_address = f"{add.address}, {add.house_number}, {add.city}, {add.district}, {add.zip_code}"  # nopep8
            try:
                location = geocode(full_address, exactly_one=True)
                if location:
                    print(f"Geocoded address: {full_address} to {location.latitude}, {location.longitude}")  # nopep8
                    # ((location.latitude, location.longitude))
                    coordinates.append((f"{location.latitude}", f"{location.longitude}"))  # nopep8

                else:
                    print(f"A non-existent address was added: {full_address}")
                    return ""
            except Exception as e:
                print(f"Error geocoding address {full_address}: {e}")
                return ""

        # logger.info(coordinates)
        return coordinates

        # travel_data_populated = AddressConverter.populate_travel_data(
        #     coordinates, address_list)
        # logger.info(travel_data_populated)

        # coordinates_string = AddressConverter.coordinate_to_string(coordinates)
        # logger.info(coordinates_string)
        # return coordinates_string

    # @staticmethod
    # def address_to_coordinates_converter(delivery: Delivery) -> List[float]:
    #     """
    #     Converts a list of addresses into a single string of geographical coordinates.

    #     Parameters
    #     ----------
    #     address: GeopyInputData
    #         A GeopyInputData objects containing address details.

    #     Returns
    #     -------
    #     str
    #         A list with Latitude and Longitude

    #     """
    #     request = os.environ.get("USER_AGENT", "my_agent")
    #     logger.info(request)
    #     geolocator = ArcGIS(user_agent=request)
    #     geocode = RateLimiter(geolocator.geocode,
    #                           min_delay_seconds=1,  max_retries=10)

    #     try:
    #         full_address = f"{delivery.address}, {delivery.house_number}, {delivery.city}, {delivery.district}, {delivery.zip_code}"  # nopep8
    #         location = geolocator.geocode(full_address)

    #         if location is not None:
    #             coordinates = [location.latitude, location.longitude]
    #             return coordinates
    #         else:
    #             logger.error(
    #                 f"A non-existent address was added: {full_address}")
    #     except Exception as e:
    #         logger.error(f"Error geocoding address {full_address}: {e}")
