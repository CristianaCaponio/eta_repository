from typing import List
from pydantic import BaseModel


class GeopyInputData(BaseModel):
    
    address: str
    city: str
    postal_code: str