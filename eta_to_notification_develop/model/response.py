from typing import List, Optional
# from pydantic import BaseModel
from model.base_model import BaseModel
from datetime import datetime

from model.delivery import Delivery


class Delivery_ETA(Delivery):
    eta: datetime
    delivered: Optional[bool] = False
    delivered_at: Optional[datetime] = None


class Response(BaseModel):
    ginc: str
    personal_id: str
    delivery: List[Delivery_ETA]
