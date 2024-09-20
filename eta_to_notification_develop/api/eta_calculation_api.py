from fastapi import FastAPI, APIRouter, HTTPException, status
from model.input_data import InputData
from utils.eta_calculation_service import TomTomParams
from model.db_models import TravelData
from loguru import logger
import json
from database.json_model import JsonCollectionTest
from database.settings import db_connect, db_disconnect


eta_api_router = APIRouter(tags=["Eta-To-Notification"])

app = FastAPI()

# Established connection to MongoDB when app starts


@app.on_event("startup")
def startup_db():
    db_connect()


# Included router
app.include_router(eta_api_router)


@eta_api_router.post("/eta/calculation", response_model=TravelData)
def eta_calculation(input_data: TravelData):
    try:
        # # Taking delays from JSON file
        # with open("./eta_to_notification_develop/zip_code.json") as cap_file:
        #     cap_delays = json.load(cap_file)
        #     logger.info(cap_delays)

        # request_params = TomTomParams.request_params(input_data)
        # logger.info(request_params)

        # initial_response = TomTomParams.tomtom_request(
        #     request_params, input_data)

        # final_response = TomTomParams.calculate_definitive_eta(
        #     initial_response, cap_delays)

        # logger.info(final_response)

        # transforming the json object into a dictionary
        # final_response_dict = final_response.dict()

        logger.info(input_data)

    except Exception as ex:
        logger.error(f"An error occurred during ETA calculation: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))


@app.on_event("shutdown")
def shutdown_db():
    db_disconnect()
