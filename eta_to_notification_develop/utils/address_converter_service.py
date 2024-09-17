from typing import List
import os
from io import StringIO
from geopy.geocoders import Nominatim
from model.geopy_input_data import GeopyInputData
from geopy.extra.rate_limiter import RateLimiter
from loguru import logger


class AddressConverter:
    
    
    @staticmethod
    def address_to_coordinates_converter(addresses_list: List[GeopyInputData]) -> str:
        
        
        """         
        Converts a list of addresses into a single string of geographical coordinates.

        Parameters
        ----------
        addresses_list : List[GeopyInputData]
            A list of GeopyInputData objects containing address details.

        Returns
        -------
        str
            A string of geographical coordinates in the format 'lat1,lon1:lat2,lon2:...'.

        """
        request = os.environ.get("USER_AGENT","my_agent") 
        logger.info(request)       
        geolocator = Nominatim(user_agent = request)
        geocode = RateLimiter(geolocator.geocode,min_delay_seconds = 1,  max_retries = 0)
        coordinates_list = []
                
        for data in addresses_list:
            
            try:
                full_address = f"{data.address}, {data.house_number}, {data.city}, {data.district}, {data.zip_code}"
                location = geolocator.geocode(full_address)

                if location is not None:
                    coordinates = (location.latitude, location.longitude)
                    coordinates_list.append(coordinates)
                else:
                    logger.error(f"A non-existent address was added: {full_address}")
            except Exception as e:
                logger.error(f"Error geocoding address {full_address}: {e}")
        
        if not coordinates_list:
            raise ValueError("No valid coordinates found.")
    
        full_coordinates_list = StringIO()
        full_coordinates_list.write(f"{coordinates_list[0][0]},{coordinates_list[0][1]}")
        
        for single_coordinate in coordinates_list[1:]:
            full_coordinates_list.write(f":{single_coordinate[0]},{single_coordinate[1]}")

                    
        return full_coordinates_list.getvalue()
