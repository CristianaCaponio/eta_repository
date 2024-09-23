from typing import List
import os
from io import StringIO
from model.db_models import StopSummary, Summary, TravelData
from geopy.geocoders import ArcGIS #Nominatim
from model.geopy_input_data import GeopyInputData
from geopy.extra.rate_limiter import RateLimiter
from loguru import logger


class AddressConverter:

    @staticmethod
    def populate_travel_data(coordinates: List[tuple], address_list: List[GeopyInputData]) -> TravelData:
        """Popola TravelData con coordinate e indirizzi."""
        if len(coordinates) < 2:
            raise ValueError("La lista deve contenere almeno due indirizzi per start e end.")

        new_summary = Summary(
            startLatitude=coordinates[0][0],
            startLongitude=coordinates[0][1],
            endLatitude=coordinates[-1][0],
            endLongitude=coordinates[-1][1],
            startAddress=address_list[0],
            endAddress=address_list[-1]
        )
        new_stops = []
        for i in range(len(address_list) - 1):
            address_stop = StopSummary(
                departureLatitude=coordinates[i][0],
                departureLongitude=coordinates[i][1],
                arrivalLatitude=coordinates[i + 1][0],
                arrivalLongitude=coordinates[i + 1][1],
                departureAddress=address_list[i],
                arrivalAddress=address_list[i + 1]
            )
            new_stops.append(address_stop)

        travel_data = TravelData(
            personal_id="banana",
            summary=new_summary,
            stops=new_stops
        )
        
        return travel_data

    @staticmethod
    def coordinate_to_string(coordinates: List[tuple]) -> str:
        
        if not coordinates or len(coordinates[0]) < 2:
            raise ValueError("La lista delle coordinate è vuota o malformata.")
        full_coordinates_list = StringIO()
        full_coordinates_list.write(f"{coordinates[0][0]},{coordinates[0][1]}")

        for single_coordinate in coordinates[1:]:
            full_coordinates_list.write(f":{single_coordinate[0]},{single_coordinate[1]}")

        return full_coordinates_list.getvalue()

    @staticmethod
    def address_to_coordinates_converter(address_list: List[GeopyInputData]) -> str:
        request = os.environ.get("USER_AGENT", "my_agent")
        geolocator = ArcGIS(user_agent=request)
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=10)

        coordinates = []
        for single_address in address_list:
            full_address = f"{single_address.address}, {single_address.house_number}, {single_address.city}, {single_address.district}, {single_address.zip_code}"
            try:
                location = geocode(full_address,exactly_one = True)
                logger.info(location.latitude)

                if location:
                    print(f"Geocoded address: {full_address} to {location.latitude}, {location.longitude}")
                    coordinates.append((round(location.latitude, 6), round(location.longitude, 6)))#((location.latitude, location.longitude))
                                        
                else:
                    print(f"A non-existent address was added: {full_address}")
                    return None
            except Exception as e:
                print(f"Error geocoding address {full_address}: {e}")
                return None
        
        travel_data_populated = AddressConverter.populate_travel_data(coordinates, address_list)
        logger.info(travel_data_populated)
        
       
        coordinates_string = AddressConverter.coordinate_to_string(coordinates)
        logger.info(coordinates_string)
        return coordinates_string

    
    
    # @staticmethod
    # def address_to_coordinates_converter(address: GeopyInputData) -> List[float]:
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
    #     geolocator = Nominatim(user_agent=request)
    #     geocode = RateLimiter(geolocator.geocode,
    #                           min_delay_seconds=1,  max_retries=10)

    #     try:
    #         full_address = f"{address.address}, {address.house_number}, {
    #             address.city}, {address.district}, {address.zip_code}"
    #         location = geolocator.geocode(full_address)

    #         if location is not None:
    #             coordinates = [location.latitude, location.longitude]
    #             return coordinates
    #         else:
    #             logger.error(
    #                 f"A non-existent address was added: {full_address}")
    #     except Exception as e:
    #         logger.error(f"Error geocoding address {full_address}: {e}")
            
    
        
  
