from typing import List
from pydantic import BaseModel


class Address(BaseModel):
    ''' this class gives the parameters for the address that will be converted into coordinate by 
    the function hosted in address_converter_service.
    Must be str'''
    address: str
    city: str
    district: str
    house_number: str
    zip_code: str   
    telephone_number: str #"+3933332345678"
   
class Delivery(BaseModel):
    '''This class contains an instance of the Address class and a gsin'''
    gsin: str
    address: Address
