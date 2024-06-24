from typing import List, Tuple
from geopy.geocoders import Nominatim
from model.geopy_input_data import GeopyInputData
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderServiceError
from loguru import logger

class AddressConverter:
    
    @staticmethod
    def address_to_coordinates_converter(addresses_list: List[(GeopyInputData)]) -> List[tuple]:
        
        """
        function to convert addresses to geographical coordinates

        Parameters
        ----------
        list of GeopyInputData objects converted into a string
        """

        geolocator = Nominatim(user_agent = 'my_request')
        geocode = RateLimiter(geolocator.geocode,min_delay_seconds = 1,  max_retries = 0)
        coordinates_list = []
        
        
        for data in addresses_list:
            
            full_address = f"{data.address}, {data.house_number}, {data.city}"
            location = geolocator.geocode(full_address)   
                  
            if location is not None:       
                coordinates = (location.latitude, location.longitude)
                coordinates_list.append(coordinates)
                
            else:           
                logger.error(f"a non existent address was added : {full_address}")

        return coordinates_list

    @staticmethod                        
    def coordinates_to_address_converter(coordinates_list: List[Tuple[float, float]])-> List[str]:
        """
        function for reversing geofence

        Parameters
        ----------
        list of float tuple coming from coordinates converted by the function address_to_coordinates_converter
        """
    
        geolocator = Nominatim(user_agent = 'my_request')
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds = 1,  max_retries = 0)
        addresses_list = []
    
        for coordinates in coordinates_list:            
            
            location = geolocator.reverse(f"{coordinates[0]}, {coordinates[1]}")            
                
            if location is not None:    
               
                address =  location.address
                addresses_list.append(address)
                
            else:           
                logger.error(f"an error occurred : {coordinates}")

        return addresses_list
    

