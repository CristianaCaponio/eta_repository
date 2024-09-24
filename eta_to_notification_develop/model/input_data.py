from typing import List, Optional
from model.delivery import Delivery
from pydantic import BaseModel


class InputData(BaseModel):

    '''model for input data into the API. DepartAt value for real-time departing = now'''

    location: Optional[List[Delivery]]
    routeType: str
    travelMode: str
    departAt: str
    # routeRepresentation: str
    # ordered: str
