from typing import List
from utils.tomtom_recalculation import TomTomRecalculation
from utils.tomtom_service import TomTom
from model.delivery import Delivery
from fastapi import FastAPI, APIRouter, status, UploadFile, HTTPException
from utils.preprocess_service import PreProcess
from utils.postprocess_service import PostProcess
from utils.message_trigger_service import MessageSending
from model.travel_data import TravelData
from model.response import Response
from model.device_message import DeliveryMessage
from controller.db.follow_track_db import FollowTrackDB
from utils.update_service import RouteUpdate
from loguru import logger
import json
from motor.motor_asyncio import AsyncIOMotorDatabase
from controller.db.db_setting import ROUTE_DBDependency

eta_api_router = APIRouter(tags=["Eta-To-Notification"])

app = FastAPI()


@eta_api_router.post("/upload_route_file/")
async def create_upload_file(file: UploadFile,
                             route_db: AsyncIOMotorDatabase = ROUTE_DBDependency) -> Response:
    delivery_list, date, trace_id = await PreProcess.digest_csv(file)
    coordinates, raw_travel_data = PreProcess.populate_travel_data(
        delivery_list)
    ordered_travel_data = TomTom.order_travel_data(
        coordinates)
    complete_travel_data = PostProcess.associate_address(
        raw_travel_data, ordered_travel_data)
    with open("./eta_to_notification_develop/zip_code.json") as cap_file:
        cap_delays = json.load(cap_file)
        # logger.info(cap_delays)
    delay_travel_data = PostProcess.update_eta(
        complete_travel_data, cap_delays)
    delay_travel_data.ginc = trace_id
    # logger.info(delay_travel_data)
    message_sending = MessageSending.check_time_and_send(delay_travel_data)
    save_response = await FollowTrackDB.add_new_object(route_db, delay_travel_data)
    # save_response = True
    if save_response:
        logger.info("trace saved in db")
        response = PostProcess.create_response(delay_travel_data)
        return response
    else:
        logger.info("error in store trace inside db")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"error in store trace inside db")


@eta_api_router.get("/get_route/")
async def get_route_object_by_ginc(ginc: str,
                                   route_db: AsyncIOMotorDatabase = ROUTE_DBDependency) -> TravelData:
    route = await FollowTrackDB.get_route_object(route_db, ginc)

    if route and route is not None:
        return route[0]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"route information not found.")


@eta_api_router.post("/eta/calculation", status_code=status.HTTP_201_CREATED)
async def eta_calculation(delivery_list: List[Delivery]) -> TravelData:
    """this is the api used for ETA calculation. It takes in input a list of addresses with a gsin and return a TravelData object with TomTom information and time delays 
    provided by every zip code"""

    coordinates, raw_travel_data = PreProcess.populate_travel_data(
        delivery_list)

    ordered_travel_data = TomTom.order_travel_data(
        coordinates)

    # logger.info(ordered_travel_data)

    complete_travel_data = PostProcess.associate_address(
        raw_travel_data, ordered_travel_data)

    # logger.info(complete_travel_data)

    with open("./eta_to_notification_develop/zip_code.json") as cap_file:
        cap_delays = json.load(cap_file)
        logger.info(cap_delays)

    delay_travel_data = PostProcess.update_eta(
        complete_travel_data, cap_delays)

    message_sending = MessageSending.check_time_and_send(delay_travel_data)

    return delay_travel_data


@eta_api_router.post("/route_update/", status_code=status.HTTP_201_CREATED)
async def eta_modification(update: DeliveryMessage,
                           route_db: AsyncIOMotorDatabase = ROUTE_DBDependency) -> Response:
    """this is the api used to trigger again the TomTom service when a delivery is made. It takes in input a DeliveryMessage object 
    and returns an updated Response Object"""

    old_travel_data = await FollowTrackDB.get_route_object(route_db, update.ginc)

    if not old_travel_data or old_travel_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"route information not found.")

    new_travel_data = RouteUpdate.update_route(old_travel_data, update)
    ordered_travel_data = TomTomRecalculation.order_travel_data(
        new_travel_data)
    # logger.info(f"the travel data of the api are {travel_data}")

    with open("./eta_to_notification_develop/zip_code.json") as cap_file:
        cap_delays = json.load(cap_file)
        logger.info(cap_delays)

    delay_travel_data = PostProcess.update_eta(ordered_travel_data, cap_delays)

    message_sending = MessageSending.check_time_and_send(delay_travel_data)
    ###########
    # save_response = await FollowTrackDB.add_new_object(route_db, delay_travel_data)
    ##########
    return delay_travel_data
