from model.base_model import BaseModel
from datetime import datetime


class TrackerMessage(BaseModel):
    ''' this class contains data sent by a tracker'''
    lat: float
    long: float
    time: datetime
