from typing import List, Tuple
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from model.input_data import InputData
from fastapi import APIRouter,HTTPException, status
from loguru import logger

class AddressConverter:
    
    @staticmethod
    def address_to_coordinates_converter(addresses: List[InputData]) -> List[Tuple[float, float]]:

        geolocator = Nominatim(user_agent = 'my_request')
        geocode = RateLimiter(geolocator.geocode,min_delay_seconds = 1)
        coordinates_list = []

        try:
            for data in addresses:
                location = geolocator.geocode(data.address)
                if location:
                    coordinates = (location.latitude, location.longitude)
                    coordinates_list.append(coordinates)
                else:
                    logger.warning(f"Could not geocode address: {data.address}")
        except Exception as ex:
            logger.error(f"An error occurred: {ex}")

        return coordinates_list

                        
# loc = ['torre di Pisa, Pisa', 'via Cisanello, Pisa', 'via san Michele degli Scalzi, Pisa', 'via Amerigo Vespucci, Pisa'] #bastano via e città 
# geolocator = Nominatim(user_agent="my_request")
# geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# for x in loc:
#     location = geolocator.geocode(x)
#     print(location.address)
#     print((location.latitude, location.longitude))