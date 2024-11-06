from fastapi import FastAPI, APIRouter
from model.device_message import DeliveryMessage

message_api_router = APIRouter(tags=["Notificaton"])

app = FastAPI()


@message_api_router.post("/notification")
async def update_travel_data(message: DeliveryMessage):

    ginc = DeliveryMessage.ginc
    gsin = DeliveryMessage.gsin
    delivered_at = DeliveryMessage.delivery_time

    # prendere Travel data nel DB
    # aggiornare travel data
    # notificare sms
    # salvare travel data aggiorato
