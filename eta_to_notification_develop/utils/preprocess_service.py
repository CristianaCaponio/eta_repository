from typing import List, Tuple
import os
from model.travel_data import StopSummary, Summary, TravelData
from model.delivery import Delivery
from geopy.geocoders import ArcGIS
from model.delivery import Delivery, Address
from geopy.extra.rate_limiter import RateLimiter
from loguru import logger
import csv
import io


class PreProcess():
    """
    The `PreProcess` class provides functionality to prepare and preprocess delivery data, including:
    - Converting delivery addresses to geographical coordinates.
    - Populating `TravelData` objects with necessary details for a delivery route.
    - Parsing CSV files containing delivery information.

    The class is primarily responsible for transforming input delivery data into the appropriate format 
    required for routing and travel calculations.

    Key Responsibilities:
    1. **Coordinate Conversion**: Convert a list of delivery addresses into geographic coordinates (latitude, longitude).
    2. **Travel Data Population**: Populate a `TravelData` object with route summaries and stop details derived from delivery addresses.
    3. **CSV Parsing**: Parse CSV files containing delivery information, converting rows into structured `Delivery` objects with associated metadata.
    """

    @staticmethod
    def populate_travel_data(delivery_list: List[Delivery]) -> Tuple[List[str], TravelData]:
        """
        Converts a list of `Delivery` objects into `TravelData`, including route summary and stops.

        This method:
        1. Converts the addresses from the `Delivery` objects into geographic coordinates.
        2. Constructs a summary (start and end coordinates) for the travel data.
        3. Creates `StopSummary` objects for each leg of the journey (from one delivery to the next).

        Args:
            delivery_list (List[Delivery]): A list of `Delivery` objects containing delivery details.

        Returns:
            Tuple[List[str], TravelData]: A tuple consisting of:
                - A list of coordinates (latitude, longitude).
                - A `TravelData` object with summary and stops information.

        Raises:
            ValueError: If the `delivery_list` does not contain at least two addresses for start and end.
        """

        coordinates = PreProcess.address_to_coordinates_converter(
            delivery_list)

        if len(coordinates) < 2:
            raise ValueError(
                "This list must contain at least two addresses: one for the departure and one another for the arrival.")

        new_summary = Summary(
            startLatitude=coordinates[0][0],
            startLongitude=coordinates[0][1],
            endLatitude=coordinates[-1][0],
            endLongitude=coordinates[-1][1],
            startAddress=delivery_list[0].address,
            endAddress=delivery_list[-1].address
        )
        new_stops = []
        for i in range(len(delivery_list) - 1):

            address_stop = StopSummary(
                gsin=delivery_list[i+1].gsin,
                departureLatitude=coordinates[i][0],
                departureLongitude=coordinates[i][1],
                arrivalLatitude=coordinates[i + 1][0],
                arrivalLongitude=coordinates[i + 1][1],
                departureAddress=delivery_list[i].address,
                arrivalAddress=delivery_list[i + 1].address
            )
            new_stops.append(address_stop)

        travel_data = TravelData(
            personal_id="temporary_ID",
            ginc="some_ginc",
            summary=new_summary,
            stops=new_stops,
            delivered_stops=[]
        )
        # logger.info(f"travel data in preprocess_service: {travel_data}")
        return coordinates, travel_data

    @staticmethod
    def address_to_coordinates_converter(delivery_list: List[Delivery]) -> List[str]:
        """
        Converts delivery addresses into geographic coordinates (latitude, longitude) using geocoding.

        This method:
        1. Uses the `ArcGIS` geocoder to look up the coordinates for each delivery address.
        2. Returns the list of coordinates as tuples of latitude and longitude.

        Args:
            delivery_list (List[Delivery]): A list of `Delivery` objects containing address details.

        Returns:
            List[str]: A list of coordinates (latitude, longitude) for each address in the delivery list.

        Raises:
            ValueError: If any address cannot be geocoded.
        """

        request = os.environ.get("USER_AGENT", "my_agent")
        geolocator = ArcGIS(user_agent=request)
        geocode = RateLimiter(geolocator.geocode,
                              min_delay_seconds=1, max_retries=10)

        coordinates = []

        for delivery in delivery_list:
            add = delivery.address
            full_address = f"{add.address}, {add.house_number}, {add.city}, {add.district}, {add.zip_code}"  # nopep8
            try:
                location = geocode(full_address, exactly_one=True)
                if location:
                    coordinates.append((f"{location.latitude}", f"{location.longitude}"))  # nopep8
                    logger.info(coordinates)

                else:
                    logger.info(
                        f"A non-existent address was added: {full_address}")
                    return ""
            except Exception as e:
                logger.error(f"Error geocoding address {full_address}: {e}")
                return ""
        # logger.info(coordinates)
        return coordinates

    @staticmethod
    async def digest_csv(route_file) -> Tuple[List[Delivery], str, str]:
        """
        Parses a CSV file containing delivery data and returns a list of `Delivery` objects, along with
        additional metadata such as date and trace ID.

        This method:
        1. Reads the CSV file containing delivery information.
        2. Creates a list of `Delivery` objects from the parsed CSV content.
        3. Extracts the date and trace ID from the file name.

        Args:
            route_file: The CSV file containing delivery data.

        Returns:
            Tuple[List[Delivery], str, str]: A tuple consisting of:
                - A list of `Delivery` objects created from the CSV file.
                - The date extracted from the file name.
                - The trace ID extracted from the file name.
        """

        delivery_list = []
        result = []
        file_name = route_file.filename
        date = file_name[0:10]
        trace_id = file_name[11:16]

        with route_file.file as f:
            csv_content = csv.DictReader(
                io.TextIOWrapper(f, encoding='utf_8'), ('id', 'indirizzo', 'città', 'provincia', 'numero civico', 'cap', 'telefono'))

            for row in csv_content:
                result.append(row)

        result = result[1:]

        for item in result:
            logger.info(item)
            gsin = item['gsin']
            del item['gsin']

            address = Address(**{
                'address': item['address'],
                'city': item['city'],
                'district': item['district'],
                'house_number': item['house_number'],
                'zip_code': item['zip_code'],
                'telephone_number': item['telephone_number']
            })

            item = Delivery(**{
                'gsin': gsin,
                'address': address

            })
            delivery_list.append(item)

        logger.info(input)
        return delivery_list, date, trace_id
