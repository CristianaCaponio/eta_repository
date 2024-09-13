from typing import List, Optional
from model.geopy_input_data import GeopyInputData
from pydantic import BaseModel


class InputData(BaseModel):
    
    '''model for input data into the API. DepartAt value for real-time departing = now'''
        
    location: Optional[List[GeopyInputData]]
    routeType: str   
    travelMode: str
    departAt: str      
    routeRepresentation: str
    ordered: str
