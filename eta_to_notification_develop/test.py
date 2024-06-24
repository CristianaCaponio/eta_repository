from typing import List
from geopy.geocoders import Nominatim
#from model.input_data import InputData
from geopy.extra.rate_limiter import RateLimiter
from loguru import logger

loc = ['ndsknsdonpsdnmondsoinfpidodsnoinfopioi'] #bastano via e città 
geolocator = Nominatim(user_agent="my_request")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

for x in loc:
    location = geolocator.geocode(x)
    print("-------------------------------------")
    print(location)
    print((location.latitude, location.longitude, location.raw))
    print("-------------------------------------")