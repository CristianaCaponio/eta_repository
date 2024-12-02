from model.travel_data import TravelData
from model.tracker_update import TrackerUpdate
from geopy import distance
import time
from loguru import logger
import datetime
from model.device_message import DeliveryMessage
from utils.tomtom_recalculation import TomTomRecalculation
from utils.message_trigger_service import MessageSending
from utils.postprocess_service import PostProcess
import json
import os
from controller.db.follow_track_db import FollowTrackDB
from controller.db.db_setting import ROUTE_DBDependency


class TrackerUpdate():

    @staticmethod
    async def is_arrived(tracker_update: TrackerUpdate) -> bool:

        date = datetime.datetime.now().strftime("%Y_%m_%d")
        trace = await FollowTrackDB.get_route_object_by_date(ROUTE_DBDependency, date)

        tracker_coordinates = (tracker_update.lat, tracker_update.long)
        # eta_unix_time = time.mktime()

        for stop in trace.stops:
            if not stop.delivered:
                stop_coordinates = (stop.arrivalLatitude,
                                    stop.arrivalLongitude)
                # eta_unix_time = time.mktime(stop.arrivalTime.timetuple())
                dis = distance.distance(
                    tracker_coordinates, stop_coordinates).m
                if dis < 10:
                    upper_range = stop.arrivalTime + datetime.timedelta(0, 600)
                    lower_range = stop.arrivalTime - datetime.timedelta(0, 600)
                    if lower_range <= tracker_update.time <= upper_range:
                        logger.info("delivery proof ok")

                        update = DeliveryMessage(
                            ginc=trace.ginc,
                            gsin=stop.gsin,
                            delivery_time=tracker_update.time
                        )

                        new_travel_data = TomTomRecalculation.update_route(
                            trace, update)
                        ordered_travel_data = TomTomRecalculation.order_travel_data(
                            new_travel_data)

                        with open("./eta_to_notification_develop/zip_code.json") as cap_file:
                            cap_delays = json.load(cap_file)
                            logger.info(cap_delays)

                        delay_travel_data = PostProcess.update_eta(
                            ordered_travel_data, cap_delays, default_delay=int(os.getenv('DEFAULT_DELAY', 100)))

                        stop = MessageSending.delivery_occurred_message(stop)
                        logger.info(trace)

                        save_response = await FollowTrackDB.update_route_object(ROUTE_DBDependency, delay_travel_data)
                        if save_response:
                            logger.info("trace updated in db")
                            return True
                        else:
                            logger.info("error in store trace inside db")
                            return False

        return False
