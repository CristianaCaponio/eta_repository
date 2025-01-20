from model.travel_data import StopSummary, TravelData
from datetime import datetime, timedelta
from smsapi.client import SmsApiComClient
from smsapi.exception import SendException
from loguru import logger
import json
import pytz
import os


class MessageSending:
    """
    The `MessageSending` class contains methods to handle the sending of SMS messages related to the delivery status of packages.
    It interacts with the SmsApiComClient to send notifications about estimated arrival times and delivery completions.

    Key Responsibilities:
    1. **Notification of estimated delivery**: On the first update, the system sends an SMS with the estimated delivery time.
    2. **Check and notify imminent delivery**: Checks if a stop's arrival time is within 30 minutes and sends an SMS notification with the expected time.
    3. **Notification of completed delivery**: Sends an SMS confirming that the package has been delivered.
    """

    @staticmethod
    def check_time_and_send(travel_data: TravelData):
        """
        Checks if the arrival time of each stop is within 30 minutes of the current time.
        If it is, sends an SMS to notify the recipient of the imminent delivery.

        Args:
            travel_data (TravelData): Object containing data about the trip's stops.
        """
        current_time = datetime.now(pytz.UTC)
        logger.info(f"The actual datetime is {current_time}")

        for stop in travel_data.stops:

            if stop.message_sent is False:
                arrival_time = stop.arrivalTime

                if arrival_time < current_time + timedelta(minutes=30):
                    MessageSending.incoming_delivery_message(stop)


    

    @staticmethod
    def delivery_departure_message(travel_data: TravelData) -> TravelData:
        """
        Sends an SMS to inform the recipient of the estimated delivery time.

        This method formats the arrival time, retrieves the required API token, and uses
        `SmsApiComClient` to send a message to the recipient's phone number.

        Args:
            travel_data (TravelData): Object containing the stops and related information.

        Returns:
            TravelData: The updated object with the sending status for each stop.

        On database:
            The shipping status is saved in the "message_report" field (the list of statuses is contained in the "sms_deliver_statuses.json" file) or any error message
            whose detailed explanation is contained in the "sms_deliver_error_list.json")
        """
        sms_token = os.getenv("SMS_DELIVERING")
        client = SmsApiComClient(access_token=sms_token)

        with open('./eta_to_notification_develop/sms_deliver_statuses.json') as deliver_statuses:
            statuses_codes = json.load(deliver_statuses)

        for single_stop in travel_data.stops:
            try:
                    

                single_delivery = single_stop.arrivalAddress
                formatted_datetime = single_stop.arrivalTime.strftime("%d/%m/%Y %H:%M:%S")
                # logger.info(f"Messaggio inviato a: {single_delivery.telephone_number}. Il corriere è partito. La tua consegna è prevista per il giorno: {formatted_datetime} ")

                response = client.sms.send(
                    to=single_delivery.telephone_number,
                    message=f"Il corriere è partito. La tua consegna è prevista nel seguente arco temporale: {formatted_datetime}",
                    from_=""
                )

                for sms_result in response.results:
                    status = sms_result.status
                    logger.info(f"sms result for {single_delivery.telephone_number}: {status}")

                    if status in {"QUEUE", "SENT", "DELIVERED", "ACCEPTED"}:
                        single_stop.message_report = f"Messaggio di partenza corriere inviato a: {single_delivery.telephone_number}"
                    else:
                        error_message = next(
                            (msg for msg, code in statuses_codes.items() if code == sms_result.code),
                            "Errore sconosciuto"
                        )
                        single_stop.message_report = f"Problema nell'invio del messaggio a {single_delivery.telephone_number}: {error_message}"

            except SendException as e:
                single_stop.message_report = f"Eccezione durante l'invio del messaggio di arrivo a {single_stop.arrivalAddress.telephone_number}: {e}"

        return travel_data

    @staticmethod
    def incoming_delivery_message(stop: StopSummary) -> StopSummary:
        """
        Sends an SMS to notify the recipient that the delivery is imminent.

        This method formats the arrival time, retrieves the required API token, and uses
        `SmsApiComClient` to send a message to the recipient's phone number.

        Args:
            stop (StopSummary): Stop data containing the recipient's phone number and estimated time.

        Returns:
            StopSummary: The updated stop object with the sending status.
        
        On database:
            The shipping status is saved in the "message_report" field (the list of statuses is contained in the "sms_deliver_statuses.json" file) or any error message
            whose detailed explanation is contained in the "sms_deliver_error_list.json")
        """
        sms_token = os.getenv("SMS_DELIVERING")
        client = SmsApiComClient(access_token=sms_token)

        formatted_datetime = stop.arrivalTime.strftime("%d/%m/%Y %H:%M:%S")
        with open('./eta_to_notification_develop/sms_deliver_statuses.json') as deliver_statuses:
            statuses_codes = json.load(deliver_statuses)
        successful_statuses = {"QUEUE", "SENT", "DELIVERED", "ACCEPTED"}

        try:
            # logger.info(f"messaggio inviato a: {stop.arrivalAddress.telephone_number}. La tua consegna è prevista nel seguente arco temporale: {formatted_datetime} e {(stop.arrivalTime + timedelta(hours=1)).strftime('%d/%m/%Y %H:%M:%S')}")
            # return stop
            if not stop.message_sent and not stop.delivered:
                response = client.sms.send(
                    to=stop.arrivalAddress.telephone_number,
                    message=f"La tua consegna è prevista nel seguente arco temporale: {formatted_datetime} e {(stop.arrivalTime + timedelta(hours=1)).strftime('%d/%m/%Y %H:%M:%S')}",
                    from_=""
                )

                for sms_result in response.results:
                    status = sms_result.status
                    logger.info(f"sms result for {stop.arrivalAddress.telephone_number}: {status}")

                    if status in successful_statuses:
                        stop.message_report = f"Messaggio di consegna stimata inviato a: {stop.arrivalAddress.telephone_number}"
                        stop.message_sent = True
                        stop.delivered = True
                    else:
                        error_message = next(
                            (msg for msg, code in statuses_codes.items() if code == sms_result.code),
                            "Errore sconosciuto"
                        )
                        stop.message_report = f"Problema nell'invio del messaggio a {stop.arrivalAddress.telephone_number}: {error_message} (stato: {status})"
                        stop.message_sent = False
                        stop.delivered = False

                return stop

        except SendException as e:
            stop.message_report = f"Eccezione durante l'invio del messaggio a {stop.arrivalAddress.telephone_number}: {e}"
            stop.message_sent = False
            stop.delivered = False
            return stop
                      

    # @staticmethod
    # def delivery_occurred_message(stop: StopSummary) -> StopSummary:
    #     """
    #     Sends an SMS confirming that the package has been delivered.

    #     Args:
    #         stop (StopSummary): Stop data containing the recipient's phone number and delivery confirmation.

    #     Returns:
    #         StopSummary: The updated stop object with the sending status.
    #     On database:
    #         The shipping status is saved in the "message_report" field (the list of statuses is contained in the "sms_deliver_statuses.json" file) or any error message
    #         whose detailed explanation is contained in the "sms_deliver_error_list.json")  
    #     """
    #     sms_token = os.getenv("SMS_DELIVERING")
    #     client = SmsApiComClient(access_token=sms_token)

    #     with open('./eta_to_notification_develop/sms_deliver_statuses.json') as deliver_statuses:
    #         statuses_codes = json.load(deliver_statuses)
    #     successful_statuses = {"QUEUE", "SENT", "DELIVERED", "ACCEPTED"}

    #     try:
    #         response = client.sms.send(
    #             to=stop.arrivalAddress.telephone_number,
    #             message="Il tuo pacco è stato consegnato",
    #             from_=""
    #         )

    #         for sms_result in response.results:
    #             status = sms_result.status
    #             logger.info(f"Stato della risposta per {stop.arrivalAddress.telephone_number}: {status}")

    #             if status in successful_statuses:
    #                 stop.message_report = f"Messaggio di avvenuta consegna inviato a: {stop.arrivalAddress.telephone_number}"
    #                 return stop
    #             else:
    #                 error_message = next(
    #                     (msg for msg, code in statuses_codes.items() if code == sms_result.code),
    #                     "Errore sconosciuto"
    #                 )
    #                 stop.message_report = f"Problema nell'invio del messaggio di avvenuta consegna a: {stop.arrivalAddress.telephone_number}: {error_message}"
    #                 return stop

    #     except SendException as e:
    #         stop.message_report = f"Eccezione durante l'invio del messaggio di avvenuta consegna a {stop.arrivalAddress.telephone_number}: {e}"

    #     return stop
