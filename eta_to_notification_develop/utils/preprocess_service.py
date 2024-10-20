from typing import List, Tuple
import os
from io import StringIO
from model.travel_data import StopSummary, Summary, TravelData
from geopy.geocoders import ArcGIS  
from model.delivery import Delivery
from geopy.extra.rate_limiter import RateLimiter
from loguru import logger


class PreProcess():
    """This class is used to create the string of coordinates that will be included in tomTom url and to populate TravelData before the eta calculation"""

    @staticmethod
    def populate_travel_data(delivery_list: List[Delivery]) -> Tuple[List[str], TravelData]:
        """this function takes in input a list of Delivery (with a gsin and a full address) and returns a Tuple with a list of coordinates in str format and 
            a TravelData object populated with coordinates and addresses. This function calls address_to_coordinates_converter to convert addresses into coordinates
            and then both data are used to populate TravelData"""

        coordinates = PreProcess.address_to_coordinates_converter(
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
            ginc= "some_ginc",      
            summary=new_summary,
            stops=new_stops
        )
        logger.info(f"travel data in preprocess_service: {travel_data}")

        return coordinates, travel_data

    @staticmethod
    def address_to_coordinates_converter(delivery_list: List[Delivery]) -> List[str]:
        """this function takes in input a list of Delivery (with a gsin and a full address) and returns a string of coordinates in str format"""      

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
                    coordinates.append((f"{location.latitude}", f"{location.longitude}"))  # nopep8
                    logger.info(coordinates)

                else:
                    print(f"A non-existent address was added: {full_address}")
                    return ""
            except Exception as e:
                print(f"Error geocoding address {full_address}: {e}")
                return ""

        # logger.info(coordinates)
        return coordinates

    