from typing import List
import os
from db_settings import db_connect, db_disconnect
#from db_models import Location
from io import StringIO
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from db_models import TravelData


class AddressConverter:
    
    # @staticmethod
    # def find_mongo_object() -> List[dict]:
    #     result = Location.objects(personal_id=1)
    #     addresses = []
        
    #     if result:
    #         for location in result:
    #             # Add departure address
    #             if location.departure_address:
    #                 addresses.append({
    #                     'type': 'departure',
    #                     'address': location.departure_address.address,
    #                     'latitude': location.departure_address.latitude,
    #                     'longitude': location.departure_address.longitude,
    #                     'id': str(location.id)
    #                 })
                
    #             # Add stop addresses
    #             if location.stops:
    #                 for stop in location.stops:
    #                     addresses.append({
    #                         'type': 'stop',
    #                         'address': stop.address,
    #                         'latitude': stop.latitude,
    #                         'longitude': stop.longitude,
    #                         'id': str(location.id)
    #                     })
    #     else:
    #         print("No results found.")
        
    #     return addresses

    # @staticmethod
    # def address_to_coordinates_converter() -> None:      
    #     addresses_list = AddressConverter.find_mongo_object()
    #     request = os.environ.get("USER_AGENT", "my_agent") 
    #     print(request)       
    #     geolocator = Nominatim(user_agent=request)
    #     geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=0)
        
    #     for address_info in addresses_list:
    #         data = address_info['address']
    #         location_id = address_info['id']
    #         address_type = address_info['type']
            
    #         # Check if the address already has coordinates
    #         if address_info['latitude'] is not None and address_info['longitude'] is not None:
    #             print(f"Address {data} already has coordinates.")
    #             continue
            
    #         try:
    #             location = geolocator.geocode(data)

    #             if location:
    #                 coordinates = (location.latitude, location.longitude)
                    
    #                 # Update MongoDB document
    #                 if address_type == 'departure':
    #                     Location.objects(id=location_id).update(
    #                         set__departure_address__latitude=coordinates[0],
    #                         set__departure_address__longitude=coordinates[1]
    #                     )
    #                 elif address_type == 'stop':
    #                     Location.objects(id=location_id, stops__address=data).update(
    #                         set__stops__S__latitude=coordinates[0],
    #                         set__stops__S__longitude=coordinates[1]
    #                     )
    #             else:
    #                 print(f"A non-existent address was added: {data}")
    #         except Exception as e:
    #             print(f"Error geocoding address {data}: {e}")
        
    #     print("Geocoding and updating complete.")

    @staticmethod
    def collect_coordinates(travel_data: TravelData) -> str:
        # Collect all the coordinates and format them as a string
       
        all_coordinates = travel_data.stops
        coordinates_list = []
        
        for coordinate in all_coordinates:
            if coordinate.departureLatitude  is not None and coordinate.departureLongitude is not None:
               coordinates_list.append((coordinate.departureLatitude,coordinate.departureLongitude)) 

            else:
                return "no departure coordinates found"
            
            if coordinate.arrivalLatitude  is not None and coordinate.arrivalLongitude is not None:
               coordinates_list.append((coordinate.arrivalLatitude,coordinate.arrivalLongitude)) 


            else:
                return "no arrival coordinates found"
        
        full_coordinates_list = StringIO()
        full_coordinates_list.write(f"{coordinates_list[0][0]},{coordinates_list[0][1]}")
        
        for single_coordinate in coordinates_list[1:]:
            full_coordinates_list.write(f":{single_coordinate[0]},{single_coordinate[1]}")
        
        return full_coordinates_list.getvalue()
    
        