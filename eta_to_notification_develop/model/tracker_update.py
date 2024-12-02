from model.base_model import BaseModel
from datetime import datetime


class TrackerUpdate(BaseModel):
    lat: float
    long: float
    time: datetime
