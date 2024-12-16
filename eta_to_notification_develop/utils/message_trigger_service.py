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
                    MessageSending.second_delivery_message(stop)

    @staticmethod
    def first_delivery_message(travel_data: TravelData) -> TravelData:
        """
        Sends an SMS to inform the recipient of the estimated delivery time.

        This method formats the arrival time, retrieves the required API token, and uses
        `SmsApiComClient` to send a message to the recipient's phone number.

        Args:
            travel_data (TravelData): Object containing the stops and related information.

        Returns:
            TravelData: The updated object with the sending status for each stop.
        """
        sms_token = os.getenv("SMS_DELIVERING")
        logger.info(f"il token dell'api degli sms è {sms_token}")
        client = SmsApiComClient(access_token=sms_token)

        with open('./eta_to_notification_develop/sms_deliver_problems.json') as deliver_problems:
            problem_codes = json.load(deliver_problems)

        for single_stop in travel_data.stops:

            try:

                single_delivery = single_stop.arrivalAddress
                formatted_datetime = single_stop.arrivalTime.strftime(
                    "%d/%m/%Y %H:%M:%S")

                logger.info(f"messaggio a: {single_delivery.telephone_number}: la consegna è prevista per il giorno  {formatted_datetime}. Un nuovo messaggio sarà inviato quando saremo in prossimità del tuo indirizzo")  # nopep8

                # response = client.sms.send(to = single_delivery.telephone_number, 
                #                            message = f"la consegna è prevista per il giorno  {formatted_datetime}. Un nuovo messaggio sarà inviato quando saremo in prossimità del tuo indirizzo",
                #                            from_ = "Follow-Track")

                # if response.status_code in problem_codes.values():
                #     for message, code in problem_codes.items():
                #             if code == response.status_code:
                #                 single_stop.message_report = f"Problema nell'invio del messaggio di arrivo a:  {single_delivery.telephone_number}: {message} "
                
                #             else:
                #                 single_stop.message_report = f"messaggio di arrivo inviato a: {single_delivery.telephone_number}"
                

            except SendException as e:
                single_stop.message_report = f"An exception during the sms deliver to  {
                    single_stop.arrivalAddress.telephone_number} was found: {e}"

        return travel_data

    @staticmethod
    def second_delivery_message(stop: StopSummary) -> StopSummary:
        """
        Sends an SMS to notify the recipient that the delivery is imminent.

        This method formats the arrival time, retrieves the required API token, and uses
        `SmsApiComClient` to send a message to the recipient's phone number.

        Args:
            stop (StopSummary): Stop data containing the recipient's phone number and estimated time.

        Returns:
            StopSummary: The updated stop object with the sending status.
        """
        sms_token = os.getenv("SMS_DELIVERING")
        logger.info(f"il token dell'api degli sms è {sms_token}")
        client = SmsApiComClient(access_token=sms_token)

        formatted_datetime = stop.arrivalTime.strftime("%d/%m/%Y %H:%M:%S")
        with open('./eta_to_notification_develop/sms_deliver_problems.json') as deliver_problems:
            problem_codes = json.load(deliver_problems)

        try:

            if not stop.message_sent and not stop.delivered:
                logger.info(f"messaggio a: {stop.arrivalAddress.telephone_number}: la tua consegna è prevista nel seguente arco temporale:  {formatted_datetime} e {(stop.arrivalTime + timedelta(hours=1)).strftime('%d/%m/%Y %H:%M:%S')}")  # nopep8
                stop.message_sent = True
                return stop
                # response = client.sms.send(to = stop.arrivalAddress.telephone_number, 
                #                            message = f"la tua consegna è prevista nel seguente arco temporale:  {formatted_datetime} e {(stop.arrivalTime + timedelta(hours=1)).strftime('%d/%m/%Y %H:%M:%S')}",
                #                            from_ = "Follow-Track")

                # if response.status_code in problem_codes.values():
                #     for message, code in problem_codes.items():
                #             if code == response.status_code:
                #                 stop.message_report = f"Problema nell'invio del messaggio di consegna stimata a:  {stop.arrivalAddress.telephone_number}: {message} "
                #                 stop.message_sent = False
                #                 return stop

                #             else:
                #                 stop.message_report = f"messaggio di consegna stimata inviato a: {stop.arrivalAddress.telephone_number}"
                #                 stop.message_sent = True
                #                 return stop

        except SendException as e:
            stop.message_report = f"An exception during the sms deliver to  {
                stop.arrivalAddress.telephone_number} was found: {e}"
            stop.message_sent = False
            return stop

    @staticmethod
    def delivery_occurred_message(stop: StopSummary) -> StopSummary:
        """
        Sends an SMS confirming that the package has been delivered.

        Args:
            stop (StopSummary): Stop data containing the recipient's phone number and delivery confirmation.

        Returns:
            StopSummary: The updated stop object with the sending status.
        """
        sms_token = os.getenv("SMS_DELIVERING")
        client = SmsApiComClient(access_token=sms_token)

        with open('./eta_to_notification_develop/sms_deliver_problems.json') as deliver_problems:
            problem_codes = json.load(deliver_problems)

        try:

            if stop.delivered is True:

                logger.info(f"messaggio a: {stop.arrivalAddress.telephone_number}: il tuo pacco è stato consegnato")  # nopep8
                return stop
                # response = client.sms.send(to = stop.arrivalAddress.telephone_number, 
                #                            message = f"il tuo pacco è stato consegnato",
                #                            from_ = "Follow-Track")

                # if response.status_code in problem_codes.values():
                #     for message, code in problem_codes.items():
                #             if code == response.status_code:
                #                 stop.message_report = f"Problema nell'invio del messaggio di avvenuta consegna a:  {stop.arrivalAddress.telephone_number}: {message} "
                #                 return stop

                #             else:
                #                 stop.message_report = f"messaggio di avvenuta consegna inviato a: {stop.arrivalAddress.telephone_number}"
                #                 return stop
        except SendException as e:
            stop.message_report = f"An exception during the sms deliver to  {
                stop.arrivalAddress.telephone_number} was found: {e}"
            return stop
