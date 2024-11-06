from geopy import distance
from model.travel_data import TravelData
from loguru import logger
from datetime import datetime, timedelta
from typing import Dict


class PostProcess():
    """in this class the coordinates and addresses of TravelData are matched with the new order given by TomTom. the ETAs are updated with the delays given by
        every zip code and, together with every delay, the departure and arrival time are also updated """

    @staticmethod
    def associate_address(raw_travel_data: TravelData, ordered_travel_data: TravelData) -> TravelData:
        
        """ this function associates the addresses from raw_travel_data to ordered_travel_data based on the geographical proximity of the stops.
            It calculates the distance between each stop's coordinates (departure and arrival) in both raw and ordered travel data, and matches the closest ones. 
            Then, it updates the addresses and gsin for the corresponding stops in ordered_travel_data and updates the summary with the first stop's departure address 
            and the last stop's arrival address."""  
           
        for stop in raw_travel_data.stops:
            departure_latitude = stop.departureLatitude
            departure_longitude = stop.departureLongitude
            arrival_latitude = stop.arrivalLatitude
            arrival_longitude = stop.arrivalLongitude
            dep_dist_list = []
            arr_dist_list = []
            for i in range(len(ordered_travel_data.stops)):

                ordered_departure_latitude = ordered_travel_data.stops[i].departureLatitude
                ordered_departure_longitude = ordered_travel_data.stops[i].departureLongitude
                ordered_arrival_latitude = ordered_travel_data.stops[i].arrivalLatitude
                ordered_arrival_longitude = ordered_travel_data.stops[i].arrivalLongitude

                dep_dist = distance.distance((departure_latitude, departure_longitude), (
                    ordered_departure_latitude, ordered_departure_longitude)).m

                # logger.info(f"departure distance:{dep_dist}")
                dep_dist_list.append(dep_dist)

                arr_dist = distance.distance(
                    (arrival_latitude, arrival_longitude), (ordered_arrival_latitude, ordered_arrival_longitude)).m
                # logger.info(f"arrival distance:{arr_dist}")
                arr_dist_list.append(arr_dist)

            departure_min_index = dep_dist_list.index(min(dep_dist_list))
            arrival_min_index = arr_dist_list.index(min(arr_dist_list))

            ordered_travel_data.stops[departure_min_index].departureAddress = stop.departureAddress
            ordered_travel_data.stops[arrival_min_index].arrivalAddress = stop.arrivalAddress
            ordered_travel_data.stops[arrival_min_index].gsin = stop.gsin
            ordered_travel_data.summary.startAddress = ordered_travel_data.stops[
                0].departureAddress
            ordered_travel_data.summary.endAddress = ordered_travel_data.stops[-1].arrivalAddress

        return ordered_travel_data
    
    @staticmethod
    def add_delay_to_time(time_obj: datetime, delay_in_seconds: int) -> datetime:
        """This method takes a datetime object and a delay in seconds. It applies the delay using timedelta, and 
        returns the updated time as an ISO 8601 string."""        
        
        new_time_obj = time_obj + timedelta(seconds=delay_in_seconds)        
        
        return new_time_obj

    # @staticmethod
    # def add_delay_to_time(time_str: str, delay_in_seconds: int) -> str:
        """This method takes an ISO-format time string and a delay in seconds. It converts the time string to a datetime object,
            applies the delay using timedelta, and returns the updated time as an ISO-format string."""
        
        
        # time_format = "%Y-%m-%dT%H:%M:%S%z"
        # time_obj = datetime.strptime(time_str, time_format)
        # new_time_obj = time_obj + timedelta(seconds=delay_in_seconds)
        # formatted_time_str = new_time_obj.strftime("%Y-%m-%dT%H:%M:%S%z")        
        # formatted_time_with_colon = formatted_time_str[:-2] + ":" + formatted_time_str[-2:]
        
        # return formatted_time_with_colon
        #return new_time_obj.strptime(time_format)

    @staticmethod
    def update_eta(travel_data: TravelData, zip_code_delay: Dict[str, int]) -> TravelData:
        """this function updates ETAs with the delay given by every zip code"""

        if not travel_data.stops:
            logger.info("No stops available in travel_data. Skipping ETA update.")
            return travel_data

        for i in range(len(travel_data.stops)-1):
            zip_code = travel_data.stops[i+1].departureAddress.zip_code
            delay = zip_code_delay[f"{zip_code}"]
            for y in range(i+1, len(travel_data.stops)):
                dep_time = travel_data.stops[y].departureTime
                arr_time = travel_data.stops[y].arrivalTime
                travel_data.stops[y].departureTime = PostProcess.add_delay_to_time(
                    dep_time, delay)
                travel_data.stops[y].arrivalTime = PostProcess.add_delay_to_time(
                    arr_time, delay)
        travel_data.summary.arrivalTime = travel_data.stops[-1].arrivalTime
        return travel_data
