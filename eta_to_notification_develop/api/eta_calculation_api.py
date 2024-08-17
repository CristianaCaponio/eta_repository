from fastapi import APIRouter, HTTPException, status
from model.input_data import InputData
from utils.eta_calculation_service import TomTomParams
from model.tomtom_output_data import TomTomResponse
from loguru import logger
import json

eta_api_router = APIRouter(tags=["Eta-To-Notification"])

@eta_api_router.post("/eta_to_notification_project/eta_calculation", response_model=TomTomResponse)
def eta_calculation(input_data: InputData):
    
    try:
        # Carica i ritardi per CAP dal file JSON
        with open("./eta_to_notification_develop/zip_code.json") as cap_file:
            cap_delays = json.load(cap_file)
            logger.info(cap_delays)

        request_params = TomTomParams.request_params(input_data)
        logger.info(request_params)
                        
        initial_response = TomTomParams.tomtom_request(request_params, input_data)
        #cap_delays = [300, 200, 100]  
        final_response = TomTomParams.calculate_definitive_eta(initial_response, cap_delays)
        
        logger.info(final_response) 
        return final_response
    
    except Exception as ex:
        logger.error(f"An error occurred during ETA calculation: {ex}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))