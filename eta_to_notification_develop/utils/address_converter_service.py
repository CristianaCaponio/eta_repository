from typing import List
import os
#from dotenv import load_dotenv
from io import StringIO
from geopy.geocoders import Nominatim
from model.geopy_input_data import GeopyInputData
from geopy.extra.rate_limiter import RateLimiter
from loguru import logger


class AddressConverter:
    
    
    @staticmethod
    def address_to_coordinates_converter(addresses_list: List[GeopyInputData]) -> str:
        
        
        """
        this function converts addresses into geographical coordinates and
        creates a single string with all coordinates to mach TomTom's parameter
        'location' that is a string with the following structure
        52.50931,13.42936:52.50274,13.43872:52.50945,13.42988 

        Parameters
        ----------
        list of GeopyInputData objects converted into a string
        """
        #load_dotenv()
        request = os.environ.get("USER_AGENT","my_agent") 
        logger.info(request)       
        geolocator = Nominatim(user_agent = request)
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

        
        if not coordinates_list:
            raise ValueError("No valid coordinates found.")
    
        full_coordinates_list = StringIO()
        full_coordinates_list.write(f"{coordinates_list[0][0]},{coordinates_list[0][1]}")
        
        for single_coordinate in coordinates_list[1:]:
            full_coordinates_list.write(f":{single_coordinate[0]},{single_coordinate[1]}")

                    
        return full_coordinates_list.getvalue()
   
