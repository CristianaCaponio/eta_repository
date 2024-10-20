from model.travel_data import TravelData
from datetime import datetime, timedelta
from loguru import logger
import pytz

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
                    logger.info(f"Telefono: {stop.arrivalAddress.telephone_number}. Il tuo pacco è in consegna. Orario previsto: {stop.arrivalTime}")
                    stop.message_sent = True


