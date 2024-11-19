from model.base_model import BaseModel
from datetime import datetime


class DeliveryMessage(BaseModel):
    '''This class contains information used for marking a delivery as delivered (delivered=True) 
    and triggers both TomTom and message services.'''
    ginc: str
    gsin: str
    delivery_time: datetime
