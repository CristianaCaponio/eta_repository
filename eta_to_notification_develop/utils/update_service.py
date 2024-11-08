from model.travel_data import TravelData
from model.device_message import DeliveryMessage
from loguru import logger


class RouteUpdate():

    @staticmethod
    def update_route(old_route: TravelData, update: DeliveryMessage) -> TravelData:

        gsin = update.gsin
        delivered_at = update.delivery_time

        for stop in old_route.stops:
            if stop.gsin == gsin:
                if stop.delivered is False:
                    stop.delivered_at = delivered_at
                    stop.delivered = True
                else:
                    logger.info(
                        "not possible to update route file, shipment already delivered")
                    return None

        logger.info(old_route)
        return old_route
