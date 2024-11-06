from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from model.delivery import Delivery


class Response(Delivery):
    eta: datetime
    delivered: bool
    delivered_at: Optional[datetime] = None
