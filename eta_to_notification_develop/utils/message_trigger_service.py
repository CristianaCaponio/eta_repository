from model.travel_data import StopSummary, TravelData
from datetime import datetime, timedelta
from smsapi.client import SmsApiComClient
from smsapi.exception import SendException
from loguru import logger
import json
import pytz
import os

"""This application takes a TravelData object as input and iterates through its stop-arrivals to retrieve phone numbers and arrival times. If the arrival times 
are less than one hour from the current time, a message is printed, and the message_sent attribute changes from false to true."""


class MessageSending:

    @staticmethod
    def check_time_and_send(travel_data: TravelData):
        current_time = datetime.now(pytz.UTC)
        logger.info(f"The actual datetime is {current_time}")

        for stop in travel_data.stops:

            if stop.message_sent is False:
                arrival_time = stop.arrivalTime

                if arrival_time < current_time + timedelta(hours=1):
                    MessageSending.send_message(stop)

                    # logger.info(f"Telefono: {stop.arrivalAddress.telephone_number}. Il tuo pacco è in consegna. Orario previsto: {stop.arrivalTime}")#qui va il messaggio
                    # stop.message_sent = True

    @staticmethod
    def send_message(stop: StopSummary) -> StopSummary:
        sms_token = os.getenv("SMS_DELIVERING")
        logger.info(f"il token dell'api degli sms è {sms_token}")
        client = SmsApiComClient(access_token=sms_token)

        formatted_datetime = stop.arrivalTime.strftime("%d/%m/%Y %H:%M:%S")
        with open('./eta_to_notification_develop/sms_deliver_errors.json') as deliver_errors:
            error_codes = json.load(deliver_errors)

        try:
                
            if not stop.message_sent and not stop.delivered:

                logger.info(f"messaggio a: {stop.arrivalAddress.telephone_number}: il tuo pacco arriverà alle il giorno  {formatted_datetime}")  # nopep8
                return stop
                # response = client.sms.send(to = stop.arrivalAddress.telephone_number, message = f"il tuo pacco arriverà alle ore {formatted_datetime}",from_ = "Follow-Track")

                # if response.status_code in error_codes.values():
                #     for message, code in error_codes.items():
                #             if code == response.status_code:
                #                 stop.message_report = f"Problema nell'invio del messaggio di arrivo a:  {stop.arrivalAddress.telephone_number}: {message} "
                #                 stop.message_sent = False
                #                 return stop

                #             else:
                #                 stop.message_report = f"messaggio di arrivo inviato a: {stop.arrivalAddress.telephone_number}"
                #                 stop.message_sent = True
                #                 return stop
                            
            elif stop.delivered is True:

                logger.info(f"messaggio a: {stop.arrivalAddress.telephone_number}: il tuo pacco è stato consegnato")  # nopep8
                return stop
                # response = client.sms.send(to = stop.arrivalAddress.telephone_number, message = f"il tuo pacco è stato consegnato",from_ = "Follow-Track")

                # if response.status_code in error_codes.values():
                #     for message, code in error_codes.items():
                #             if code == response.status_code:
                #                 stop.message_report = f"Problema nell'invio del messaggio di avvenuta consegna a:  {stop.arrivalAddress.telephone_number}: {message} "
                #                 return stop

                #             else:
                #                 stop.message_report = f"messaggio di avvenuta consegna inviato a: {stop.arrivalAddress.telephone_number}"                                
                #                 return stop

        except SendException as e:
            stop.message_report = f"An exception during the sms deliver to  {stop.arrivalAddress.telephone_number} was found: {e}"
            stop.message_sent = False
            return stop
        
        
