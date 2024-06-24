from typing import List
from pydantic import BaseModel


class GeopyInputData(BaseModel):
    ''' this class gives the parameters for the address that will be converted into coordinate by 
    the function hosted in address_converter_service.
    Must be str'''
    address: str
    city: str
    house_number: str