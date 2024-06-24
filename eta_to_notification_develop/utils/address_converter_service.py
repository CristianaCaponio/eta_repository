from typing import List, Tuple
from geopy.geocoders import Nominatim
from model.geopy_input_data import GeopyInputData
from geopy.extra.rate_limiter import RateLimiter
from loguru import logger

class AddressConverter:
    
    @staticmethod
    def address_to_coordinates_converter(addresses_list: List[(GeopyInputData)]):

        geolocator = Nominatim(user_agent = 'my_request')
        geocode = RateLimiter(geolocator.geocode,min_delay_seconds = 1)
        coordinates_list = []
        
        
        for data in addresses_list:
            
            full_address = f"{data.address}, {data.city}, {data.postal_code}"
            location = geolocator.geocode(full_address)   
                  
            if location is not None:       
                coordinates = (location.latitude, location.longitude)
                coordinates_list.append(coordinates)
                
            else:           
                logger.error(f"a non existent address was added : {full_address}")

        return coordinates_list

                        
# loc = ['torre di Pisa, Pisa', 'via Cisanello, Pisa', 'via san Michele degli Scalzi, Pisa', 'via Amerigo Vespucci, Pisa'] #bastano via e città 
# geolocator = Nominatim(user_agent="my_request")
# geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# for x in loc:
#     location = geolocator.geocode(x)
#     print(location.address)
#     print((location.latitude, location.longitude))