from typing import List
import os
from io import StringIO
from geopy.geocoders import Nominatim
from model.geopy_input_data import GeopyInputData
from geopy.extra.rate_limiter import RateLimiter
from loguru import logger


class AddressConverter:

    @staticmethod
    def address_to_coordinates_converter(address: GeopyInputData) -> List[float]:
        """         
        Converts a list of addresses into a single string of geographical coordinates.

        Parameters
        ----------
        address: GeopyInputData
            A GeopyInputData objects containing address details.

        Returns
        -------
        str
            A list with Latitude and Longitude

        """
        request = os.environ.get("USER_AGENT", "my_agent")
        logger.info(request)
        geolocator = Nominatim(user_agent=request)
        geocode = RateLimiter(geolocator.geocode,
                              min_delay_seconds=1,  max_retries=10)

        try:
            full_address = f"{address.address}, {address.house_number}, {
                address.city}, {address.district}, {address.zip_code}"
            location = geolocator.geocode(full_address)

            if location is not None:
                coordinates = [location.latitude, location.longitude]
                return coordinates
            else:
                logger.error(
                    f"A non-existent address was added: {full_address}")
        except Exception as e:
            logger.error(f"Error geocoding address {full_address}: {e}")

        # full_coordinates_list = StringIO()
        # full_coordinates_list.write(f"{coordinates_list[0][0]},{
        #                             coordinates_list[0][1]}")

        # for single_coordinate in coordinates_list[1:]:
        #     full_coordinates_list.write(f":{single_coordinate[0]},{
        #                                 single_coordinate[1]}")

        # return full_coordinates_list.getvalue()
