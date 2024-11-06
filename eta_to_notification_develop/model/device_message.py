from pydantic import BaseModel
from datetime import datetime


class DeliveryMessage(BaseModel):
    ginc: str
    gsin: str
    delivery_time: datetime
