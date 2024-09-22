from typing import List
from utils.eta_calculation_service import TomTomParams
from model.geopy_input_data import GeopyInputData
from fastapi import FastAPI, APIRouter, HTTPException, status
from utils.address_converter_service import AddressConverter
from model.db_models import TravelData
from loguru import logger
import json
from database.settings import db_connect, db_disconnect


eta_api_router = APIRouter(tags=["Eta-To-Notification"])

app = FastAPI()

# Established connection to MongoDB when app starts


# @app.on_event("startup")
# def startup_db():
#     db_connect()


# Included router
#app.include_router(eta_api_router)


@eta_api_router.post("/eta/calculation", status_code=status.HTTP_201_CREATED)
def eta_calculation(input_data: List[GeopyInputData]) -> TravelData:
    
        
    tomtom_call = TomTomParams.request_params(input_data)
    logger.info(input_data)
    
    travel_data_population = TomTomParams.tomtom_request(tomtom_call)
    logger.info(tomtom_call)
    
    return travel_data_population
#     try:
#         # # Taking delays from JSON file
#         # with open("./eta_to_notification_develop/zip_code.json") as cap_file:
#         #     cap_delays = json.load(cap_file)
#         #     logger.info(cap_delays)

#         # request_params = TomTomParams.request_params(input_data)
#         # logger.info(request_params)

#         # initial_response = TomTomParams.tomtom_request(
#         #     request_params, input_data)

#         # final_response = TomTomParams.calculate_definitive_eta(
#         #     initial_response, cap_delays)

#         # logger.info(final_response)

#         # transforming the json object into a dictionary
#         # final_response_dict = final_response.dict()

#         if input_data.summary.startLatitude is None:

#             start_coordinates = AddressConverter.address_to_coordinates_converter(
#                 input_data.summary.startAddress)
#             input_data.summary.startLatitude = start_coordinates[0]
#             input_data.summary.startLongitude = start_coordinates[1]

#         if input_data.summary.endLatitude is None:
#             end_coordinates = AddressConverter.address_to_coordinates_converter(
#                 input_data.summary.endAddress)
#             input_data.summary.endLatitude = end_coordinates[0]
#             input_data.summary.endLongitude = end_coordinates[1]

#         for stop in input_data.stops:
#             if stop.departureLatitude is None:
#                 departure_coordinates = AddressConverter.address_to_coordinates_converter(
#                     stop.departureAddress)
#                 stop.departureLatitude = departure_coordinates[0]
#                 stop.departureLongitude = departure_coordinates[1]
#             if stop.arrivalLatitude is None:
#                 arrival_coordinates = AddressConverter.address_to_coordinates_converter(
#                     stop.arrivalAddress)
#                 stop.arrivalLatitude = arrival_coordinates[0]
#                 stop.arrivalLongitude = arrival_coordinates[1]

#         logger.info(input_data)

#     except Exception as ex:
#         logger.error(f"An error occurred during ETA calculation: {ex}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


# @app.on_event("shutdown")
# def shutdown_db():
#     db_disconnect()
