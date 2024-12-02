from model.base_model import BaseModel
from datetime import datetime


class TrackerMessage(BaseModel):
    lat: float
    long: float
    time: datetime
