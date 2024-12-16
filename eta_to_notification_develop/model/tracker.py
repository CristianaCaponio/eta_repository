from model.base_model import BaseModel
from datetime import datetime


class TrackerMessage(BaseModel):
    ''' this class contains data sent by a tracker. It's important to leave "time" as a str since the tracker sends time in string format'''
    lat: float
    long: float
    time: str
