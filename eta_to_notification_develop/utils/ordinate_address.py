from geopy import distance
from model.db_models import TravelData
from loguru import logger


def ordinate_address(raw_travel_data: TravelData, ordered_travel_data: TravelData) -> TravelData:
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
        ordered_travel_data.summary.startAddress = ordered_travel_data.stops[0].departureAddress
        ordered_travel_data.summary.endAddress = ordered_travel_data.stops[-1].departureAddress

    return ordered_travel_data
