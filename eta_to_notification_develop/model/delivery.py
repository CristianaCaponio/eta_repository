from typing import List
from model.base_model import BaseModel


class Address(BaseModel):
    '''This class defines the parameters for an address. The address will be converted into coordinates 
    by a function hosted preprocess_service and used to populate TravelData object. The fields must be strings (str).'''
    address: str
    city: str
    district: str
    house_number: str
    zip_code: str
    telephone_number: str  # "3933332345678"


class Delivery(BaseModel):
    '''This class contains an instance of the Address class and a gsin'''
    gsin: str
    address: Address
