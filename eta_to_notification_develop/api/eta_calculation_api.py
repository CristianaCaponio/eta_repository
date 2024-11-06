from typing import List
from utils.tomtom_recalculation import TomTomRecalculation
from utils.tomtom_service import TomTom
from model.delivery import Delivery
from fastapi import FastAPI, APIRouter, status, UploadFile
from utils.preprocess_service import PreProcess
from utils.postprocess_service import PostProcess
from utils.message_trigger_service import MessageSending
from model.travel_data import TravelData
from loguru import logger
import json


eta_api_router = APIRouter(tags=["Eta-To-Notification"])

app = FastAPI()


@eta_api_router.post("/eta/upload_route_file/")
async def create_upload_file(file: UploadFile):
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
    return delay_travel_data


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


@eta_api_router.post("/eta/modification", status_code=status.HTTP_201_CREATED)
async def eta_modification(travel_data: TravelData) -> TravelData:
    """this is the api used to trigger again the TomTom service when a delivery is made. It takes in input a TravelData object 
    and returns an updated Trabel Data Object"""

    ordered_travel_data = TomTomRecalculation.order_travel_data(travel_data)
    # logger.info(f"the travel data of the api are {travel_data}")

    with open("./eta_to_notification_develop/zip_code.json") as cap_file:
        cap_delays = json.load(cap_file)
        logger.info(cap_delays)

    delay_travel_data = PostProcess.update_eta(travel_data, cap_delays)

    message_sending = MessageSending.check_time_and_send(delay_travel_data)

    return delay_travel_data
