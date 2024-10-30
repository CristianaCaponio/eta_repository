from model.travel_data import StopSummary, TravelData
from datetime import datetime, timedelta
from smsapi.client import SmsApiComClient
from loguru import logger
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
         
            if stop.message_sent == False:
                arrival_time = stop.arrivalTime
                
                if arrival_time < current_time + timedelta(hours=1):
                    MessageSending.send_message(stop)                    
                    #logger.info(f"Telefono: {stop.arrivalAddress.telephone_number}. Il tuo pacco è in consegna. Orario previsto: {stop.arrivalTime}")#qui va il messaggio
                    stop.message_sent = True



    @staticmethod
    def send_message(stop: StopSummary):
        sms_token = os.getenv("SMS_DELIVERING")
        logger.info(f"il token dell'api degli sms è {sms_token}")        
        client = SmsApiComClient(access_token=sms_token)

        formatted_datetime = stop.arrivalTime.strftime("%d/%m/%Y %H:%M:%S")
        
        logger.info(f"il numero di telefono è {stop.arrivalAddress.telephone_number} e l'orario è {formatted_datetime}")

        #send_results = client.sms.send(to = stop.arrivalAddress.telephone_number, message = f"il tuo pacco arriverà alle ore {stop.arrivalTime}",from_ = "Test")

        # for result in send_results:
        #     logger.info(result.id, result.points, result.error)