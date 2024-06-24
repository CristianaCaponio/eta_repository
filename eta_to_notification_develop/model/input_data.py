from datetime import datetime
from typing import List, Tuple
from model.geopy_input_data import GeopyInputData
from pydantic import BaseModel


class InputData(BaseModel):
    
    '''model for input data into the API'''
        
    # version_number: int
    addresses: List[GeopyInputData]
    # coordinate: Tuple[float, float] 
    # departure_date_time: datetime   
    # vehicle_type: str 
    # best_order: bool
    # traffic: bool
    
    
    