from typing import List
from utils.tomtom_recalculation import TomTomRecalculation
from utils.tomtom_service import TomTom
from model.delivery import Delivery
from fastapi import FastAPI, APIRouter, status, UploadFile, HTTPException
from utils.preprocess_service import PreProcess
from utils.postprocess_service import PostProcess
from model.travel_data import TravelData
from controller.db.eta_calculator_db import EtaDb
from model.device_message import DeliveryMessage
from model.response import Response

from loguru import logger
import json
import os
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi.responses import StreamingResponse
from controller.db.db_setting import ROUTE_DBDependency
import datetime

eta_api_router = APIRouter(tags=["Eta-Calculator"])

app = FastAPI()


@eta_api_router.post("/upload_route_file/")
async def create_upload_file(file: UploadFile,
                             route_db: AsyncIOMotorDatabase = ROUTE_DBDependency) -> StreamingResponse:
    """
    Handles the upload of a CSV file containing route details, processes the data,
    and stores the resulting delivery route in the database.

    Steps:
    1. **Extract delivery details**: Reads the uploaded CSV file and extracts relevant delivery information.
    2. **Optimal route calculation**: Sends the extracted data to TomTom to calculate the optimal delivery sequence.
    3. **Address association and ETA adjustment**: Links addresses to deliveries and updates the estimated times of arrival (ETAs),
       accounting for potential ZIP code-specific delays.
    4. **Send notifications**: Sends initial SMS notifications to recipients based on the processed delivery schedule.
    5. **Save the route**: Stores the processed route and its details in the database for further use.

    Returns:
        StreamingResponse: A CSV file containing the processed delivery route and its details.

    Raises:
        HTTPException:
            - 409 Conflict: If a route with the same unique identifier (trace ID) already exists in the database.
            - 500 Internal Server Error: If there is an error saving the route in the database.
    """

    delivery_list, date, trace_id = await PreProcess.digest_csv(file)
    logger.info(f'il trace_id è {trace_id}')

    route = await EtaDb.get_route_object(route_db, trace_id)

    if route or route is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"route with the same ginc is alredy registered in db.")
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
        complete_travel_data, cap_delays, default_delay=int(os.getenv('DEFAULT_DELAY', 100)))
    delay_travel_data.ginc = trace_id
    # logger.info(delay_travel_data)

    save_response = await EtaDb.add_new_object(route_db, delay_travel_data)

    if save_response:
        logger.info("trace saved in db")
        csv_file = PostProcess.generate_csv(delay_travel_data)
        response = StreamingResponse(
            csv_file,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=route.csv"}
        )
        return response
    else:
        logger.info("error in store trace inside db")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"error in store trace inside db")


@eta_api_router.get("/get_route/")
async def get_route_object_by_ginc(ginc: str,
                                   route_db: AsyncIOMotorDatabase = ROUTE_DBDependency) -> TravelData:
    """
    Retrieve a route from the database using its unique identifier (ginc).

    Args:
        ginc (str): The unique identifier for the route.

    Returns:
        TravelData: The route information if found.

    Raises:
        HTTPException: If the route is not found (404).
    """

    route = await EtaDb.get_route_object(route_db, ginc)

    if route and route is not None:
        return route[0]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"route information not found.")


@eta_api_router.post("/route_delete/", status_code=status.HTTP_200_OK)
async def delete_trace(ginc: str,
                       route_db: AsyncIOMotorDatabase = ROUTE_DBDependency):
    """
    Delete a route from the database using its unique identifier (ginc).

    Args:
        ginc (str): The unique identifier for the route.
        route_db (AsyncIOMotorDatabase): The database connection instance.

    Returns:
        str: Confirmation message on successful deletion.

    Raises:
        HTTPException: If an error occurs during the deletion process (500).
    """

    delete = await EtaDb.delete_route_object(route_db, ginc)

    if delete:
        logger.info(f"object with ginc:{ginc} deleted")
        return "deleted"
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="error during the deleting process")


@eta_api_router.post("/route_update/", status_code=status.HTTP_201_CREATED)
async def route_update(update: DeliveryMessage,
                       route_db: AsyncIOMotorDatabase = ROUTE_DBDependency) -> Response:
    """
    Update the delivery status of a specific order and recalculate route details.

    Steps:
    1. Mark the specified delivery as delivered (delivered=true).
    2. Stores the route marked as delivered=true inside the list travel_data.delivered _tops
    3. Recalculate the route using TomTom's services(it doesn't calculate the optimal delivery sequence).
    4. Adjust ETA based on ZIP code delays.
    5. Send SMS notifications for both the completed delivery and the next scheduled delivery.
    6. Save the updated route in the database.

    Args:
        update (DeliveryMessage): The delivery update information (ginc, gsin and delivery_time).

    Returns:
        Response: The updated route response.

    Raises:
        HTTPException: If the route is not found (404) or if an error occurs during saving (500).
    """

    list_travel_data = await EtaDb.get_route_object(route_db, update.ginc)
    old_travel_data = list_travel_data[0]

    if not old_travel_data or old_travel_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"route information not found.")

    new_travel_data = TomTomRecalculation.update_route(old_travel_data, update)
    # logger.info(f"inside eta_calculation_api and travel data after update_route are are{new_travel_data}")
    ordered_travel_data = TomTomRecalculation.order_travel_data(
        new_travel_data)
    # logger.info(f"inside eta_calculation_api and travel data after order_travel_data are {new_travel_data}")
    with open("./eta_to_notification_develop/zip_code.json") as cap_file:
        cap_delays = json.load(cap_file)
        logger.info(cap_delays)

    delay_travel_data = PostProcess.update_eta(
        ordered_travel_data, cap_delays, default_delay=int(os.getenv('DEFAULT_DELAY', 100)))
    # logger.info(f"travel_data delays after il Postprocess.update_eta are {delay_travel_data}")

    ###########
    save_response = await EtaDb.update_route_object(route_db, delay_travel_data)
    if save_response:
        logger.info("trace updated in db")
        response = PostProcess.create_response(delay_travel_data)
        return response
    else:
        logger.info("error in store trace inside db")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"error in store trace inside db")


