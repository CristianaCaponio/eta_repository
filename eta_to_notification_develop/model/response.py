from typing import List, Optional
from model.base_model import BaseModel
from datetime import datetime

from model.delivery import Delivery


class Delivery_ETA(Delivery):
    '''This class extends Delivery and includes estimated arrival time (eta), 
    delivered status, and the time the delivery actually occurred (delivered_at).'''
    eta: datetime
    delivered: Optional[bool] = False
    delivered_at: Optional[datetime] = None


class Response(BaseModel):
    '''This class represents a response that includes delivery-related information for a specific journey. It is used to view the 
    response obtained calling the methods create_upload_file and eta_modification inside eta_calculation_api.py'''
    ginc: str
    personal_id: str
    delivery: List[Delivery_ETA]
