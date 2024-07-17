from fastapi import APIRouter, HTTPException, status
from model.input_data import InputData
from utils.eta_calculation_service import TomTomParams
from model.output_data import TomTomResponse
from loguru import logger

eta_api_router = APIRouter(tags=["Eta-To-Notification"])

@eta_api_router.post("/eta_to_notification_project/eta_calculation", response_model=TomTomResponse)
async def eta_calculation(input_data: InputData):
    try:
        request_params = TomTomParams.request_params(input_data)
        logger.info(request_params)
                
        result = TomTomParams.tomtom_request(request_params)
        
        return result
    
    except Exception as ex:
        logger.error(f"An error occurred during ETA calculation: {ex}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))