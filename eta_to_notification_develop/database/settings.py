# from mongoengine import connect,disconnect
# from loguru import logger


# client = connect(
#     db='followtruck',
#     username='root',
#     password='1234',
#     host='mongodb://host.docker.internal:27017/followtruck',
#     authentication_source='admin'
# )

# logger.info(client)

# def db_connect():
#     logger.info('Sono nel metodo db_connect() di settings.py')    
#     try:
#         db = client.get_database('followtruck')
#         if db is not None:
#             logger.info("Connection Successful!")
            
#             # Recupera la collection
#             collection = db['json_collection_test']
#             logger.info(f"Collection: {collection.name}")
            
#     except Exception as e:
#         logger.error(f"Connection failed: {e}")
        
# def db_disconnect():
#     logger.info('Sono nel metodo db_connect() di settings.py')  
#     try:
#         disconnect()
#         logger.info("Database disconnesso con successo!")
#     except Exception as e:
#         logger.error(f"Errore durante la disconnessione: {e}")


# if __name__ == '__main__':
#     db_connect()    