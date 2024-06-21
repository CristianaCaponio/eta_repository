from typing import List
from fastapi import APIRouter,HTTPException, status
from loguru import logger
from model.input_data import InputData
from utils.address_converter_service import AddressConverter

eta_api_router = APIRouter(tags=["Eta-To-Notification"])

@eta_api_router.post("/eta_to_notification_project/eta_calculation", response_model=List[tuple])
async def eta_calculation(input_data: List[InputData]):
    try:
        coordinates = AddressConverter.address_to_coordinates_converter(input_data)
        return coordinates
    except Exception as ex:
        logger.error(f"An error occurred during ETA calculation: {ex}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

