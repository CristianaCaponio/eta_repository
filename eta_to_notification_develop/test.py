from typing import List
from geopy.geocoders import Nominatim
#from model.input_data import InputData
from geopy.extra.rate_limiter import RateLimiter
from loguru import logger

'''file to make test before building a new container'''

loc = ['Via Lioce Bari', 'Torino porta nuova' ] #bastano via e città 
geolocator = Nominatim(user_agent="my_request")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries = 0)

for x in loc:
    coordinates = geolocator.geocode(x)
    print("-------------------------------------")
    print(loc)
    print((coordinates.latitude, coordinates.longitude))
    print("-------------------------------------")        
    
    
     
    addresses = geolocator.reverse((coordinates.latitude, coordinates.longitude))
    print(coordinates)
    print(addresses)
    
   