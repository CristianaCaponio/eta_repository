


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time
from database.settings import db_connect
from fastapi import FastAPI
from datetime import datetime, timedelta
from model.json_model import JsonCollectionTest
from loguru import logger
import pytz

# Definisci la funzione che vuoi eseguire ogni 3 minuti
def stampa_messaggio():
    print("Questo messaggio viene stampato ogni 3 minuti.")

# Crea un'istanza del scheduler
scheduler = BackgroundScheduler()

# Aggiungi un job per eseguire la funzione ogni 3 minuti
scheduler.add_job(stampa_messaggio, IntervalTrigger(minutes=3))

# Avvia il scheduler
scheduler.start()

# Mantieni il programma in esecuzione
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    # Chiudi il scheduler quando il programma termina
    scheduler.shutdown()

# logger.info("sono dentro il file check_message.api")

# app = FastAPI()

# # Establish connection to MongoDB when app starts and starting scheduler
# @app.on_event("startup")
# def startup():
#     logger.info("sto verificando se connettermi e far partire la schedule")
#     db_connect()
#     start_scheduler()
#     logger.info("mi sono connesso e la schedule è partita")

# # Function to check arrival times
# def check_arrival_time_with_realtime():
#     try:
#         # Retrieve the latest document from MongoDB
#         latest_document = JsonCollectionTest.objects.order_by('-id').first()
        
#         if not latest_document:
#             logger.info("No document found in the database.")
        
#         else:
#             logger.info(f"Latest document retrieved: {latest_document}")

#         # Extract the 'arrivalTime' from the document
#         json_data = latest_document.response_data
#         routes = json_data.get('routes', [])

#         if not routes:
#             logger.error("No routes found in the JSON data.")
#             return
        
#         current_time = datetime.now(pytz.utc)
        
#         for route in routes:
#             # Check for route summary arrival time
#             route_arrival_time_str = route['summary']['arrivalTime']
#             route_arrival_time = datetime.strptime(route_arrival_time_str, "%Y-%m-%dT%H:%M:%S%z")
            
#             # Check if current time is less than 30 minutes before the route's arrival time
#             current_time = datetime.now(route_arrival_time.tzinfo)  # Ensure timezone consistency
#             time_diff = route_arrival_time - current_time
            
#             if timedelta(minutes=0) < time_diff <= timedelta(minutes=30):
#                 logger.info(f"Real-time is less than 30 minutes before route arrival at: {route_arrival_time_str}")

#             # Check for each leg's arrival time
#             for leg in route['legs']:
#                 leg_arrival_time_str = leg['summary']['arrivalTime']
#                 leg_arrival_time = datetime.strptime(leg_arrival_time_str, "%Y-%m-%dT%H:%M:%S%z")
                
#                 # Check if current time is less than 30 minutes before the leg's arrival time
#                 time_diff = leg_arrival_time - current_time
#                 if timedelta(minutes=0) < time_diff <= timedelta(minutes=30):
#                     logger.info(f"Real-time is less than 30 minutes before leg arrival at: {leg_arrival_time_str}")
        
#     except Exception as e:
#         logger.error(f"Error during arrival time check: {e}")

# # Set up the background scheduler
# def start_scheduler():
#     scheduler = BackgroundScheduler(timezone=pytz.utc)
#     scheduler.start()
    
#     # Schedule the function to run every 15 minutes
#     scheduler.add_job(
#         check_arrival_time_with_realtime, 
#         trigger=IntervalTrigger(minutes=2),  
#         id='check_eta_job',
#         name='Check ETA every 2 minutes',
#         replace_existing=True
#     )
#     logger.info("Scheduler job added: check_eta_job.")
    
# # Initialize the scheduler when FastAPI starts


# @app.on_event("shutdown")
# def shutdown_event():
#     logger.info("Shutting down scheduler...")
