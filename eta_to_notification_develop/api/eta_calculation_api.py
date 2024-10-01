from typing import List
from utils.tomtom_service import TomTom
from model.delivery import Delivery
from fastapi import FastAPI, APIRouter, HTTPException, status
from utils.preprocess_service import PreProcess
from utils.postprocess_service import PostProcess
from model.db_models import TravelData
from loguru import logger
import json
from database.settings import db_connect, db_disconnect


eta_api_router = APIRouter(tags=["Eta-To-Notification"])

app = FastAPI()


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

    return delay_travel_data
